#
# Script to extract data from an Azure Serverless Function
# and add it to an AppDynamics Controller as a custom
# Analytics Event. Uses the API documented here:
# https://docs.appdynamics.com/display/PRO42/Analytics+Events+API
#
# 3. Extract the data from Azure Serverless Functions
# 4. Insert the payload from that extraction into AppDynamics
#    - assumes you have a controller with an Event cluster (see docs)
import requests
import json
import sys
# ---------------------------------------------------------------------------

def flatten_json(y):
    out = {}
    
    def flatten(x, name=''):
        if type(x) is dict:
            for a in x:
                flatten(x[a], name + a + '_')
        elif type(x) is list:
            i = 0
            for a in x:
                flatten(a, name + str(i) + '_')
                i += 1
        else:
            out[name[:-1]] = x

    flatten(y)
    return out

# Keys
azureApplicationID =
azureAPIKey =
appDCustomerName =
appDAPIKey =

# ---------------------------------------------------------------------------
# PART 1: EXTRACT THE TRACES FROM AZURE SERVERLESS FUNCTIONS
#
# THIS QUERY EXTRACTS THE TRACES FOR THE LAST 1 HOUR
#
url = 'https://api.applicationinsights.io/beta/apps/' + azureApplicationID + '/events/traces'
headers = {'x-api-key': azureAPIKey, 'Prefer': 'response-v1=true'}
payload = {'timespan': 'PT1H'}
print "Accessing Azure..."
aztraces = requests.get(url, params=payload, headers=headers).json()
print "The Azure traces payload in JSON format:"
print aztraces
print

# PART 2: FLATTEN TO 1 LEVEL OF KEY VALUES AND GET KEYS
outtraces = []
key_types = dict()
for trace in aztraces['value']:
    flat_trace = flatten_json(trace)
    outtraces.append(flat_trace)
    for key in flat_trace.keys():
        # Remove { and } from key
        value = flat_trace.pop(key)
        key = key.replace('{', '')
        key = key.replace('}', '')
        flat_trace[key] = value
        # Create Key Set
        if not key_types.has_key(key):
            key_type = type(flat_trace[key])
            appd_key_type = ''
            if key == 'timestamp':
                appd_key_type = 'date'
            elif key_type == type(None):
                appd_key_type = 'string'
            elif key_type == type(u'unicode'):
                appd_key_type = 'string'
            elif key_type == type(1):
                appd_key_type = 'integer'
            else:
                print 'Unhanled type for'
                print key
                print key_type
            key_types[key] = appd_key_type

# ---------------------------------------------------------------------------
# PART 3: INSERT THE JSON PAYLOAD INTO APPDYNAMICS
#

print "Accessing AppDynamics..."
url = 'https://analytics.api.appdynamics.com/events/publish/azureFunctions'
headers = {'X-Events-API-AccountName': appDCustomerName, 'X-Events-API-Key': appDAPIKey, 'Content-type': 'application/vnd.appd.events+json;v=2'}
print "Adding data..."
data = json.dumps(outtraces)
appdtraces = requests.post(url, headers=headers, data=data)
print "Return code:"
print appdtraces.status_code
print appdtraces.content
print
