from cloudSF import FMCAPIHandler
import json
import sys
import getopt
import getpass
import os.path
import time
from termcolor import colored
#grey, red, green, yellow, blue, magenta, cyan, white


file_blank_excel="cloudSF_blank.xlsx"
file_excel="test_new.xlsx"

file_vFTD_json="FTDv.json"
file_ACP_json="ACP.json"
file_ACE_json="ACE_CloudAccessPolicy.json"
file_NAT_json="NAT.json"
file_NAT_Rule_json="NAT_Entries.json"
file_Interfaces_json="Interfaces.json"
file_SecurityZone_json="SecurityZones.json"
file_NetHostObj_json="NetHostObject.json"
file_ProtocolPortObject_json="ProtocolPortObject.json"
file_NetworkGroups_json= "NetworkGroups.json"
file_PortObjectGroups_json= "PortObjectGroups.json"
file_PolicyAssignment_json="PolicyAssignment.json"

file_deployment_json="Deployment.json"


fmc=None
ftd=None
interfaces=None
nat=None
natRules=None
SecurityZone=None
NetHostObj=None
NetworkGroups=None
ProtocolPortObject=None
PortObjectGroups=None
PolicyAssignment=None
Deployment=None

def print_colored(msg1, col1, text1, no1, no2=None, no3=None):
    if no3==None:
        if no2==None:
            print(colored(str(no1), 'yellow'), colored(msg1, col1), colored(text1, 'white'))
        else:
            print(colored(str(no1), 'yellow'), colored(str(no2), 'yellow'), colored(msg1, col1), colored(text1, 'white'))
    else:
        print(colored(str(no1), 'yellow'), colored(str(no2), 'yellow'), colored(str(no3), 'yellow'), colored(msg1, col1), colored(text1, 'white'))

#### helper function where key name of he interface consist id of the interface
def int_name2id(name):
    global interfaces
    for each in interfaces:
        if each["name"] == name:
            return each["id"]
    return None
    
#### helper function where key name of he interface consist id of the interface
def net_name2id(name):
    global NetHostObj
    for each in NetHostObj:
        if each["name"] == name:
            return each["id"]
    for each in NetHostObj:
        if each["name"] == name:
            return each["id"]           
    return None

def port_name2id(name):
    global ProtocolPortObject
    for each in ProtocolPortObject:
        if each["name"] == name:
            return each["id"]
    return None   

def SZ_name2id(name):
    global SecurityZone
    for each in SecurityZone:
        if each["name"] == name:
            return each["id"]
    return None   



    
#### helper function to update interfaces object
def update_int_id(name, id):
    global interfaces
    each_hlp=[]
    for each in interfaces:
        if each["name"] == name:
            each["id"]=id
        each_hlp.append(each)
    interfaces=each_hlp
    
    
def update_ace_id(name, id):
    global ace
    each_hlp=[]
    for each in ace:
        if each["name"] == name:
            each["id"]=id
        each_hlp.append(each)
    ace=each_hlp
#### helper function to update add_NetHostObj object
def add_NetHostObj(obj):
    global NetHostObj
    global fmc
            
    if obj["type"] == "Host":
        updated_Obj=fmc.object.hosts.post(obj)
        if updated_Obj["code"] < 300:
            if isinstance(updated_Obj["text"], list):
                updated_Obj["text"]=updated_Obj["text"][0]
            noo=0
            for each in NetHostObj:
                if each["name"] == obj["name"]:
                    NetHostObj[noo]["id"] = updated_Obj["text"]["id"]
                noo=noo+1

            #save to file
            with open(file_NetHostObj_json, 'w') as outfile:
                json.dump(NetHostObj, outfile, indent = 4)  
            
            return updated_Obj
        else:
            return updated_Obj
            
    if obj["type"] == "Network":
        updated_Obj=fmc.object.networks.post(obj)
        if updated_Obj["code"] < 300:
            if isinstance(updated_Obj["text"], list):
                updated_Obj["text"]=updated_Obj["text"][0]           
            noo=0
            for each in NetHostObj:
                if each["name"] == obj["name"]:
                    NetHostObj[noo]["id"] = updated_Obj["text"]["id"]
                noo=noo+1

            #save to file
            with open(file_NetHostObj_json, 'w') as outfile:
                json.dump(NetHostObj, outfile, indent = 4)  
            
            return updated_Obj
        else:
            return updated_Obj

    return {"code" : 666, "text" : "Object type not Host nor Networks" }

##########

def add_ProtocolPortObject(obj):
    global ProtocolPortObject
    global fmc
            

    updated_Obj=fmc.object.protocolportobjects.post(obj)
    if updated_Obj["code"] < 300:
        if isinstance(updated_Obj["text"], list):
            updated_Obj["text"]=updated_Obj["text"][0]
        noo=0
        for each in ProtocolPortObject:
            if each["name"] == obj["name"]:
                ProtocolPortObject[noo]["id"] = updated_Obj["text"]["id"]
            noo=noo+1

        #save to file
        with open(file_ProtocolPortObject_json, 'w') as outfile:
            json.dump(ProtocolPortObject, outfile, indent = 4)  
        
        return updated_Obj
    else:
        return updated_Obj    

