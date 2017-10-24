#
# Script to extract data from an Azure Serverless Function
# and add it to an AppDynamics Controller as a custom
# Analytics Event. Uses the API documented here:
# https://docs.appdynamics.com/display/PRO42/Analytics+Events+API
#

import requests
import json
import sys
import datetime

# ---------------------------------------------------------------------------
# KEYS FOR ACCESSING BOTH AZURE AND APPDYNAMICS
#

azureApplicationID = ""
azureAPIKey = ""
appDCustomerName = ""
appDAPIKey = ""

# ---------------------------------------------------------------------------
# FUNCTIONS:
#
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
#
# Add a function for time differential
#def time_differential(x,y)
#    out = {}
#

# ---------------------------------------------------------------------------
# PART 1: EXTRACT THE TRACES FROM AZURE SERVERLESS FUNCTIONS
# THIS QUERY EXTRACTS THE TRACES FOR THE LAST 1 HOUR
#
url = 'https://api.applicationinsights.io/beta/apps/' + azureApplicationID + '/events/traces'
headers = {'x-api-key': azureAPIKey, 'Prefer': 'response-v1=true'}
payload = {'timespan': 'PT1H'}
print "Accessing Azure..."
aztraces = requests.get(url, params=payload, headers=headers).json()
print "The Azure traces payload in JSON format:"
#print aztraces
print

# ---------------------------------------------------------------------------
# PART 2: FLATTEN TO 1 LEVEL OF KEY VALUES AND GET KEYS
#
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


        # Change key type
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
                print 'Unhandled type for'
                print key
                print key_type
            key_types[key] = appd_key_type

        # Remove unimportant keys
        if key == 'operation_name':
            print key
        elif key == 'operation_id':
            print key
        elif key == 'trace_message':
            print key
            print flat_trace[key]
            s = flat_trace[key]
            a = s.split("(")
            for b in a:
                if b.endswith(")"): b = b[:-1]
                print b
                if b == "Function completed":
                    flat_trace['trace_functionReturn'] = b
                elif b == "Function started":
                    flat_trace['trace_functionReturn'] = b
                elif b.startswith("Id="):
                    flat_trace['trace_functionId'] = b
                elif b.endswith("ms)"):
                    flat_trace['trace_functionDuration'] = b
                else:
                    flat_trace['trace_functionReturn'] = flat_trace[key]
        elif key == 'customDimensions_LogLevel':
            print key
        elif key == 'operation_parentid':
            print key
        elif key == 'cloud_roleInstance':
            print key
        elif key == 'cloud_roleName':
            print key
        else:
            # print 'removing key because it isn't in the list of targets'
            # print key
            flat_trace.pop(key, None)

# important parts of the Azure Application Insights schema:
# operation_name = The name of the object as shown in the Azure portal.
# operation_id = the unique identifier for a single operation, such as a
#                function execution session, very useful for corrolating the
#                numerous Application Insight lines of data and tracking the
#                execution of a single function execution
# trace_message = this is a string that contains "Function started" or
#                 "Function completed", along with important information that
#                 must be parsed to extract and place into AppDynamics
# trace_severityLevel = Numerical version of one of these: Verbose,
#                       Information, Warning, Error, Critical
# customDimensions_LogLevel = Appears to be the string version of the above
# operation_parentid = the unique identifier for the operation that spawned
#                      this operation, which would be helpful in connecting
#                      the calls between Functions
# cloud_roleInstance = The unique identifier for the "Function apps" instance
#                      within Azure.
# cloud_roleName = The name in the Azure Portal for the "Function apps"
#                  instance. This is essentially a group that can hold multiple
#                  function apps.
#
# Less important parts of the Azure Application Insights schema:
# id = the unique identifier on a per entry basis for Application Insights
#      itself, which isn't very helpful, so this script WON'T import this
#      id into AppDynamics



# ---------------------------------------------------------------------------
# PART 3: FIND EXISTING UNIQUE VALUES THAT ALREADY EXIST IN APPDYNAMICS
#




# ---------------------------------------------------------------------------
# PART : INSERT THE JSON PAYLOAD INTO APPDYNAMICS
#

# print "Accessing AppDynamics..."
# url = 'https://analytics.api.appdynamics.com/events/publish/azureFunctions'
# headers = {'X-Events-API-AccountName': appDCustomerName, 'X-Events-API-Key': appDAPIKey, 'Content-type': 'application/vnd.appd.events+json;v=2'}
# print "Adding data..."
data = json.dumps(outtraces)
# appdtraces = requests.post(url, headers=headers, data=data)
print data
#
# print "Return code:"
# print appdtraces.status_code
# print appdtraces.content
# print
