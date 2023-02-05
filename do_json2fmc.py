from CiscoLive import JSON_2_FMC
from termcolor import colored
import getpass

#grey, red, green, yellow, blue, magenta, cyan, white


no=0


def print_colored(msg1, col1, text1, no1, no2=None, no3=None):
    if no3==None:
        if no2==None:
            print(colored(str(no1), 'yellow'), colored(msg1, col1), colored(text1, 'white'))
        else:
            print(colored(str(no1), 'yellow'), colored(str(no2), 'yellow'), colored(msg1, col1), colored(text1, 'white'))
    else:
        print(colored(str(no1), 'yellow'), colored(str(no2), 'yellow'), colored(str(no3), 'yellow'), colored(msg1, col1), colored(text1, 'white'))


print_colored("START: ", "blue", "Script will parse all json files and will push the configuration to the FMC ",  1)

fmc_ip=input('Please enter FMC IP address:')
username = input('Username:')
password = getpass.getpass('Password:')

#fmc_ip="10.62.158.66"
#username="apiadmin"
#password="Cisco123!"

CiscoLive=JSON_2_FMC(fmc_ip, username, password)

#### helper
#print(
# CiscoLive.step_0())
#quit()


step=CiscoLive.step_1_J2F()
if step["response"]:
    print_colored('PASS', 'green', "Successfully connected to FMC: "+fmc_ip+" with uuid: "+step["text"],  1)
else:
    print_colored('ERROR', 'red', "Couldn't connected to FMC: "+fmc_ip, 1)
    quit()
    
    

step=CiscoLive.step_2_J2F()
if step["response"]:
    print_colored('PASS', 'green', "Successfully loaded all JSON files",  2)
else:
    print_colored('ERROR', 'red', "Couldn't load JSON files: "+step["text"], 2)
    quit()
    
    

step=CiscoLive.step_3_J2F(3)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found ACP id: "+ step["text"], 3)
else:
    print_colored('ERROR', 'red', "Error during ACP id validation: "+str(step["text"]), 3)
    print_colored('EXITING', 'magenta', "Please confirm deployment for pending devices", 0)
    quit()   
    
    

step=CiscoLive.step_4_J2F(4)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found FTD with id: "+step["text"], 4)
else:
    print_colored('ERROR', 'red', "Error during FTD id validation: "+str(step["text"]), 4)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()   
    

######### step 5 checking interfaces
step=CiscoLive.step_5_J2F(5)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found interfaces id's: "+str(step["text"]), 5)
else:
    print_colored('ERROR', 'red', "Error during interface id validation: "+str(step["text"]), 5)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()       
    
 

########    step 6:
########    SecurityZone checks? 
step=CiscoLive.step_6_J2F(6)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found SecurityZone id's: "+str(step["text"]), 6)
else:
    print_colored('ERROR', 'red', "Error during SecurityZone id validation: "+str(step["text"]), 6)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()     
    
    
########    step 7:
########    NetworkObjects checks 
step=CiscoLive.step_7_J2F(7)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found Network Object id's: "+str(step["text"]), 7)
else:
    print_colored('ERROR', 'red', "Error during Network Object id validation: "+str(step["text"]), 7)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()      

    
########    step 8:
########    PORTProtocol checks 
step=CiscoLive.step_8_J2F(8)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found Port/Protocol Object id's: "+str(step["text"]), 8)
else:
    print_colored('ERROR', 'red', "Error during Port/Protocol Object id validation: "+str(step["text"]), 8)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()      

########    step 9:
########    NetworkGoupr checks 
step=CiscoLive.step_9_J2F(9)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found Network Group Object id's: "+str(step["text"]), 9)
else:
    print_colored('ERROR', 'red', "Error during Network Group Object id validation: "+str(step["text"]), 9)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit() 

########    step 10:
########    PORTProtocol Group checks 
step=CiscoLive.step_10_J2F(10)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found Port/Protocol Group Object id's: "+str(step["text"]), 10)
else:
    print_colored('ERROR', 'red', "Error during Port/Protocol Group Object id validation: "+str(step["text"]), 10)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()     
    
########    step 11:
########    ACE checks 
step=CiscoLive.step_11_J2F(11)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found id's for following ACE entries: "+str(step["text"]), 11)
else:
    print_colored('ERROR', 'red', "Error during ACE id validation: "+str(step["text"]), 11)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()      

    
########    step 12:
########    NAT policy checks 
step=CiscoLive.step_12_J2F(12)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found id for NAT Policy: "+str(step["text"]), 12)
else:
    print_colored('ERROR', 'red', "Error during NAT Policy id validation: "+str(step["text"]), 12)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()  

    
########    step 13:
########    NAT RUle checks 
step=CiscoLive.step_13_J2F(13)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully found id's for following NAT Rules: "+str(step["text"]), 13)
else:
    print_colored('ERROR', 'red', "Error during NAT Rules id validation: "+str(step["text"]), 13)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()    
    
########    step 14:
########    ACP/NAT policy assignement check 
step=CiscoLive.step_14_J2F(14)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully checked Policy Assignment for FTD id t: "+str(step["text"]), 14)
else:
    print_colored('ERROR', 'red', "Error during Policy Assignment validation for FTD id : "+str(step["text"]), 14)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()  


 ##### step 15 waiting for initial deployment to finish
step=CiscoLive.step_15_J2F(15)
if step["response"]: 
    print_colored('PASS', 'green', "Success, There is no ongoing deployment.", 15)
else:
    print_colored('ERROR', 'red', "Error during initial deployment: "+str(step["text"]), 15)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)
    quit()   

########    step 16:
########    Deployment
step=CiscoLive.step_16_J2F(16)
if step["response"]: 
    print_colored('PASS', 'green', "Successfully completed deployment checks with result: "+str(step["text"]), 16)
else:
    print_colored('ERROR', 'red', "Error during the deployment: "+str(step["text"]), 16)
    print_colored('EXITING', 'magenta', "Please fix the problem and restart the script", 0)    
    quit()  

    
print_colored("FINISHED! ", "blue", "Script completed successfully!", 17)