#### Update PolicyAssignment JSON file
def update_PolicyAssignment():
    global ftd
    global acp
    global nat
    global PolicyAssignment
    
    hlp_PolicyAssignment=[]
    
    for each in PolicyAssignment:
        if each["name"] == acp["name"]:
            each["id"]=acp["id"]
            each["targets"]=[{"type": ftd["type"], "name": ftd["name"], "id": ftd["id"]}]
            each["policy"]={"type": acp["type"], "name": acp["name"], "id": acp["id"]}
        if each["name"] == nat["name"]:
            each["id"]=nat["id"]
            each["targets"]=[{"type": ftd["type"], "name": ftd["name"], "id": ftd["id"]}]
            each["policy"]={"type": nat["type"], "name": nat["name"], "id": nat["id"]}
        hlp_PolicyAssignment.append(each)
            
    with open(file_PolicyAssignment_json, 'w') as outfile:
        json.dump(hlp_PolicyAssignment, outfile, indent = 4)  


#####  CheckACEID if has all ID:
def CheckACEID():
    global ace
    id_exists=True

    for each in ace:

        for sourceZones_obj in each["sourceZones"]["objects"]:
            if "id" not in sourceZones_obj.keys():
                id_exists=False
        
        for destinationZones_obj in each["destinationZones"]["objects"]:
            if "id" not in destinationZones_obj.keys():
                id_exists=False
            
        for sourceNetworks_obj in each["sourceNetworks"]["objects"]:            
            if "id" not in sourceNetworks_obj.keys():
                id_exists=False

        for destinationNetworks_obj in each["destinationNetworks"]["objects"]:             
            if "id" not in destinationNetworks_obj.keys():
                id_exists=False

        for destinationPorts_obj in each["destinationPorts"]["objects"]: 
            if "id" not in destinationPorts_obj.keys():
                id_exists=False
    
    return id_exists

#check if NAT rule has all ids
def CheckNatRID():
    global natRules
    id_exists=True

    for each in natRules:

        if "id" not in each["sourceInterface"].keys():
            id_exists=False
        
        if "id" not in each["destinationInterface"].keys():
            id_exists=False
            
        if "id" not in each["originalSource"].keys():
            id_exists=False

        if "id" not in each["translatedDestination"].keys():
            id_exists=False

        if "id" not in each["originalDestinationPort"].keys():
            id_exists=False

        if "id" not in each["translatedDestinationPort"].keys():
            id_exists=False

    return id_exists

def CheckNetGrpsID():
    row=0
    row_obj=0
    NetGrps_hlp=[]
    for each in NetworkGroups:
        if "objects" in each.keys():
            for NetGrps_obj in each["objects"]:
                if "id" not in NetGrps_obj.keys():
                    NetworkGroups[row]["objects"][row_obj]["id"]=net_name2id(NetGrps_obj["name"])
                    #print("Updated ID for Net/Host Object name: "+NetworkGroups[row]["objects"][row_obj]["name"])
                row_obj=row_obj+1
        row=row+1  
        row_obj=0        
        

    with open(file_NetworkGroups_json, 'w') as outfile:
        json.dump(NetworkGroups, outfile, indent = 4)
    return True

## Port/Protocol Group
def CheckPortProtoGrpID():
    row=0
    row_obj=0
    PortProtoGrp_hlp=[]
    for each in PortObjectGroups:
        if "objects" in each.keys():
            for PortProtoGrp_obj in each["objects"]:
                if "id" not in PortProtoGrp_obj.keys():
                    PortObjectGroups[row]["objects"][row_obj]["id"]=port_name2id(PortProtoGrp_obj["name"])
                    #print("Updated ID for Net/Host Object name: "+NetworkGroups[row]["objects"][row_obj]["name"])
                row_obj=row_obj+1
        row=row+1  
        row_obj=0        

    with open(file_PortObjectGroups_json, 'w') as outfile:
        json.dump(PortObjectGroups, outfile, indent = 4)
    return True
