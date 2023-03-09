from cloudSF import FMCAPIHandler
import json
import re
import sys
import getopt
import getpass
from termcolor import colored
import warnings
warnings.filterwarnings('ignore', category=UserWarning, module='openpyxl')

file_FTDv_json="FTDv.json"
file_Interfaces_json="Interfaces.json"
file_SecurityZone_json="SecurityZones.json"
file_ACP_json="ACP.json"
file_ACE_json="ACE_"
file_NAT_json="NAT.json"
file_NAT_Rule_json="NAT_Entries.json"
file_NetHostObject_json= "NetHostObject.json"
file_ProtocolPortObject_json= "ProtocolPortObject.json"
file_NetworkGroups_json= "NetworkGroups.json"
file_PortObjectGroups_json= "PortObjectGroups.json"
file_PolicyAssignment="PolicyAssignment.json"


def print_colored(msg1, col1, text1, no1, no2=None, no3=None):
    if no3==None:
        if no2==None:
            print(colored(str(no1), 'yellow'), colored(msg1, col1), colored(text1, 'white'))
        else:
            print(colored(str(no1), 'yellow'), colored(str(no2), 'yellow'), colored(msg1, col1), colored(text1, 'white'))
    else:
        print(colored(str(no1), 'yellow'), colored(str(no2), 'yellow'), colored(str(no3), 'yellow'), colored(msg1, col1), colored(text1, 'white'))

print_colored("START: ","blue", "Script will poll the configuration from FMC and save it to JSON files ", 1)

fmc_ip=input('Please enter FMC IP address:')
username = input('Username:')
password = getpass.getpass('Password:')

fmc = FMCAPIHandler(fmc_ip, username, password)


ftd=fmc.devices.devicerecords.get()  
if ftd["code"] < 300:
    with open(file_FTDv_json, 'w') as outfile:
        json.dump(ftd["text"], outfile, indent = 4)

    print_colored('PASS: ', 'green', 'Saved Devices to the file: '+file_FTDv_json, 2)
else:
    print_colored('ERROR: ', 'red', str(ftd["text"]), 2)

if len(ftd["text"]) < 0:
    interfaces=fmc.devices.devicerecords.physicalinterfaces.get(ftd["text"][0]["id"])
    if interfaces["code"] < 300:
        with open(file_Interfaces_json, 'w') as outfile:
            json.dump(interfaces["text"], outfile, indent = 4)

        print_colored('PASS: ', 'green', 'Saved Interfaces to the file: '+file_Interfaces_json, 3)
    else:
        print_colored('ERROR: ', 'red', str(interfaces["text"]), 3)


SecurityZone_json=fmc.object.securityzones.get()
if SecurityZone_json["code"] < 300:
    with open(file_SecurityZone_json, 'w') as outfile:
        json.dump(SecurityZone_json["text"], outfile, indent = 4)

    print_colored('PASS: ', 'green', 'Saved SecurityZone to the file: '+file_SecurityZone_json, 4)    
else:
    print_colored('ERROR: ', 'red', str(SecurityZone_json["text"]), 4)


#there is a bug in FMC!!!! cannot poll via api extended
ACP_json=fmc.policy.accesspolicies.get()
if ACP_json["code"] < 300:
    with open(file_ACP_json, 'w') as outfile:
        json.dump(ACP_json["text"], outfile, indent = 4)

    print_colored('PASS: ', 'green', "Saved ACP to the file: "+file_ACP_json, 5)
else:
    print_colored('ERROR: ', 'red', str(ACP_json["text"]), 5)
 

no=1

for each in ACP_json["text"]:
    if not isinstance(each, str):
        if  "id" in each.keys():
            ACE_json=fmc.policy.accesspolicies.accessrules.get(each["id"])
            if ACE_json["code"] < 300:
                with open(file_ACE_json+each["name"]+".json", 'w') as outfile:
                    json.dump(ACE_json["text"], outfile, indent = 4)
            
                print_colored('PASS: ', 'green', "Saved ACE "+str(len(ACE_json["text"]))+"to the file: "+file_ACE_json+each["name"]+".json", 6, no)
            else:
                print_colored('ERROR: ', 'red', str(ACE_json["text"]), 6)
        no=no+1
