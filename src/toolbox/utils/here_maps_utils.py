import time #To generate the OAuth timestamp
import urllib.parse #To URLencode the parameter string
import hmac #To implement HMAC algorithm
import hashlib #To generate SHA256 digest
from base64 import b64encode #To encode binary data into Base64
import binascii #To convert data into ASCII
import requests #To make HTTP requests

def get_here_maps_access_token(oauth_consumer_key, access_key_secret):

    grant_type = 'client_credentials'
    oauth_nonce = str(int(time.time()*1000))
    oauth_signature_method = 'HMAC-SHA256'
    oauth_timestamp = str(int(time.time()))
    oauth_version = '1.0'

    def create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version):
        parameter_string = ''
        parameter_string = parameter_string + 'grant_type=' + grant_type
        parameter_string = parameter_string + '&oauth_consumer_key=' + oauth_consumer_key
        parameter_string = parameter_string + '&oauth_nonce=' + oauth_nonce
        parameter_string = parameter_string + '&oauth_signature_method=' + oauth_signature_method
        parameter_string = parameter_string + '&oauth_timestamp=' + oauth_timestamp
        parameter_string = parameter_string + '&oauth_version=' + oauth_version
        return parameter_string

    parameter_string = create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version)
    encoded_parameter_string = urllib.parse.quote(parameter_string, safe='') #From credentials.properties file
    oauth_nonce = str(int(time.time()*1000))
    oauth_signature_method = 'HMAC-SHA256'
    oauth_timestamp = str(int(time.time()))
    oauth_version = '1.0'

    def create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version):
        parameter_string = ''
        parameter_string = parameter_string + 'grant_type=' + grant_type
        parameter_string = parameter_string + '&oauth_consumer_key=' + oauth_consumer_key
        parameter_string = parameter_string + '&oauth_nonce=' + oauth_nonce
        parameter_string = parameter_string + '&oauth_signature_method=' + oauth_signature_method
        parameter_string = parameter_string + '&oauth_timestamp=' + oauth_timestamp
        parameter_string = parameter_string + '&oauth_version=' + oauth_version
        return parameter_string

    parameter_string = create_parameter_string(grant_type, oauth_consumer_key,oauth_nonce,oauth_signature_method,oauth_timestamp,oauth_version)
    encoded_parameter_string = urllib.parse.quote(parameter_string, safe='')

    url = 'https://account.api.here.com/oauth2/token'
    encoded_base_string = 'POST' + '&' + urllib.parse.quote(url, safe='')
    encoded_base_string = encoded_base_string + '&' + encoded_parameter_string

    signing_key = access_key_secret + '&'

    def create_signature(secret_key, signature_base_string):
        encoded_string = signature_base_string.encode()
        encoded_key = secret_key.encode()
        temp = hmac.new(encoded_key, encoded_string, hashlib.sha256).hexdigest()
        byte_array = b64encode(binascii.unhexlify(temp))
        return byte_array.decode()

    oauth_signature = create_signature(signing_key, encoded_base_string)
    encoded_oauth_signature = urllib.parse.quote(oauth_signature, safe='')

    body = {'grant_type' : '{}'.format(grant_type)}

    headers = {
        'Content-Type' : 'application/x-www-form-urlencoded',
        'Authorization' : 'OAuth oauth_consumer_key="{0}",oauth_nonce="{1}",oauth_signature="{2}",oauth_signature_method="HMAC-SHA256",oauth_timestamp="{3}",oauth_version="1.0"'.format(oauth_consumer_key,oauth_nonce,encoded_oauth_signature,oauth_timestamp)
    }
        
    response = requests.post(url, data=body, headers=headers)
    access_token = response.json().get('access_token')

    return access_token

###

class RoadDistanceCalculator:
    def __init__(self):
        self.url = "https://matrix.router.hereapi.com/v8/matrix"

    def generate_auth_header(self, access_token):
        headers = {
            'Authorization': f'Bearer {access_token}',
            'Content-Type': 'application/json'
        }
        return headers
    
    def create_job(self, access_token, locations):
        headers = self.generate_auth_header(access_token)
        
        payload = {
            "origins": locations,
            "profile": "truckFast",
            "regionDefinition": {
                "type": "world"
            },
            "matrixAttributes": ["distances"]
        }
        
        response = requests.post(self.url, json=payload,headers=headers)
        data = response.json()
        data = data if type(data) == dict else {}

        matrix_id = data.get("matrixId",None)
        status_url = data.get("statusUrl",None)
        
        return {"matrix_id":matrix_id,"status_url":status_url}

    def get_job_result(self, access_token, status_url):
        
        attempt = 0
        max_attempts = 10
        job_completed = False
        
        headers = self.generate_auth_header(access_token)
        
        distances = None
        while attempt <= max_attempts and not distances:
            response = requests.get(status_url,headers=headers)
            data = response.json()
            distances =  data.get("matrix",{}).get("distances",None)
        
        return distances

def geocode_location(access_token, location):
    url = f"https://geocode.search.hereapi.com/v1/geocode?q={location}"
    headers = {
        'Authorization': f'Bearer {access_token}',
        'Content-Type': 'application/json'
    }
    response = requests.get(url,headers=headers)
    data = response.json()
    # Extract latitude and longitude from the response
    if 'items' in data and len(data['items']) > 0:
        latitude = data['items'][0]['position']['lat']
        longitude = data['items'][0]['position']['lng']
        return latitude, longitude
    return None, None