##### Update ACE ID
def UpdateACEID():
    global NetHostObj        
    global SecurityZone    
    global ProtocolPortObject
    global ace
    
    no=0
    for each in ace:
        no_sourceZones=0
        no_destinationZones=0
        no_sourceNetworks=0
        no_destinationNetworks=0
        no_destinationPorts=0
            

        for sourceZones_obj in each["sourceZones"]["objects"]:
            if "id" not in sourceZones_obj.keys():
                ace[no]["sourceZones"]["objects"][no_sourceZones]["id"]=SZ_name2id(ace[no]["sourceZones"]["objects"][no_sourceZones]["name"])
            no_sourceZones=no_sourceZones+1
        
        for destinationZones_obj in each["destinationZones"]["objects"]:
            if "id" not in destinationZones_obj.keys():
                ace[no]["destinationZones"]["objects"][no_destinationZones]["id"]=SZ_name2id(ace[no]["destinationZones"]["objects"][no_destinationZones]["name"])        
            no_destinationZones=no_destinationZones+1
            
        for sourceNetworks_obj in each["sourceNetworks"]["objects"]:            
            if "id" not in sourceNetworks_obj.keys():
                ace[no]["sourceNetworks"]["objects"][no_sourceNetworks]["id"]=net_name2id(ace[no]["sourceNetworks"]["objects"][no_sourceNetworks]["name"]) 
            no_sourceNetworks=no_sourceNetworks+1

        for destinationNetworks_obj in each["destinationNetworks"]["objects"]:             
            if "id" not in destinationNetworks_obj.keys():
                ace[no]["destinationNetworks"]["objects"][no_destinationNetworks]["id"]=net_name2id(ace[no]["destinationNetworks"]["objects"][no_destinationNetworks]["name"]) 
            no_destinationNetworks=no_destinationNetworks+1

        for destinationPorts_obj in each["destinationPorts"]["objects"]: 
            if "id" not in destinationPorts_obj.keys():
                ace[no]["destinationPorts"]["objects"][no_destinationPorts]["id"]=port_name2id(ace[no]["destinationPorts"]["objects"][no_destinationPorts]["name"])  
            no_destinationPorts=no_destinationPorts+1

        no=no+1        
  
    with open(file_NAT_Rule_json, 'w') as outfile:
        json.dump(ace, outfile, indent = 4)   
    print_colored('PASS', 'green', "Updated ACE with object id...", 9, 2)  


##### Update NatR ID
def UpdateNatRID():
    global NetHostObj        
    global SecurityZone    
    global ProtocolPortObject
    global natRules
    
    no=0
    for each in natRules:
        no_sourceZones=0
        no_destinationZones=0
        no_sourceNetworks=0
        no_destinationNetworks=0
        no_destinationPorts=0
        no=0
        if "id" not in each["sourceInterface"].keys():
            natRules[no]["sourceInterface"]["id"]=SZ_name2id(natRules[no]["sourceInterface"]["name"])
        if "id" not in each["destinationInterface"].keys():
            natRules[no]["destinationInterface"]["id"]=SZ_name2id(natRules[no]["destinationInterface"]["name"])
        if "id" not in each["originalSource"].keys():
            natRules[no]["originalSource"]["id"]=net_name2id(natRules[no]["originalSource"]["name"])
        if "id" not in each["translatedDestination"].keys():
            natRules[no]["translatedDestination"]["id"]=net_name2id(natRules[no]["translatedDestination"]["name"])
        if "id" not in each["originalDestinationPort"].keys():
            natRules[no]["originalDestinationPort"]["id"]=port_name2id(natRules[no]["originalDestinationPort"]["name"])
        if "id" not in each["translatedDestinationPort"].keys():  
            natRules[no]["translatedDestinationPort"]["id"]=port_name2id(natRules[no]["translatedDestinationPort"]["name"])          
        no=no+1        
  
    with open(file_NAT_Rule_json, 'w') as outfile:
        json.dump(natRules, outfile, indent = 4)   
    print_colored('PASS', 'green', "Updated Nat Rule with object id...", 11, 2)  

#########################################################################################################
####################   JSON to FMC part of the code
#########################################################################################################


class JSON_2_FMC:
    def __init__(self, ip, username, password):
        global fmc
        fmc = FMCAPIHandler(ip, username, password)
        #self.ftd = None
        
    def __del__(self):
        self.__close()

    def __close(self):
        if 'fmc' in locals():
            del fmc 
######## helper step 0
    def step_0(self):
        global fmc    
        return fmc.job.taskstatuses.get("c7b0ba32-94c1-11ed-aa93-5b55b7c2c9aa")

########    step 1:
########    Can connect to FMC?

    def step_1_J2F(self):
        global fmc    
        if fmc.domain.get() != None:
            return {"response": True, "text" : fmc.domain.get()} 
        else:
            return {"response": False} 
            
            
            
