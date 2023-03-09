########################################
###   python class for cloud automation
########################################

#importing modules:
import requests
import json
import base64
import getpass
import time

#disabling warning about unsecure https
from requests.packages.urllib3.exceptions import InsecureRequestWarning
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

#connect to FMC
class Connect:
    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        verify_cert=False, #for now it is hardcoded - tbc
    ):
        self.hostname=hostname
        self.username=username
        self.password=password
        #building FMC URL
        #this is URI to get the domain uuid:
        uri='/api/fmc_platform/v1/info/domain'
        #requesting domain ID
        url=hostname+uri
        base64string = base64.encodebytes(('%s:%s' % (username, password)).encode('utf8')).decode('utf8').replace('\n', '')
        authstring = ('Basic %s' % base64string)
        self.headers = {'Authorization' : authstring, 'Content-Type' : 'application/json'}
        url_auth=hostname+'/api/fmc_platform/v1/auth/generatetoken'
        response = requests.post(url_auth, headers = self.headers, verify=False)

        XauthToken = response.headers['x-auth-access-token']
        XauthRefToken = response.headers['X-auth-refresh-token']

        self.headers = {'x-auth-access-token' : XauthToken, 'X-auth-refresh-token' : XauthRefToken, 'Content-Type' : "application/json"}

        response = requests.get(url, headers = self.headers, verify=False)


        #getting UUID from the response
        self.uuid = json.loads(response.text)['items'][0]['uuid']

################################################################################################################
### Domain
################################################################################################################

class domain:
    def __init__(self,conn):
        self.conn=conn    
    def get(self):
        uri='/api/fmc_platform/v1/info/domain'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        
        if response.status_code < 300:
            return json_data["items"][0]["uuid"]
        else:
            return None       
       
    
################################################################################################################
### Objects
################################################################################################################
class object:
    def __init__(self,conn):
        self.conn=conn
        self.networks=networks(self.conn)        
        self.networkgroups=networkgroups(self.conn)   
        self.hosts=hosts(self.conn)        
        self.securityzones=securityzones(self.conn)
        self.protocolportobjects=protocolportobjects(self.conn)
        self.portobjectgroups=portobjectgroups(self.conn)

