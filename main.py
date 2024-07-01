from loaders.netbox import Populate_netbox
from error_handling import PersistentError, TransientError, log_setup
from collectors import DeviceFactory
from parsers import Parser
from yaml import safe_load
from argparse import ArgumentParser
from transformers import Transformer
import pynetbox
from pprint import pprint
from os import getenv

def get_arguments():
    """ Getting Command Line Arguments"""
    parser = ArgumentParser(
        description=f"NetBox-AutoSync is designed to seamlessly collect, parse, validate, transform, enrich, and load network data into NetBox.",
        add_help=True
    )
    
    parser.add_argument('--create',action='store_true', help='Run the creation phase')
    parser.add_argument('--update',action='store_true', help='Run the update phase')
    parser.add_argument('--selective-update',action='store_true', help='Run the selective-update phase')
    parser.add_argument('--device-inventory-path', default="config/collector_inventory.yml", help='Path to the device inventory file')
    parser.add_argument('--loader-conf', default="config/autosync_config.yml", help='Path to the loader configuration file')
    args = parser.parse_args()
    if not any(vars(args).values()):
        parser.print_help()
    return args

def read_inventory(inventory_path):
    """Read and returns the devices configuration from a YAML file."""
    with open(inventory_path, "r") as f:
        return safe_load(f)

# made it a function to pass the creds to the get ips function
def read_netbox_creds(config_path):
    """Read and returns netbox creds from a YAML file."""
    with open(config_path, "r") as f:
        return safe_load(f)

# Getting the devices info for update phase
def get_device_info_for_update(loader_config,logger=None):
    nb = pynetbox.api(loader_config['NETBOX_URL'], token=getenv('NETBOX_TOKEN'))
    logger.info(f"Connecting to Netbox instance at {loader_config['NETBOX_URL']}")
    # exclude non-SSH or REST devices 
    os_to_include = ['cisco_ios','cisco_xe','apic']
    # Get all devices
    logger.info("Retrieving device data from Netbox...")
    all_devices = nb.dcim.devices.all()
    logger.info(f"Retrieved devices  data from Netbox...")
    # Filter devices including specified os_types and where primary_ip4 is None
    filtered_devices = [device for device in all_devices if str(device.custom_fields['os_type']) in os_to_include and device.primary_ip4 and device.primary_ip4.address.split('/')[0] != '0.0.0.0']

    data = {}
    for device in filtered_devices:
        site = device.site.name
        region = device.site.region.name
        location = device.location.name
        os_type = str(device.custom_fields['os_type'])
        device_name = device.name
        ip = device.primary_ip4.address.split('/')[0]
    
        if os_type == 'apic':
            os_type = 'aci'
            ip = 'https://' + ip
    # Initialize nested dictionaries only if they don't exist
        if region not in data:
            data[region] = {}
        if site not in data[region]:
            data[region][site] = {}
        if location not in data[region][site]:
            data[region][site][location] = {}
        if os_type not in data[region][site][location]:
            data[region][site][location][os_type] = {}
        if device_name not in data[region][site][location][os_type]:
            data[region][site][location][os_type][device_name] = {}
        
        
 
        if os_type == 'cisco_ios' or os_type== 'cisco_xe':  
    # Assign the device details
            data[region][site][location][os_type][device_name] = {
            'ip': ip,
            'device_role': str(device.device_role),
            'device_tenant': str(device.tenant)  # Assuming device has a 'tenant' attribute
            }
        else:
            # Assign the device details
            data[region][site][location][os_type][device_name] = {
            'ip': ip,
        'device_tenant': str(device.tenant)  # Assuming device has a 'tenant' attribute
            }
    
    return data