########    step 2:
########    JSON file exists?
           
    def step_2_J2F(self):
    
        if os.path.exists(file_vFTD_json):
            with open(file_vFTD_json) as json_file:
                global ftd
                ftd=json.load(json_file)
                if isinstance(ftd, list):
                    ftd=ftd[0]
        else:
            return {"response": False, "text" : file_vFTD_json}                

        if os.path.exists(file_ACP_json):
            with open(file_ACP_json) as json_file:
                global acp
                acp=json.load(json_file)  
                if isinstance(acp, list):
                    acp=acp[0]
        else:
            return {"response": False, "text" : file_ACP_json}                

        if os.path.exists(file_NAT_json):
            with open(file_NAT_json) as json_file:
                global nat
                nat=json.load(json_file) 
                if isinstance(nat, list):
                    nat=nat[0]
        else:
            return {"response": False, "text" : file_NAT_json}

        if os.path.exists(file_NAT_Rule_json):
            with open(file_NAT_Rule_json) as json_file:
                global natRules
                natRules=json.load(json_file) 
        else:
            return {"response": False, "text" : file_NAT_json}
 
        if os.path.exists(file_Interfaces_json):
            with open(file_Interfaces_json) as json_file:
                global interfaces
                interfaces=json.load(json_file) 
        else:
            return {"response": False, "text" : file_Interfaces_json}

        if os.path.exists(file_SecurityZone_json):
            with open(file_SecurityZone_json) as json_file:
                global SecurityZone
                SecurityZone=json.load(json_file) 
        else:
            return {"response": False, "text" : file_SecurityZone_json}

        if os.path.exists(file_NetHostObj_json):
            with open(file_NetHostObj_json) as json_file:
                global NetHostObj
                NetHostObj=json.load(json_file) 
        else:
            return {"response": False, "text" : file_NetHostObj_json}

        if os.path.exists(file_NetworkGroups_json):
            with open(file_NetworkGroups_json) as json_file:
                global NetworkGroups
                NetworkGroups=json.load(json_file) 
        else:
            return {"response": False, "text" : file_NetworkGroups_json}

        if os.path.exists(file_ACE_json):
            with open(file_ACE_json) as json_file:
                global ace
                ace=json.load(json_file)  
        else:
            return {"response": False, "text" : file_ACE_json}    

        if os.path.exists(file_ProtocolPortObject_json):
            with open(file_ProtocolPortObject_json) as json_file:
                global ProtocolPortObject
                ProtocolPortObject=json.load(json_file)  
        else:
            return {"response": False, "text" : file_ProtocolPortObject_json} 

        if os.path.exists(file_PortObjectGroups_json):
            with open(file_PortObjectGroups_json) as json_file:
                global PortObjectGroups
                PortObjectGroups=json.load(json_file)  
        else:
            return {"response": False, "text" : file_PortObjectGroups_json}

        if os.path.exists(file_PolicyAssignment_json):
            with open(file_PolicyAssignment_json) as json_file:
                global PolicyAssignment
                PolicyAssignment=json.load(json_file)  
        else:
            return {"response": False, "text" : file_PolicyAssignment_json} 

        if os.path.exists(file_deployment_json):
            with open(file_deployment_json) as json_file:
                global Deployment
                Deployment=json.load(json_file)  
        else:
            return {"response": False, "text" : file_deployment_json} 

 
        return {"response": True}        
        
########    step 3:
########    ACP checks?
           
    def step_3_J2F(self, no):
        global fmc    
        global acp
        if "id" in acp.keys():
            return {"response" : True, "text" : acp["id"]}              
        else:
            print_colored('ON HOLD', 'cyan', "No ACP id found, adding ACP: ", no, 1)
            adding_acp=fmc.policy.accesspolicies.post(acp)
            if adding_acp["code"] < 300:
                acp["id"]=adding_acp["text"]["id"]
                print_colored('PASS', 'green', "Successfully  added ACP with id: "+acp["id"], no, 2)
                with open(file_ACP_json, 'w') as outfile:
                    json.dump(acp, outfile, indent = 4) 
                ftd["accessPolicy"]["id"]=acp["id"]    
                with open(file_vFTD_json, 'w') as outfile:
                    json.dump(ftd, outfile, indent = 4)                     
                    
                return {"response" : True, "text" : acp["id"]}
            else:
                return {"response" : False, "text" : adding_acp["text"]}

            
        return {"response" : True, "text" : acp["id"]}     
        
########    step 4:
########    FTD checks?
           
    def step_4_J2F(self, no):
        global ftd
        if "id" in ftd.keys():
            return {"response" : True, "text" : ftd["id"]}              
        else:
            print_colored('ON HOLD', 'cyan', "No FTD id found, adding FTD: "+ftd["name"], no, 1)
            adding_ftd=fmc.devices.devicerecords.post(ftd)
            if adding_ftd["code"] < 300:
                task_id=adding_ftd["text"]["metadata"]["task"]["id"]
                print_colored('ON HOLD', 'cyan', "Successfully sent the request to add FTD with task id: "+task_id, no, 2)
                nooo=1
                repeats=10
                while repeats != 0:
                    adding_ftd=fmc.job.taskstatuses.get(task_id)
                    
                    if adding_ftd["code"] < 300:
                        print_colored('ON HOLD', 'cyan', "Status: "+adding_ftd["text"]["status"]+" waiting for 30 sec, no of retries: "+str(repeats), no, 3, nooo)
                        nooo=nooo+1
                        repeats=repeats-1
                        time.sleep(30)
                    else:
                        print_colored('ON HOLD', 'cyan', "Initialization completed, checking the FTD status...", no, 3)
                        break
            
            adding_ftd=fmc.devices.devicerecords.get()          
            if adding_ftd["code"] < 300:
                print_colored('ON HOLD', 'cyan', "Searching for FTDs...", no, 4)
                if isinstance(adding_ftd["text"], list):
                    adding_ftd["text"]=adding_ftd["text"][0]
                if "id" in adding_ftd["text"]:
                        print_colored('ON HOLD', 'cyan', "Found FTD: "+adding_ftd["text"]["id"]+" ...checking details", no, 5)
                        nooo=1
                        repeats=10
                        while repeats != 0:
                            ftd_details=fmc.devices.devicerecords.get(adding_ftd["text"]["id"])
                            if ftd_details["code"] < 300:
                                ftd["id"]=ftd_details["text"]["id"]
                                with open(file_vFTD_json, 'w') as outfile:
                                    json.dump(ftd, outfile, indent = 4)                  
                                print_colored('ON HOLD', 'cyan', "Registration completed for FTD name: "+ftd_details["text"]["name"]+" and S/N "+ftd_details["text"]["metadata"]["deviceSerialNumber"], no, 6)        
                                return {"response" : True, "text" : ftd["id"]}
                            else:
                                print_colored('ON HOLD', 'cyan', "FTD not registered yet, waiting for 30 sec, no of retries: "+ str(repeats), no, 6, nooo)
                                repeats=repeats-1
                                nooo=nooo+1
                                time.sleep(30)                                
                else:
                    return {"response" : False, "text" : "Cannot find FTD on the list newly added devices. Most likely FTD not fully enrolled yet or wrong IP/regKey of FTD used."}      
            else:
                return {"response" : False, "text" : "Error while polling the list of newly added devices."+str(adding_ftd["text"])}