class securityzones:
    def __init__(self,conn):
        self.conn=conn
    def get(self):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/securityzones?expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
        else:
            pages=0
        if pages != 0:
            json_list=json_data['items']
        else:
            if "item" in json_data.keys():
                return {"code": response.status_code, "text": json_data['items']}
            else:
                return {"code": response.status_code, "text": []}
        while pages > 0:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/securityzones?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}

    def post(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/securityzones'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}
            
class networks:
    def __init__(self,conn):
        self.conn=conn
    def get(self, uuid=None):
        offset=0
        limit=100
        if uuid is None:
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networks?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
        else:
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networks/'+uuid+'&expanded=True'

        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)            
        if response.status_code == 429:
            print("We have to wait due to HTTP 429")
            time.sleep(45)
            response = requests.get(url, headers = self.conn.headers, verify=False)     

        json_data=json.loads(response.text)
        
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
        else:
            pages=0
        if pages != 0:
            json_list=json_data['items']
        else:
            return {"code": response.status_code, "text": json_data}

        while pages > 0:
            offset=offset+limit
            if uuid is None:
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networks?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            else:
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networks/'+uuid+'&expanded=True'

            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)

            if response.status_code == 429:
                print("We have to wait due to HTTP 429")
                time.sleep(45)
                response = requests.get(url, headers = self.conn.headers, verify=False)

            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']            
            pages=pages-1
            
        return {"code": response.status_code, "text": json_list}  
        
    def delete(self, uuid, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networks/'+uuid
        url=self.conn.hostname+uri 
        response = requests.delete(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items'] 
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
            
    def post(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networks?bulk=true'
        url=self.conn.hostname+uri 
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items'] 
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}

    def put(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networks/'+data_payload["id"]
        url=self.conn.hostname+uri 
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items'] 
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}

class hosts:
    def __init__(self,conn):
        self.conn=conn
    def get(self, uuid=None):
        offset=0
        limit=100
        if uuid is None:        
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/hosts?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
        else:
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/hosts/'+uuid
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)

        if response.status_code == 429:
            print("We have to wait due to HTTP 429")
            time.sleep(45)
            response = requests.get(url, headers = self.conn.headers, verify=False)

        json_data=json.loads(response.text)
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']    
        else:
            pages=0
            
        if pages != 0:
            json_list=json_data['items']
        else:
            return {"code": response.status_code, "text": json_data}

        while pages > 0:
            offset=offset+limit
            if uuid is None: 
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/hosts?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            else:
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/hosts/'+uuid+'?offset='+str(offset)+'&limit='+str(limit)
            url=self.conn.hostname+uri

            response = requests.get(url, headers = self.conn.headers, verify=False)

            if response.status_code == 429:
                print("We have to wait due to HTTP 429")
                time.sleep(45)
                response = requests.get(url, headers = self.conn.headers, verify=False)

            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']      
            pages=pages-1
            
        
        return {"code": response.status_code, "text": json_list}  

    def delete(self, uuid, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/hosts/'+uuid
        url=self.conn.hostname+uri 
        response = requests.delete(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items'] 
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
        
    def post(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/hosts?bulk=true'
        url=self.conn.hostname+uri 
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        if response.status_code == 429:
            print("We have to wait due to HTTP 429")
            time.sleep(45)
            response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_data=json.loads(response.text)


        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
            
    def put(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/hosts/'+data_payload["id"]
        url=self.conn.hostname+uri 
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)


        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
            
class protocolportobjects:
    def __init__(self,conn):
        self.conn=conn
    def get(self):
        offset=0
        limit=100    
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/protocolportobjects?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)

        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
        else:
            pages=0
        if pages != 0:
            json_list=json_data['items']
        else:
            if "item" in json_data.keys():
                return {"code": response.status_code, "text": json_data['items']}
            else:
                return {"code": response.status_code, "text": []}
            
        while pages > 0:
            offset=offset+limit
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/protocolportobjects?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']            
            pages=pages-1
            
        return {"code": response.status_code, "text": json_list} 

    def delete(self, uuid, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/protocolportobjects/'+uuid
        url=self.conn.hostname+uri 
        response = requests.delete(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items'] 
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}

    def post(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/protocolportobjects?bulk=true'
        url=self.conn.hostname+uri 
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)
        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
            
    def put(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/protocolportobjects/'+data_payload["id"]
        url=self.conn.hostname+uri 
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)
        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
        
class networkgroups:
    def __init__(self,conn):
        self.conn=conn
    def get(self):
        offset=0
        limit=100
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networkgroups?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
        else:
            pages=0
        if pages != 0:
            json_list=json_data['items']
        else:
            if "item" in json_data.keys():
                return {"code": response.status_code, "text": json_data['items']}
            else:
                return {"code": response.status_code, "text": []}

        while pages > 0:
            offset=offset+limit
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networkgroups?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)

            if response.status_code == 429:
                print("We have to wait due to HTTP 429")
                time.sleep(45)
                response = requests.get(url, headers = self.conn.headers, verify=False)

            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']            
            pages=pages-1
            
        return {"code": response.status_code, "text": json_list}    

    def post(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networkgroups?bulk=true'
        url=self.conn.hostname+uri 
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        if response.status_code == 429:
            print("We have to wait due to HTTP 429")
            time.sleep(45)
            response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}

    def delete(self, uuid, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networkgroups/'+uuid
        url=self.conn.hostname+uri 
        response = requests.delete(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items'] 
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}

    def put(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/networkgroups/'+data_payload["id"]
        url=self.conn.hostname+uri 
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)


        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
        
class portobjectgroups:
    def __init__(self,conn):
        self.conn=conn
    def get(self):
        offset=0
        limit=100    
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/portobjectgroups?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
        else:
            pages=0
        if pages != 0:
            json_list=json_data['items']
        else:
            if "item" in json_data.keys():
                return {"code": response.status_code, "text": json_data['items']}
            else:
                return {"code": response.status_code, "text": []}
            
        while pages > 0:
            offset=offset+limit
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/portobjectgroups?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']            
            pages=pages-1
            
        return {"code": response.status_code, "text": json_list} 

    def delete(self, uuid, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/portobjectgroups/'+uuid
        url=self.conn.hostname+uri 
        response = requests.delete(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)

        if 'items' in json_data.keys():
            json_list=json_data['items'] 
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}

    def post(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/portobjectgroups?bulk=true'
        url=self.conn.hostname+uri 
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)
        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
            
    def put(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/object/portobjectgroups/'+data_payload["id"]
        url=self.conn.hostname+uri 
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)
        if 'items' in json_data.keys():
            json_list=json_data['items']
        else:
            json_list=json_data
        return {"code": response.status_code, "text": json_list}
   
################################################################################################################
### Policy
################################################################################################################
class policy:
    def __init__(self,conn):
        self.conn=conn
        self.accesspolicies=accesspolicies(self.conn)
        self.ftdnatpolicies=ftdnatpolicies(self.conn)
        
class accesspolicies:
    def __init__(self,conn):
        self.conn=conn
        self.accessrules=accessrules(self.conn)

    def get(self, uuid=None):
        offset=0
        limit=25
        if uuid==None:
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies?expanded=true'
        else:
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies/'+uuid
        url=self.conn.hostname+uri

        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
        else:
            pages=0
            
        if pages != 0:
            json_list=json_data['items']
        else:
            return {"code": response.status_code, "text": json_data}

        while pages > 0:
            offset=offset+25
            if uuid==None:
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            else:
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies/'+uuid+'?offset='+str(offset)+'&limit='+str(limit)
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}

    def put(self,data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies/'+data_payload["id"]
        url=self.conn.hostname+uri
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}
        
    def post(self,data_payload, uuid=None):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}

class accessrules:
    def __init__(self,conn):
        self.conn=conn

    def get(self, uuid):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies/'+uuid+'/accessrules?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)

        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
            if "items" in json_data.keys():
                json_list=json_data['items']
            else:
                json_list=[]
        else:
            pages=0
            if "items" in json_data.keys():
                json_list=json_data['items']
            else:
                json_list=[]    
            return {"code": response.status_code, "text": json_list}

        while pages > 0:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies/'+uuid+'/accessrules?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}

    def post(self,data_payload, uuid):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies/'+uuid+'/accessrules'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}