def collect_data(devices_inventory, logger=None):
    """Retrieve data from devices using the collectors."""
    collected_data = []
    for region, region_value in devices_inventory.items():
        for site, site_value in region_value.items():
            for location, location_value in site_value.items():
                for device_type, devices_in_type in location_value.items():
                    for device_name, device_value in devices_in_type.items():
                        try:
                            device_value["device_type"] = device_type
                            device_value["device_name"] = device_name
                            device_value["username"] = getenv('USERNAME')
                            device_value["password"] = getenv('PASSWORD')
                            device = DeviceFactory.create_device(**device_value)
                            device.run()

                            # Build the data dictionary
                            if device_type in ['cisco_ios', 'cisco_xe']:
                                data = {
                                    "device_name": device_name,
                                    "device_ip": device_value["ip"],
                                    "device_role": device_value.get("device_role"),
                                    "device_tenant": device_value.get('device_tenant'),
                                    "device_location": location,
                                    "os_type": Transformer.sanitize_slug(device_type),
                                    "nodes": device.data,
                                    "region": region,
                                    "site": site,
                                    
                                }
                            elif device_type == 'PANOS':
                                data = {
                                    "device_name": device_name,
                                    "os_type": Transformer.sanitize_slug(device_type),
                                    "region": region,
                                    "location": location,
                                    "nodes": device.data,
                                }
                                
                            else:
                                data = {
                                    "device_name": device_name,
                                    "device_tenant": device_value.get('device_tenant'),
                                    "device_location": location,
                                    "os_type": Transformer.sanitize_slug(device_type),
                                    "nodes": device.data,
                                    "region": region,
                                    "site": site,
                                    "location": location
                                }
                            collected_data.append(data)

                        except (PersistentError, TransientError, NameError) as e:
                            if logger:
                                logger.error(f"Error collecting data from {device_name}: {str(e)}")
                            continue  # Proceed to next device iteration in case of error

    return collected_data

def parse_data(collected_data,logger=None):
    """Parse collected data using the Parser class."""
    if collected_data:
        parser = Parser(collected_data,logger)
        return parser.parse()
    return []



def load_data(devices_data,loader_conf,action):
    """Populate Netbox with the parsed device data based on action(create,update)"""
    

    loader_format= '%(asctime)s - Populate Netbox \n%(levelname)s - %(message)s\n' + ("=" * 150)
    logger=log_setup(format=loader_format)

    try:
        netbox = Populate_netbox(
            netbox_conf={
                "netbox_url": loader_conf["NETBOX_URL"],
                "netbox_token": getenv("NETBOX_TOKEN"),
            },
            logger=logger,
        )

        netbox.check_connection()
        
        netbox.populate(
            devices_data=devices_data,
            action=action
        )
    except PersistentError:
        pass