########    step 5:
########    Initial deployment checks?
    def step_5_J2F(self, no):
        nooo=1
        jobH=fmc.devices.jobhistories.get()   
        if jobH["code"] < 300:
            repeats=10
            while repeats != 0:
                if isinstance(jobH["text"], list):
                    if "deploymentNote" is in jobH["text"][len(jobH["text"])-1].keys():
                        if jobH["text"][len(jobH["text"])-1]["deploymentNote"] == "Deployment after registration":
                            #print_colored('ON HOLD', 'cyan', "Initial deployment completed.", no, 1)
                            repeats=0
                            return {"response" : True, "text" : "Initial deployment completed."}
                        else:
                            print_colored('ON HOLD', 'cyan', "Initial deployment has not finished yet, waiting for 30 sec, no of retries: "+ str(repeats), no, 1, nooo)
                            repeats=repeats-1
                            nooo=nooo+1
                            time.sleep(30)   
                    
                    print_colored('ON HOLD', 'cyan', "FTD not registered yet, waiting for 30 sec, no of retries: "+ str(repeats), no, 6, nooo)
                else:
                    if "deploymentNote" is in jobH["text"].keys():
                        if jobH["text"][len(jobH["text"])-1]["deploymentNote"] == "Deployment after registration":
                            #print_colored('ON HOLD', 'cyan', "Initial deployment completed.", no, 1)
                            repeats=0
                            return {"response" : True, "text" : "Initial deployment completed."}
                        else:
                            print_colored('ON HOLD', 'cyan', "Initial deployment has not finished yet, waiting for 30 sec, no of retries: "+ str(repeats), no, 1, nooo)
                            repeats=repeats-1
                            nooo=nooo+1
                            time.sleep(30)                           

        return {"response" : False, "text" : "Error while polling the current deployment."+str(adding_ftd["text"])}
########    step 6:
########    Interfaces checks?
           
    def step_6_J2F(self, no):
        global interfaces
        global ftd
        int_id={}
        int_id["ids"]=[]
        for each in interfaces:
            if "id" in each.keys():
                int_id["found"]=True
                int_id["ids"].append(each["id"])
            else:
                int_id["found"]=False
                break
        
        if int_id["found"]:
            return {"response" : True, "text" : int_id["ids"]}   
        else:
            print_colored('ON HOLD', 'cyan', "No interfaces id found, polling the interfaces id for FTD: "+ftd["id"], no, 1)
            #interfaces=[]
            int_to_print=""
            int_response=fmc.devices.devicerecords.physicalinterfaces.get(ftd["id"])
            
            #updating interface id
            noo=1
            for each in int_response["text"]:
                del each["links"] 
                update_int_id(each["name"], each["id"])
                #interfaces.append(each)
                print_colored('ON HOLD', 'cyan', "Successfully  found interfaces id for: "+each["name"]+" id: "+each["id"], no, 1, noo)
                int_id["ids"].append(each["id"])
                noo=noo+1

             
            print_colored('ON HOLD', 'cyan', "Updating interface status... ", no, 2)
            #updating interface status
            noo=1            
            for each in interfaces:
                int_update=fmc.devices.devicerecords.physicalinterfaces.put(each, ftd["id"])
                if int_update["code"] < 300:
                    print_colored('ON HOLD', 'cyan', "Successfully  updated the status of the interface id: "+each["id"], no, 2, noo)
                    noo=noo+1
                else:
                    return {"response" : False, "text" : int_update["text"]}

            with open(file_Interfaces_json, 'w') as outfile:
                json.dump(interfaces, outfile, indent = 4) 

            return {"response" : True, "text" : int_id["ids"]}  
            #adding_ftd=fmc.devices.devicerecords.post(ftd)    
            
            
