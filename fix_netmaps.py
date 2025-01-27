import requests
import sys
import json
import ssl
from requests.adapters import HTTPAdapter
from urllib3 import poolmanager
import xml.etree.ElementTree as ET
from requests.auth import HTTPBasicAuth
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

class config_info:
    sspcm_user = 'admin'
    sspcm_pasw = 'Test@123'
    sspcm_base_url = 'https://gm250.hub4edi.dev:21443'
    session_token_uri = '/sspcmrest/sspcm/rest/session'
    all_netmap_uri = '/sspcmrest/sspcm/rest/netmap/getAllNetmaps'
    netmap_uri = '/sspcmrest/sspcm/rest/netmap/getNetmap/'
    update_netmap_uri='/sspcmrest/sspcm/rest/netmap/addNetmapNodes/'

class TLSAdapter(HTTPAdapter):
    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        ctx = ssl.create_default_context()
        ctx.set_ciphers('DEFAULT:@SECLEVEL=1')
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        self.poolmanager = poolmanager.PoolManager(
            num_pools=connections,
            maxsize=maxsize,
            block=block,
            ssl_context=ctx
        )

session = requests.Session()
session.mount("https://", TLSAdapter())

class netmap_manager(object):
    def __init__(self):
        self.config = config_info()
    def get_netmaps_list(self):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/xml'}
        #auth = HTTPBasicAuth(self.config.sspcm_user, self.config.sspcm_pasw)
        payload = {}
        payload['userId']=self.config.sspcm_user
        payload['password']=self.config.sspcm_pasw
        resp2 = session.post(self.config.sspcm_base_url+self.config.session_token_uri,headers=headers,data=json.dumps(payload),verify=False)
        if resp2.status_code == 200:
            response_xml = resp2.text
            root = ET.fromstring(response_xml)
            objects_list_str = root.find("objectsList").text
            session_data = json.loads(objects_list_str)
            session_token = session_data["sessionToken"]
            #print(session_token)
            headers['X-Authentication']=session_token
            resp = session.get(self.config.sspcm_base_url+self.config.all_netmap_uri,headers=headers, verify=False)
            if resp.status_code==200:
                xml_data = resp.text
                root = ET.fromstring(xml_data)
                objects_list_str = root.find("objectsList").text
                obj_array = json.loads(objects_list_str)
                return obj_array
        return None
    def get_netmap_details(self,netmap):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/xml'}
        #auth = HTTPBasicAuth(self.config.sspcm_user, self.config.sspcm_pasw)
        payload = {}
        payload['userId']=self.config.sspcm_user
        payload['password']=self.config.sspcm_pasw
        resp2 = session.post(self.config.sspcm_base_url+self.config.session_token_uri,headers=headers,data=json.dumps(payload),verify=False)
        if resp2.status_code == 200:
            response_xml = resp2.text
            #print(response_xml)
            root = ET.fromstring(response_xml)
            objects_list_str = root.find("objectsList").text
            session_data = json.loads(objects_list_str)
            session_token = session_data["sessionToken"]
            #print(session_token)
            headers['X-Authentication']=session_token
            headers['X-Passphrase']=self.config.sspcm_pasw
            headers['Accept']='*/*'
            resp = session.get(self.config.sspcm_base_url+self.config.netmap_uri+netmap,headers=headers, verify=False)
            #print(resp.text)
            if resp.status_code==200:
                resp_data = resp.text
                root = ET.fromstring(resp_data)
                value_escaped = root.find(".//value").text
                value_unescaped = value_escaped.replace("&lt;", "<").replace("&gt;", ">")
                #print(value_unescaped)
                netmap_root = ET.fromstring(value_unescaped)
                #print(netmap_root.find("name").text)
                return value_unescaped
            else:
                print(resp.status_code,resp.text)

        return None

    def update_netmap_details(self, netmap, payload2):
        headers = {'Content-Type': 'application/json', 'Accept': 'application/xml'}
        #auth = HTTPBasicAuth(self.config.sspcm_user, self.config.sspcm_pasw)
        payload = {}
        payload['userId']=self.config.sspcm_user
        payload['password']=self.config.sspcm_pasw
        resp2 = session.post(self.config.sspcm_base_url+self.config.session_token_uri,headers=headers,data=json.dumps(payload),verify=False)
        if resp2.status_code == 200:
            response_xml = resp2.text
            #print(response_xml)
            root = ET.fromstring(response_xml)
            objects_list_str = root.find("objectsList").text
            session_data = json.loads(objects_list_str)
            session_token = session_data["sessionToken"]
            #print(session_token)
            headers['X-Authentication']=session_token
            headers['X-Passphrase']=self.config.sspcm_pasw
            headers['Content-Type']='application/xml'
            headers['Accept']='*/*'
            resp = session.post(self.config.sspcm_base_url+self.config.update_netmap_uri+netmap,headers=headers, data=payload2, verify=False)
            #print(resp.text)
            if resp.status_code==200:
                print(resp.status_code,resp.text)
                return True
            else:
                print(resp.status_code,resp.text)
        return False

if __name__ == '__main__':
    nm = netmap_manager()
    netmap_source=sys.argv[1]
    netmap_dest=sys.argv[2]

    netmap_source_data=nm.get_netmap_details(netmap_source)
    netmap_dest_data=nm.get_netmap_details(netmap_dest)

    source_list1 = {}
    source_list2 = {}

    root = ET.fromstring(netmap_source_data)
    inbound_nodes = root.find('inboundNodes')
    for node in inbound_nodes.findall('inboundNodeDef'):
        name = node.find('name').text
        peer_address = node.find('peerAddressPattern').text
        policy_id = node.find('policyId').text
        policy_id2 = node.find('policyId')
        if policy_id2 is not None:
            policy_id2.text = "SFTP_OKTA"
        node_xml = ET.tostring(node, encoding='unicode')
        source_list1[f'{name}']=node_xml

    root = ET.fromstring(netmap_dest_data)
    inbound_nodes = root.find('inboundNodes')
    for node in inbound_nodes.findall('inboundNodeDef'):
        node_xml = ET.tostring(node, encoding='unicode')
        print(node_xml)
        name = node.find('name').text
        peer_address = node.find('peerAddressPattern').text
        policy_id = node.find('policyId').text
        source_list2[f'{name}']=node_xml

    payload = ''
    for key in source_list1:
        if key in source_list2:
            print(f'Exists {key}')
        else:
            print(f'Adding {key}')
            source_list2[key]=source_list1[key]
            payload = payload + source_list1[key]
    payload='<inboundNodes>'+payload+'</inboundNodes>'
    success = nm.update_netmap_details(netmap_dest,payload)
    if success:
        print('Netmap updated successfully')
    else:
        print('Netmap update failed')