if __name__ == '__main__':
    #Get the logger 
    logger = log_setup()
 
    # Get Arguments 
    args = get_arguments()
    

    # read netbox api creds
    loader_conf = read_netbox_creds(args.loader_conf)

    # use .yml as inventory
    if args.create or args.selective_update: 
        devices_inventory = read_inventory(args.device_inventory_path)    

    # use netbox as inventory   
    elif args.update:
        devices_inventory =  get_device_info_for_update(loader_conf,logger)

    # Collect Data from Devices
    #collected_data = collect_data(devices_inventory, logger)   
    collected_data=[
    {
        "device_name": "SE212-BKP-SCP-01",
        "device_ip": "SE212-BKP-SCP-01.noc.intraxa",
        "device_role": "router",
        "device_tenant": "AXA",
        "device_location": "CLICHY",
        "os_type": "cisco_xe",
        "nodes": {
            "show version": "Cisco IOS XE Software, Version 17.07.01\nCisco IOS Software [Cupertino], Catalyst L3 Switch Software (CAT9K_IOSXE), Version 17.7.1, RELEASE SOFTWARE (fc5)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2021 by Cisco Systems, Inc.\nCompiled Sat 04-Dec-21 15:59 by mcpre\n\n\nCisco IOS-XE software, Copyright (c) 2005-2021 by cisco Systems, Inc.\nAll rights reserved.  Certain components of Cisco IOS-XE software are\nlicensed under the GNU General Public License (\"GPL\") Version 2.0.  The\nsoftware code licensed under GPL Version 2.0 is free software that comes\nwith ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such\nGPL code under the terms of GPL Version 2.0.  For more details, see the\ndocumentation or \"License Notice\" file accompanying the IOS-XE software,\nor the applicable URL provided on the flyer accompanying the IOS-XE\nsoftware.\n\n\nROM: IOS-XE ROMMON\nBOOTLDR: System Bootstrap, Version 17.6.1r[FC2], RELEASE SOFTWARE (P)\n\nSE212-BKP-SCP-01 uptime is 1 year, 30 weeks, 6 days, 1 hour, 19 minutes\nUptime for this control processor is 1 year, 30 weeks, 6 days, 1 hour, 22 minutes\nSystem returned to ROM by PowerOn\nSystem restarted at 14:34:56 UTC Fri Nov 25 2022\nSystem image file is \"flash:packages.conf\"\nLast reload reason: PowerOn\n\n\n\nThis product contains cryptographic features and is subject to United\nStates and local country laws governing import, export, transfer and\nuse. Delivery of Cisco cryptographic products does not imply\nthird-party authority to import, export, distribute or use encryption.\nImporters, exporters, distributors and users are responsible for\ncompliance with U.S. and local country laws. By using this product you\nagree to comply with applicable laws and regulations. If you are unable\nto comply with U.S. and local laws, return this product immediately.\n\nA summary of U.S. laws governing Cisco cryptographic products may be found at:\nhttp://www.cisco.com/wwl/export/crypto/tool/stqrg.html\n\nIf you require further assistance please contact us by sending email to\nexport@cisco.com.\n\n\nTechnology Package License Information: \n\n------------------------------------------------------------------------------\nTechnology-package                                     Technology-package\nCurrent                        Type                       Next reboot  \n------------------------------------------------------------------------------\nnetwork-advantage   \tSmart License                 \t network-advantage   \ndna-advantage       \tSubscription Smart License    \t dna-advantage                 \nAIR License Level: AIR DNA Advantage\nNext reload AIR license Level: AIR DNA Advantage\n\n\nSmart Licensing Status: Registration Not Applicable/Not Applicable\n\ncisco C9300-48T (X86) processor with 1319367K/6147K bytes of memory.\nProcessor board ID FOC2624YCC5\n316 Virtual Ethernet interfaces\n104 Gigabit Ethernet interfaces\n16 Ten Gigabit Ethernet interfaces\n4 TwentyFive Gigabit Ethernet interfaces\n4 Forty Gigabit Ethernet interfaces\n2048K bytes of non-volatile configuration memory.\n8388608K bytes of physical memory.\n1638400K bytes of Crash Files at crashinfo:.\n1638400K bytes of Crash Files at crashinfo-1:.\n11264000K bytes of Flash at flash:.\n11264000K bytes of Flash at flash-1:.\n\nBase Ethernet MAC Address          : e8:d3:22:d4:a5:00\nMotherboard Assembly Number        : 73-19915-04\nMotherboard Serial Number          : FOC26232L4W\nModel Revision Number              : H0\nMotherboard Revision Number        : B0\nModel Number                       : C9300-48T\nSystem Serial Number               : FOC2624YCC5\nCLEI Code Number                   : \n\n\nSwitch Ports Model              SW Version        SW Image              Mode   \n------ ----- -----              ----------        ----------            ----   \n     1 65    C9300-48T          17.07.01          CAT9K_IOSXE           INSTALL\n*    2 65    C9300-48T          17.07.01          CAT9K_IOSXE           INSTALL\n\n\nSwitch 01\n---------\nSwitch uptime                      : 1 year, 30 weeks, 6 days, 1 hour, 19 minutes \n\nBase Ethernet MAC Address          : f8:e9:4f:04:96:80\nMotherboard Assembly Number        : 73-19915-04\nMotherboard Serial Number          : FOC26225ZA7\nModel Revision Number              : H0\nMotherboard Revision Number        : B0\nModel Number                       : C9300-48T\nSystem Serial Number               : FOC2624YC9C\nLast reload reason                 : PowerOn\nCLEI Code Number                   : \n",
            "show platform": "Switch  Ports    Model                Serial No.   MAC address     Hw Ver.       Sw Ver. \n------  -----   ---------             -----------  --------------  -------       --------\n 1       65     C9300-48T             FOC2624YC9C  f8e9.4f04.9680  V05           17.07.01      \n 2       65     C9300-48T             FOC2624YCC5  e8d3.22d4.a500  V05           17.07.01      \nSwitch/Stack Mac Address : e8d3.22d4.a500 - Local Mac Address\nMac persistency wait time: Indefinite\n                                   Current\nSwitch#   Role        Priority      State \n-------------------------------------------\n 1       Standby         1          Ready               \n*2       Active          1          Ready               \n\n\n",
        },
        "region": "SEDC",
        "site": "SEDC"
    },
    {
        "device_name": "SE212-PS-RTR-11",
        "device_ip": "SE212-PS-RTR-11.noc.intraxa",
        "device_role": "Router",
        "device_tenant": "AXA",
        "device_location": "CLICHY",
        "os_type": "cisco_xe",
        "nodes": {
            "show version": "Cisco IOS XE Software, Version 16.06.05\nCisco IOS Software [Everest], ASR1000 Software (X86_64_LINUX_IOSD-UNIVERSALK9-M), Version 16.6.5, RELEASE SOFTWARE (fc3)\nTechnical Support: http://www.cisco.com/techsupport\nCopyright (c) 1986-2018 by Cisco Systems, Inc.\nCompiled Mon 10-Dec-18 13:11 by mcpre\n\n\nCisco IOS-XE software, Copyright (c) 2005-2018 by cisco Systems, Inc.\nAll rights reserved.  Certain components of Cisco IOS-XE software are\nlicensed under the GNU General Public License (\"GPL\") Version 2.0.  The\nsoftware code licensed under GPL Version 2.0 is free software that comes\nwith ABSOLUTELY NO WARRANTY.  You can redistribute and/or modify such\nGPL code under the terms of GPL Version 2.0.  For more details, see the\ndocumentation or \"License Notice\" file accompanying the IOS-XE software,\nor the applicable URL provided on the flyer accompanying the IOS-XE\nsoftware.\n\n\nROM: IOS-XE ROMMON\n\nSE212-PS-RTR-11 uptime is 5 years, 13 weeks, 5 days, 15 hours, 41 minutes\nUptime for this control processor is 5 years, 13 weeks, 5 days, 15 hours, 44 minutes\nSystem returned to ROM by reload at 01:08:16 CET Tue Mar 26 2019\nSystem restarted at 01:12:40 CET Tue Mar 26 2019\nSystem image file is \"bootflash:/asr1000rpx86-universalk9.16.06.05.SPA.bin\"\nLast reload reason: Reload Command\n\n\n\nThis product contains cryptographic features and is subject to United\nStates and local country laws governing import, export, transfer and\nuse. Delivery of Cisco cryptographic products does not imply\nthird-party authority to import, export, distribute or use encryption.\nImporters, exporters, distributors and users are responsible for\ncompliance with U.S. and local country laws. By using this product you\nagree to comply with applicable laws and regulations. If you are unable\nto comply with U.S. and local laws, return this product immediately.\n\nA summary of U.S. laws governing Cisco cryptographic products may be found at:\nhttp://www.cisco.com/wwl/export/crypto/tool/stqrg.html\n\nIf you require further assistance please contact us by sending email to\nexport@cisco.com.\n\nLicense Type: RightToUse\nLicense Level: adventerprise\nNext reload license Level: adventerprise\n\ncisco ASR1006-X (RP2) processor (revision RP2) with 4271766K/6147K bytes of memory.\nProcessor board ID FXS2013Q1Z0\n12 Ten Gigabit Ethernet interfaces\n32768K bytes of non-volatile configuration memory.\n8388608K bytes of physical memory.\n1873919K bytes of eUSB flash at bootflash:.\n78085207K bytes of SATA hard disk at harddisk:.\n0K bytes of WebUI ODM Files at webui:.\n\nConfiguration register is 0x2102\n",
            "show platform": "Chassis type: ASR1006-X           \n\nSlot      Type                State                 Insert time (ago) \n--------- ------------------- --------------------- ----------------- \n0         ASR1000-6TGE        ok                    5y13w         \n 0/0      BUILT-IN-6TGE       ok                    5y13w         \n1         ASR1000-6TGE        ok                    5y13w         \n 1/0      BUILT-IN-6TGE       ok                    5y13w         \nR0        ASR1000-RP2         ok, active            5y13w         \nR1        ASR1000-RP2         ok, standby           5y13w         \nF0        ASR1000-ESP100      ok, active            5y13w         \nF1        ASR1000-ESP100      ok, standby           5y13w         \nP0        ASR1000X-AC-1100W   ok                    5y13w         \nP1        ASR1000X-AC-1100W   ok                    5y13w         \nP2        Unknown             N/A                   never         \nP3        Unknown             N/A                   never         \nP4        Unknown             N/A                   never         \nP5        Unknown             N/A                   never         \nP6        ASR1000X-FAN        ok                    5y13w         \nP7        ASR1000X-FAN        ok                    21w1d         \n\nSlot      CPLD Version        Firmware Version                        \n--------- ------------------- --------------------------------------- \n0         14011701            16.2(1r)                            \n1         14011701            16.2(1r)                            \nR0        14111801            16.2(1r)                            \nR1        14111801            16.2(1r)                            \nF0        12071700            16.2(1r),                            \nF1        12071700            16.2(1r)                            \n",
        },
        "region": "SEDC",
        "site": "SEDC"
    }
]
    # Parse Collected Data
    parsed_data = parse_data(collected_data, logger)
    pprint(parsed_data)
    # Load the parsed_data to Netbox 
    #load_data(devices_data=parsed_data,loader_conf=loader_conf,action=next((k for k, v in args.__dict__.items() if v), None)) 