########    step 7:
########    SecurityZone checks?
           
    def step_7_J2F(self, no):
        global SecurityZone
        global interfaces
        global ftd

        SZ_id={}
        SZ_id["ids"]=[]
        for each in SecurityZone:
            if "id" in each.keys():
                SZ_id["found"]=True
                SZ_id["ids"].append(each["id"])
            else:
                SZ_id["found"]=False
                break 

        if SZ_id["found"]:
            return {"response" : True, "text" : SZ_id["ids"]}   
        else:
            print_colored('ON HOLD', 'cyan', "No SecurityZone id found, adding the SecurityZone to FMC: ", no, 1)
            hlp_SecurityZone=[]
            for each_SZ in SecurityZone:
                each_int_hlp=[]
                for each_int in each_SZ["interfaces"]:
                    if "id" not in each_int.keys():
                        each_int["id"]=int_name2id(each_int["name"])
                    each_int_hlp.append(each_int)
                each_SZ["interfaces"]=each_int_hlp
                hlp_SecurityZone.append(each_SZ)

            print_colored('ON HOLD', 'cyan', "Updated the id for interfaces included in SecurityZones... ", no, 2)
            noo=1
            hlp2_SecurityZone=[]
            for each in hlp_SecurityZone:
                adding_SZ=fmc.object.securityzones.post(each)
                if adding_SZ["code"] < 300:
                    print_colored('ON HOLD', 'cyan', "Updated the SecurityZones name: "+adding_SZ["text"]["name"], no, 3, noo)
                    noo=noo+1
                    each["id"]=adding_SZ["text"]["id"]
                    SZ_id["ids"].append(each["id"])
                else:
                    return {"response" : False, "text" : adding_SZ["text"]}
                hlp2_SecurityZone.append(each)
            

            #print(hlp_SecurityZone)    
            
            with open(file_SecurityZone_json, 'w') as outfile:
                json.dump(hlp2_SecurityZone, outfile, indent = 4)
                
        return {"response" : True, "text" : SZ_id["ids"]}  
        
        
        
########    step 8:
########    NetworkObjects checks 
           
    def step_8_J2F(self, no):
        global NetHostObj
        NetHostObj_txt=""

        for each in NetHostObj:
            if "id" not in each.keys():
                print_colored('ON HOLD', 'cyan', "Network/Host Object id not found, adding object: "+each["name"], no, 1)
                adding_NetHostObj=add_NetHostObj(each)
                if adding_NetHostObj["code"] < 300:
                    print_colored('ON HOLD', 'cyan', "Successfully added object with id: "+adding_NetHostObj["text"]["id"], no, 1, 1)
                    NetHostObj_txt=NetHostObj_txt+adding_NetHostObj["text"]["name"]+", "
                else:
                    return {"response" : False, "text" : adding_NetHostObj["text"]}  
            else:
                NetHostObj_txt=NetHostObj_txt+each["name"]+", "
        
        
            with open(file_NetHostObj_json, 'w') as outfile:
                json.dump(NetHostObj, outfile, indent = 4)
                
        return {"response" : True, "text" : NetHostObj_txt}  
        
        
########    step 9:
########    Portprotocols checks 
           
    def step_9_J2F(self, no):

        global ProtocolPortObject
        ProtocolPortObject_txt=""

        for each in ProtocolPortObject:
            if "id" not in each.keys():
                print_colored('ON HOLD', 'cyan', "Port/Protocol Object id not found, adding object: "+each["name"], no, 1)
                adding_ProtocolPortObject=add_ProtocolPortObject(each)

                if adding_ProtocolPortObject["code"] < 300:
                    print_colored('ON HOLD', 'cyan', "Successfully added object with id: "+adding_ProtocolPortObject["text"]["id"], no, 1, 1)
                    ProtocolPortObject_txt=ProtocolPortObject_txt+adding_ProtocolPortObject["text"]["name"]+", "
                else:
                    return {"response" : False, "text" : adding_ProtocolPortObject["text"]}  
            else:
                ProtocolPortObject_txt=ProtocolPortObject_txt+each["name"]+", "
        
        
            with open(file_ProtocolPortObject_json, 'w') as outfile:
                json.dump(ProtocolPortObject, outfile, indent = 4)
                
        return {"response" : True, "text" : ProtocolPortObject_txt} 
        
########    step 10:
########    Net/Host Groups checks 
           
    def step_10_J2F(self, no):
        NetGrps_txt=""
        NetGrps_on_fmc={}
        global NetworkGroups
        #create acp dict from fmc
        NetGrps_get=fmc.object.networkgroups.get()
        if NetGrps_get["code"] < 300:
            for each in NetGrps_get["text"]:
                NetGrps_on_fmc[each["id"]]={"name": each["name"], "type": each["type"], "description": each["description"], "overridable": bool(each["overridable"]), "id": each["id"]}
                if "objects" in each.keys():
                    NetGrps_on_fmc[each["id"]].update({"objects": each["objects"]})
                if "literals" in each.keys():
                    NetGrps_on_fmc[each["id"]].update({"literals": each["literals"]})


        obj_in_netGrps=0 
        if CheckNetGrpsID():
            noo=1
            for each in NetworkGroups:
                if "id" in each.keys():
                    NetGrps_txt=each["id"]+", "+NetGrps_txt
                else:
                    add_netgrp=fmc.object.networkgroups.post(each)
                    if add_netgrp["code"] < 300:
                        print_colored('PASS', 'green', "Successfuly added NetGroupst Object with id: "+add_netgrp["text"][0]["id"], no, 1, noo)
                        NetworkGroups[obj_in_netGrps]["id"]=add_netgrp["text"][0]["id"]
                    else:
                        print_colored(add_netgrp["text"])
                    noo=noo+1
                obj_in_netGrps=obj_in_netGrps+1
            
                
            with open(file_NetworkGroups_json, 'w') as outfile:
                json.dump(NetworkGroups, outfile, indent = 4)
        
        return {"response" : True, "text" : NetGrps_txt} 