#    else:
#        with open("ACE_CloudAccessPolicy.json", 'w') as outfile:
#            json.dump([{ 'type': 'AccessPolicy', 'name': 'CloudAccessPolicy', 'defaultAction': { 'action': 'NETWORK_DISCOVERY'}}], outfile, indent = 4)


NetHostObject_host=fmc.object.hosts.get()
NetHostObject_net=fmc.object.networks.get()
NetHostObject_json=NetHostObject_host["text"]+NetHostObject_net["text"]
if NetHostObject_host["code"] < 300 and NetHostObject_net["code"] < 300 :

    with open(file_NetHostObject_json, 'w') as outfile:
        json.dump(NetHostObject_json, outfile, indent = 4)

    print_colored('PASS: ', 'green', "Saved Network "+str(len(NetHostObject_net["text"]))+"/Host "+str(len(NetHostObject_host["text"]))+" Object to the file: "+file_NetHostObject_json, 7)
else:
    print_colored('ERROR: ', 'red', str(NetHostObject_host["text"])+str(NetHostObject_net["text"]), 7)


ProtocolPortObject_json=fmc.object.protocolportobjects.get()
if ProtocolPortObject_json["code"] < 300:
    with open(file_ProtocolPortObject_json, 'w') as outfile:
        json.dump(ProtocolPortObject_json["text"], outfile, indent = 4)

    print_colored('PASS: ', 'green', "Saved Protocol/Port "+str(len(ProtocolPortObject_json["text"]))+" Object to the file: "+file_ProtocolPortObject_json, 8)
else:
    print_colored('ERROR: ', 'red', str(ProtocolPortObject_json["text"]), 8)


NetworkGroups_json=fmc.object.networkgroups.get()
if NetworkGroups_json["code"] < 300:
    with open(file_NetworkGroups_json, 'w') as outfile:
        json.dump(NetworkGroups_json["text"], outfile, indent = 4)

    print_colored('PASS: ', 'green', "Saved Network Groups "+str(len(NetworkGroups_json["text"]))+" Object to the file: "+file_NetworkGroups_json, 9)
else:
    print_colored('ERROR: ', 'red', str(NetworkGroups_json["text"]), 9)


PortObjectGroups_json=fmc.object.portobjectgroups.get()
if PortObjectGroups_json["code"] < 300:
    with open(file_PortObjectGroups_json, 'w') as outfile:
        json.dump(PortObjectGroups_json["text"], outfile, indent = 4)

    print_colored('PASS: ', 'green', "Saved Protocol/Port "+str(len(PortObjectGroups_json["text"]))+" Object to the file: "+file_PortObjectGroups_json, 10)
else:
    print_colored('ERROR: ', 'red', str(PortObjectGroups_json["text"]), 10)


nat_json=adding_nat=fmc.policy.ftdnatpolicies.get()
if nat_json["code"] < 300:
    with open(file_NAT_json, 'w') as outfile:
        json.dump(nat_json['text'], outfile, indent = 4)

    print_colored('PASS: ', 'green', "Saved NAT Object to the file: "+file_NAT_json, 11)
else:
    print_colored('ERROR: ', 'red', str(nat_json["text"]), 11)

if len(nat_json["text"]) > 0:
    natR_json=fmc.policy.ftdnatpolicies.manualnatrules.get(nat_json["text"][0]["id"])
    if natR_json["code"] < 300:
        with open(file_NAT_Rule_json, 'w') as outfile:
            json.dump(natR_json['text'], outfile, indent = 4)

        print_colored('PASS: ', 'green', "Saved NAT Rules Object to the file: "+file_NAT_Rule_json, 12)
    else:
        print_colored('ERROR: ', 'red', str(natR_json["text"]), 12)
else:
    with open(file_NAT_Rule_json, 'w') as outfile:
        json.dump([], outfile, indent = 4)

policyAssign_json=fmc.assignment.policyassignments.get()
if policyAssign_json["code"] < 300:
    with open(file_PolicyAssignment, 'w') as outfile:
        json.dump(policyAssign_json['text'], outfile, indent = 4)

    print_colored('PASS: ', 'green', "Saved file_Policy Assignement to the file: "+file_PolicyAssignment, 13)
else:
    print_colored('ERROR: ', 'red', str(policyAssign_json["text"]), 13)


print_colored("FINISHED! ", "blue", "Script completed successfully!", 14)