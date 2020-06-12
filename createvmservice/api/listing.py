from flask import Flask, abort, request
from flask_restful import Resource, Api
from api.config import readCfg 
from api.config.readCfg import read_config
import json
from flask_restplus import Api, Resource, fields
from flask_httpauth import HTTPBasicAuth
from werkzeug.security import generate_password_hash, check_password_hash
import requests
from kubernetes import client, config
config = read_config(['api/config/local.properties'])

app = Flask(__name__)
api = Api(app, version='1.0', title='Kubevirt',
    description='Kubevirt Microservice Framework',
)

apiuser=config.get('dev','api.u')
p=config.get('dev','api.p')
auth = HTTPBasicAuth()
apiserver = config.get('dev','api_server')
token = config.get('dev','token')

users = {
    apiuser : generate_password_hash(p)
}


@auth.verify_password
def verify_password(username, password):
    if username in users:
        return check_password_hash(users.get(username), password)
    return False



class Dashboard(Resource):
    @auth.login_required
    
    def get(self):
        input_file = open ('api/config/dashboard.json')
        json_array = json.load(input_file)
        print(json_array)
        return json_array

class KeepAlive(Resource):

    def get(self):
        return "OK"

class GetVM(Resource):
    #Just a method to get matching values for given key in json
    def get_all(self, myjson, key):
        tst = []
        if type(myjson) == str:
          myjson = json.loads(myjson)
        if type(myjson) is dict:
          for jsonkey in myjson:
              if type(myjson[jsonkey]) in (list, dict):
                  self.get_all(myjson[jsonkey], key)
              elif jsonkey == key:
                  tst.append(myjson[jsonkey])
                  #print(tst)
                  #return tst
        elif type(myjson) is list:
          for item in myjson:
              if type(item) in (list, dict):
                  self.get_all(item, key)
        return tst
    
    def get(self):
        url = apiserver+'/apis/kubevirt.io/v1alpha3/namespaces/virtual-machines/virtualmachineinstances/'
        header= {
            'content-type': 'json',
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkZFRVhoRUFTb0xkM1o3Mi1aUGtEOHhwYlZJMlctLXFDbWY4OVRQNW4zVDgifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLXRqa3RmIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIwYTk5ZmYwNy0xZjhlLTRmN2EtOGQ4YS1iZGFjN2U3MzA4ZTUiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06YWRtaW4tdXNlciJ9.DtHk0Q9BgJ6epX75_uVR5lNQNz35pyoLPpVhmkwwRkk-rY5UqjTJGQAhRu3I04iQ6Od2amuU5IQrAjPRaaRS6jBQr0wTL9dHCpQRBcu1xe9nRG4_y35LStUagnTaB95s94j3lwa5ouH5JRJFHSq7WGIqyLOJTmYeE_NpHMgWBuQ-sTtFjaEK1HkYFpxSSnpcvIWf7IuAnjO2LhnmXACtVV0sOmNkzqMSTfB1N1vJl1R2C8hkVCcS262OAgC4VMFpYS35IVuzZGduoo0gbU-qvVtaavzaP_UBBsjYrgX8KxK7usR1pRxF0PpVITmx1XIVuFU4JNpp2EJQ9ki2PrluGg'
            }
        response = requests.get(url,headers=header, verify=False).json()
        result = self.get_all(response, "name")
        res = []
        print(response['items'])
        for i in response['items']:
              res.append(i)
        return res

class CreateVM(Resource):

    def post(self):
        
        header= {
            'content-type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJSUzI1NiIsImtpZCI6IkZFRVhoRUFTb0xkM1o3Mi1aUGtEOHhwYlZJMlctLXFDbWY4OVRQNW4zVDgifQ.eyJpc3MiOiJrdWJlcm5ldGVzL3NlcnZpY2VhY2NvdW50Iiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9uYW1lc3BhY2UiOiJrdWJlLXN5c3RlbSIsImt1YmVybmV0ZXMuaW8vc2VydmljZWFjY291bnQvc2VjcmV0Lm5hbWUiOiJhZG1pbi11c2VyLXRva2VuLXRqa3RmIiwia3ViZXJuZXRlcy5pby9zZXJ2aWNlYWNjb3VudC9zZXJ2aWNlLWFjY291bnQubmFtZSI6ImFkbWluLXVzZXIiLCJrdWJlcm5ldGVzLmlvL3NlcnZpY2VhY2NvdW50L3NlcnZpY2UtYWNjb3VudC51aWQiOiIwYTk5ZmYwNy0xZjhlLTRmN2EtOGQ4YS1iZGFjN2U3MzA4ZTUiLCJzdWIiOiJzeXN0ZW06c2VydmljZWFjY291bnQ6a3ViZS1zeXN0ZW06YWRtaW4tdXNlciJ9.DtHk0Q9BgJ6epX75_uVR5lNQNz35pyoLPpVhmkwwRkk-rY5UqjTJGQAhRu3I04iQ6Od2amuU5IQrAjPRaaRS6jBQr0wTL9dHCpQRBcu1xe9nRG4_y35LStUagnTaB95s94j3lwa5ouH5JRJFHSq7WGIqyLOJTmYeE_NpHMgWBuQ-sTtFjaEK1HkYFpxSSnpcvIWf7IuAnjO2LhnmXACtVV0sOmNkzqMSTfB1N1vJl1R2C8hkVCcS262OAgC4VMFpYS35IVuzZGduoo0gbU-qvVtaavzaP_UBBsjYrgX8KxK7usR1pRxF0PpVITmx1XIVuFU4JNpp2EJQ9ki2PrluGg'
            }
        url = apiserver+'/apis/kubevirt.io/v1alpha3/namespaces/default/virtualmachines'
        vm_body = {
  "apiVersion": "kubevirt.io/v1alpha3",
  "kind": "VirtualMachine",
  "metadata": {
    "labels": {
      "kubevirt.io/vm": "vm-cirros"
    },
    "name": "vm-cirros"
  },
  "spec": {
    "running": False,
    "template": {
      "metadata": {
        "labels": {
          "kubevirt.io/vm": "vm-cirros"
        }
      },
      "spec": {
        "domain": {
          "devices": {
            "disks": [
              {
                "disk": {
                  "bus": "virtio"
                },
                "name": "containerdisk"
              },
              {
                "disk": {
                  "bus": "virtio"
                },
                "name": "cloudinitdisk"
              }
            ]
          },
          "machine": {
            "type": ""
          },
          "resources": {
            "requests": {
              "memory": "64M"
            }
          }
        },
        "terminationGracePeriodSeconds": 0,
        "volumes": [
          {
            "containerDisk": {
              "image": "registry:5000/kubevirt/cirros-container-disk-demo:devel"
            },
            "name": "containerdisk"
          },
          {
            "cloudInitNoCloud": {
              "userData": "#!/bin/sh\n\necho 'printed from cloud-init userdata'\n"
            },
            "name": "cloudinitdisk"
          }
        ]
      }
    }
  }
}
        res = requests.post(url,headers=header, json=vm_body, verify=False ).json()
        return res
        



api.add_resource(Dashboard, '/dashboard')
api.add_resource(KeepAlive, '/keepalive')
api.add_resource(CreateVM, '/createvm')
api.add_resource(GetVM, '/getvm')