########    step 11:
########    PortProto Groups checks 
           
    def step_11_J2F(self, no):
        PortGrps_txt=""
        PortGrps_on_fmc={}
        global PortObjectGroups
        #create acp dict from fmc
        PortGrps_get=fmc.object.portobjectgroups.get()
        
        if PortGrps_get["code"] < 300:
            if isinstance(PortGrps_get["text"], list):
                for each in PortGrps_get["text"]:
                    PortGrps_on_fmc[each["id"]]={"name": each["name"], "type": each["type"], "description": each["description"], "overridable": bool(each["overridable"]), "id": each["id"]}
                    if "objects" in each.keys():
                        PortGrps_on_fmc[each["id"]].update({"objects": each["objects"]})
            else:
                if "id" in PortGrps_get["text"].keys():
                    PortGrps_on_fmc[PortGrps_get["text"]["id"]]={"name": PortGrps_get["text"]["name"], "type": PortGrps_get["text"]["type"], "description": PortGrps_get["text"]["description"], "overridable": bool(PortGrps_get["text"]["overridable"]), "id": PortGrps_get["text"]["id"]}
                    if "objects" in PortGrps_get["text"].keys():
                        PortGrps_on_fmc[PortGrps_get["text"]["id"]].update({"objects": PortGrps_get["text"]["objects"]})                    

        obj_in_portGrps=0 
        if CheckPortProtoGrpID():
            noo=1
            for each in PortObjectGroups:
                if "id" in each.keys():
                    PortGrps_txt=each["id"]+", "+PortGrps_txt
                else:
                    add_portgrp=fmc.object.portobjectgroups.post(each)
                    if add_portgrp["code"] < 300:
                        print_colored('PASS', 'green', "Successfuly added Port/Proto Group Object with id: "+add_portgrp["text"][0]["id"], no, 1, noo)
                        PortObjectGroups[obj_in_portGrps]["id"]=add_portgrp["text"][0]["id"]
                    else:
                        print_colored(add_portgrp["text"])
                noo=noo+1
                obj_in_portGrps=obj_in_portGrps+1
            
                
            with open(file_PortObjectGroups_json, 'w') as outfile:
                json.dump(PortObjectGroups, outfile, indent = 4)

        return {"response" : True, "text" : PortGrps_txt}

########    step 12:
########    ACE 
           
    def step_12_J2F(self, no):
        global NetHostObj        
        global SecurityZone
        global ftd        
        global acp
        global ace   
        ACE_txt=""
        noo=1

        nooo=1
        if not CheckACEID():
            print_colored('ON HOLD', 'cyan', "Updating ACE with object id...", no, noo)
            UpdateACEID()
            noo=1
            nooo=1
            
        
            #check ACE ID
        for each in ace:
            if "id" not in each.keys():
                print_colored('ON HOLD', 'cyan', "Adding ACE to ACP: "+acp["name"], no, noo, nooo) 
                added_ACE=fmc.policy.accesspolicies.accessrules.post(each, acp["id"])
                if added_ACE["code"] < 300:
                    
                    ACE_txt=ACE_txt+added_ACE["text"]["name"]+", "
                    update_ace_id(each["name"], added_ACE["text"]["id"])
                    
                    with open(file_ACE_json, 'w') as outfile:
                        json.dump(ace, outfile, indent = 4)
                else:
                    return {"response" : False, "text" : added_ACE["text"] }
                nooo=nooo+1
                    
            else:
                ACE_txt=ACE_txt+each["name"]+", "   
            noo=noo+1    
        return {"response" : True, "text" : ACE_txt}  


########    step 13:
########    NAT Policy checks?
           
    def step_13_J2F(self, no):
        global nat
        if "id" in nat.keys():
            return {"response" : True, "text" : nat["id"]}              
        else:
            print_colored('ON HOLD', 'cyan', "No NAT Policy id found, adding NAT: ", no, 1)
            adding_nat=fmc.policy.ftdnatpolicies.post(nat)
            if adding_nat["code"] < 300:
                nat["id"]=adding_nat["text"]["id"]
                print_colored('PASS', 'green', "Successfully  added NAT Policy with id: "+nat["id"], no, 2)
                with open(file_NAT_json, 'w') as outfile:
                    json.dump(nat, outfile, indent = 4) 
               
                return {"response" : True, "text" : nat["id"]}
            else:
                return {"response" : False, "text" : adding_nat["text"]}
        #return {"response": False, "text" : file_NAT_json}
            
        return {"response" : True, "text" : nat["id"]}  