class ftdnatpolicies:
    def __init__(self,conn):
        self.conn=conn
        self.manualnatrules=manualnatrules(self.conn)

    def get(self):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/ftdnatpolicies?expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
            if "items" in json_data.keys():
                json_list=json_data['items']
            else:
                json_list=[]
        else:
            pages=0
            return {"code": response.status_code, "text": json_data}

        while pages > 0:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/accesspolicies?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}

    def post(self,data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/ftdnatpolicies'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}
            
 
class manualnatrules:
    def __init__(self,conn):
        self.conn=conn    

    def get(self, uuid):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/ftdnatpolicies/'+uuid+'/manualnatrules?expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        pages=json_data['paging']['pages']

        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
            json_list=json_data['items']
        else:
            pages=0
            return {"code": response.status_code, "text": json_data}

        while pages > 0:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/ftdnatpolicies/'+uuid+'/manualnatrules?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}
        
    def post(self,data_payload,uuid):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/policy/ftdnatpolicies/'+uuid+'/manualnatrules'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)
        json_data=json.loads(response.text)
        return {"code": response.status_code, "text": json_data}
        
################################################################################################################
### Devices
################################################################################################################
class devices:
    def __init__(self,conn):
        self.conn=conn
        self.devicerecords=devicerecords(self.conn)

class devicerecords:
    def __init__(self,conn):
        self.conn=conn
        self.physicalinterfaces=physicalinterfaces(self.conn)
        
    def get(self, uuid=None):
        offset=0
        limit=25
        if uuid==None:
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords?expanded=True'
        else:
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords/'+uuid
       
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)

        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
            if "items" in json_data.keys():
                json_list=json_data['items']
            else:
                if response.status_code < 300:
                    json_list=[]
                else:
                    json_list=json_data
        else:
            pages=0
            if "items" in json_data.keys():
                json_list=json_data['items']
            else:
                if response.status_code < 300:
                    json_list=[]
                else:
                    json_list=json_data 
            return {"code": response.status_code, "text": json_list}

        while pages > 0:
            offset=offset+25
            if uuid==None:
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            else:
                uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords/'+uuid
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            
            if 'items' in json_data:
                json_list=json_list+json_data['items']

            pages=pages-1

        return {"code": response.status_code, "text": json_list}

    def post(self,data_payload):

        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}