########    step 14:
########    NAT Rule check
           
    def step_14_J2F(self, no):
        global NetHostObj        
        global natRules
        global nat
        NatR_txt=""
        noo=1

        nooo=1
        if not CheckNatRID():
            print_colored('ON HOLD', 'cyan', "Updating NAT Rule with object id...", no, noo)
            UpdateNatRID()
            noo=noo+1
            nooo=nooo+1
            
        
            #check ACE ID
        row=0    
        for each in natRules:
            if "id" not in each.keys():
                print_colored('ON HOLD', 'cyan', "Adding NAT Rule to NAT: ", no, noo, nooo) 
                added_NatR=fmc.policy.ftdnatpolicies.manualnatrules.post(each, nat["id"])
                if added_NatR["code"] < 300:
                    #print(json.dumps(added_NatR["text"], indent=4))
                    NatR_txt=NatR_txt+str(added_NatR["text"]["metadata"]["index"])+", "
                    natRules[row]["id"]=added_NatR["text"]["id"]
                    
                    with open(file_NAT_Rule_json, 'w') as outfile:
                        json.dump(natRules, outfile, indent = 4)
                else:
                    return {"response" : False, "text" : added_NatR["text"] }
                nooo=nooo+1                        
            else:
                NatR_txt=NatR_txt+each["type"]+", "   
            noo=noo+1   
            row=row+1 

        return {"response" : True, "text" : NatR_txt}  

########    step 15:
########    ACP/ NAT Policy Assignmentt check
           
    def step_15_J2F(self, no):
        global ftd
        global acp
        global nat
        global PolicyAssignment
        checks={"result":False, "name": [] }
        
        #checking if json file has id
        for each in  PolicyAssignment:
            if "id" in each.keys():
                checks["result"]=True
                checks["name"].append(each["name"])
            else:
                checks["result"]=False
                checks["name"].append(each["name"])
              
        New_PolicyAssignment=fmc.assignment.policyassignments.get()
        if New_PolicyAssignment["code"] < 300:
            if len(New_PolicyAssignment["text"]) != len(PolicyAssignment):
                checks["result"]=False
                print_colored('ON HOLD', 'cyan', "Policy Assignment changed: ", no, 1)

        else:
            return {"response" : False, "text" : fmc_PolicyAssignment["text"]}
        #if json file has it, im not douing further tests i assume that it was automatically created and it is good and there is no need to push it to fmc
        #if json dosn't have id, im updating json and pushing it to fmc        
        if checks["result"]:
            return {"response" : True, "text" : checks["name"]}
        else:
            print_colored('ON HOLD', 'cyan', "No id found for name: "+str(checks["name"]), no, 2)
            print_colored('ON HOLD', 'cyan', "Updating PolicyAssignment list in JSON file", no, 3)
            update_PolicyAssignment()
            print_colored('ON HOLD', 'cyan', "Updating PolicyAssignment on FMC", no, 4)
            
            noo=1
            for each in PolicyAssignment:
                fmc_PolicyAssignment=fmc.assignment.policyassignments.put(each)
                if fmc_PolicyAssignment["code"] < 300:
                    print_colored('PASS', 'green', "Successfully  assigned policy name: "+fmc_PolicyAssignment["text"]["name"], no, 5, noo)
                    noo=noo+1
                else:
                    return {"response" : False, "text" : fmc_PolicyAssignment["text"]}  
            
            
        return {"response" : True, "text" : ftd["id"]}  
        
########    step 16:
########    Deployment
#    
    def step_16_J2F(self, no):
        global ftd        
        fmc_deployment=fmc.deployment.deployabledevices.get()
        if fmc_deployment["code"] < 300:
            if isinstance(fmc_deployment["text"], list):
                deployment_pending_dev=[]
                deployment_pending_ver=[]
                for each in fmc_deployment["text"]:
                    deployment_pending_dev.append(each["name"])
                    deployment_pending_ver.append(each["version"])
                print_colored('ON HOLD', 'cyan', "Found following devices pending the deployment: "+str(deployment_pending_dev)+" Deployment version: "+str(deployment_pending_ver), no, 1)
                proceed=input('Proceed with the deployment y/n?:')
                if proceed == "y" or proceed == "y" or proceed == "yes" or proceed == "YES":
                    for each_dep_pending in fmc_deployment["text"]:
                        Deployment["version"]= each_dep_pending["version"]
                        Deployment["deviceList"]=[ftd["id"]]
                        fmc_deployed=fmc.deployment.deploymentrequests.post(Deployment)
                        if fmc_deployed["code"] < 300:
                            print_colored('PASS', 'green', "Successfully  sent deployment request for version: "+fmc_deployed["text"]["version"], no, 2)
                            return {"response" : True, "text" : "Deployment request sent successfuly"}
                        else:
                            return {"response" : False, "text" : fmc_deployed["text"]} 
                else:
                    return {"response" : False, "text" : "Deployment not confirmed for device: "+str(deployment_pending_dev)}
                    
            else:
                return {"response" : True, "text" : "Nothing to be deployed."}

        else:
            return {"response" : False, "text" : fmc_deployment["text"]} 
            