class physicalinterfaces:
    def __init__(self,conn):
        self.conn=conn

    def get(self,uuid):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords/'+uuid+'/physicalinterfaces?expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        pages=json_data['paging']['pages']

        if pages != 0:
            json_list=json_data['items']
        else:
            return {"code": response.status_code, "text": json_data}

        while pages > 1:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords/'+uuid+'/physicalinterfaces?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']

            pages=pages-1

        return {"code": response.status_code, "text": json_list}

    def put(self,data_payload, uuid):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/devices/devicerecords/'+uuid+'/physicalinterfaces/'+data_payload["id"]
        url=self.conn.hostname+uri
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}

################################################################################################################
### Deployment
################################################################################################################
class deployment:
    def __init__(self,conn):
        self.conn=conn
        self.deployabledevices=deployabledevices(self.conn)
        self.deploymentrequests=deploymentrequests(self.conn)        
        self.jobhistories=jobhistories(self.conn)

class deployabledevices:
    def __init__(self,conn):
        self.conn=conn
        
    def get(self):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/deployment/deployabledevices'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        pages=json_data['paging']['pages']

        if pages != 0:
            json_list=json_data['items']
        else:
            json_list=json.loads(response.text)
            return {"code": response.status_code, "text": json_list}

        while pages > 0:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/deployment/deployabledevices?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}    
            
class deploymentrequests: 
    def __init__(self,conn):
        self.conn=conn
        
    def post(self, data_payload):
     
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/deployment/deploymentrequests'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        return {"code": response.status_code, "text": json.loads(response.text)}  

class jobhistories:
    def __init__(self,conn):
        self.conn=conn

    def get(self):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/deployment/jobhistories?expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)

        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
            json_list=json_data['items']
        else:
            pages=0
            if "items" in json_data.keys():
                return {"code": response.status_code, "text": json_data["items"]}
            else:
                return {"code": response.status_code, "text": json_data}

        while pages > 0:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/deployment/deployabledevices?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}  

################################################################################################################
### Assignement
################################################################################################################
class assignment:
    def __init__(self,conn):
        self.conn=conn
        self.policyassignments=policyassignments(self.conn)
        
class policyassignments:
    def __init__(self,conn):
        self.conn=conn

    def get(self):
        offset=0
        limit=25
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/assignment/policyassignments?expanded=True'
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)
        json_data=json.loads(response.text)
        if "paging" in json_data.keys():
            pages=json_data['paging']['pages']
            if "items" in json_data.keys():
                json_list=json_data['items']
            else:
                json_list=[]
        else:
            pages=0
            return {"code": response.status_code, "text": json_data}

        while pages > 0:
            offset=offset+25
            uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/assignment/policyassignments?offset='+str(offset)+'&limit='+str(limit)+'&expanded=True'
            url=self.conn.hostname+uri
            response = requests.get(url, headers = self.conn.headers, verify=False)
            json_data=json.loads(response.text)
            if 'items' in json_data:
                json_list=json_list+json_data['items']
            pages=pages-1

        return {"code": response.status_code, "text": json_list}

    def post(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/assignment/policyassignments'
        url=self.conn.hostname+uri
        response = requests.post(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}
        
    def put(self, data_payload):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/assignment/policyassignments/'+data_payload["id"]
        url=self.conn.hostname+uri
        response = requests.put(url, headers = self.conn.headers, data = json.dumps(data_payload), verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}
        
################################################################################################################
### Job
################################################################################################################
class job:
    def __init__(self,conn):
        self.conn=conn
        self.taskstatuses=taskstatuses(self.conn)
        
class taskstatuses:
    def __init__(self,conn):
        self.conn=conn
        
    def get(self, uuid):
        uri='/api/fmc_config/v1/domain/'+self.conn.uuid+'/job/taskstatuses/'+uuid
        url=self.conn.hostname+uri
        response = requests.get(url, headers = self.conn.headers, verify=False)

        json_list=json.loads(response.text)
        return {"code": response.status_code, "text": json_list}
        
##############################################################################################################################
############# Main Class
##############################################################################################################################
class FMCAPIHandler:
    def __init__(self, ip, username, password):
        hostname = 'https://'+ip
        self._connect=Connect(hostname,username,password)
        self.object=object(self._connect)
        self.policy=policy(self._connect)
        self.devices=devices(self._connect)
        self.deployment=deployment(self._connect)        
        self.assignment=assignment(self._connect)   
        self.domain=domain(self._connect)
        self.job=job(self._connect)        
        
    def __del__(self):
        self.__close()

    def __close(self):
        if 'self._connect' in locals():
            del self._connect 
