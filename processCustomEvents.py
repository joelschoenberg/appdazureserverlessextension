#

# Script to extract data from an Azure Serverless Function
# and add it to an AppDynamics Controller as a custom
# Analytics Event. Uses the API documented here:
# https://docs.appdynamics.com/display/PRO42/Analytics+Events+API
#
# This script is broken into three parts:
# 1. Extract the data from Azure Serverless Functions
#    - assumes you have configured Application Insights for your function
# 2. Manipulate the data to form an AppDynamics Schema
#
# 3. Insert the payload from that extraction into appdynamics
#    - assumes you have a controller with an Event cluster (see docs)




# ---------------------------------------------------------------------------
# PART 1: EXTRACT THE DATA FROM AZURE SERVERLESS FUNCTIONS
# TODO: parameterize these sensitive bits of data
# My application ID: 06e7e052-76e6-467a-9e1d-44bdfcdb71ad
# My API Key: 2ld7ms8jngjh76qpim0n7uiri0dxfl6feeghqcsq
#
# CURL TO GET AZURE METRICS
# curl "https://api.applicationinsights.io/beta/apps/06e7e052-76e6-467a-9e1d-44bdfcdb71ad/metrics/requests/count?timespan=PT12H&aggregation=sum" -H "x-api-key: 2ld7ms8jngjh76qpim0n7uiri0dxfl6feeghqcsq" -H "Prefer: response-v1=true"
#
# HTTP REQUEST TO GET AZURE METRICS
# GET "/beta/apps/06e7e052-76e6-467a-9e1d-44bdfcdb71ad/metrics/requests/count?timespan=PT12H&aggregation=sum" HTTP/1.1
# Host: api.applicationinsights.io
# x-api-key: 2ld7ms8jngjh76qpim0n7uiri0dxfl6feeghqcsq
# Prefer: response-v1=true

# I'm using the requests python module for ease of use
# And the JSON module to manipulate and merge the data
import requests
import json

# This query gets the COUNT of REQUESTS of my Azure Serverless Function, over the last 12 hours
applicationid = '06e7e052-76e6-467a-9e1d-44bdfcdb71ad'
url = 'https://api.applicationinsights.io/beta/apps/06e7e052-76e6-467a-9e1d-44bdfcdb71ad/metrics/requests/count'
headers = {'x-api-key': '2ld7ms8jngjh76qpim0n7uiri0dxfl6feeghqcsq', 'Prefer': 'response-v1=true'}
payload = {'timespan': 'PT12H'}
# TODO: make script parameters for other key metrics from Azure Application Insights, such as:
# /requests/duration
# /requests/failed
# pageViews/count
# pageViews/duration
# browserTimings/networkDuration
# browserTimings/sendDuration
# browserTimings/receiveDuration
# browserTimings/processingDuration
# browserTimings/totalDuration
# performanceCounters/requestExecutionTime
# performanceCounters/requestsPerSecond
# performanceCounters/
# performanceCounters/
# performanceCounters/
# performanceCounters/
# Each of these data points have a default parameter for:
# timespan, which is the
# interval, which breaks down the total into intervals
# aggregation, which performs a logical operation on the data, such as sum or avg

# Execute and print the GET with params and header in URL
az = requests.get(url, params=payload, headers=headers)
print "Accessing Azure..."
print "The Azure content payload in JSON format:"
print az.content
print "Return code:"
print az.status_code
print

# ---------------------------------------------------------------------------
# PART 2: Manipulate the JSON output from Azure and build new JSON for AppD
#
print "Converting JSON to Python Dictionary for flat access..."
jsonToPython = json.loads(az.content)
print jsonToPython
print "Flattened value:"
customMetric = jsonToPython['value']['requests/count']['sum']
print jsonToPython['value']['requests/count']['sum']
print customMetric

# ---------------------------------------------------------------------------
# PART 3: INSERT THE JSON PAYLOAD INTO APPDYNAMICS
# TODO: Parameterize this sensitive information
# My Analytics API key for 43 enablement controller
# 502c4052-9d55-4872-9d3d-4ea3e6784a25
# New Analytics API Key that does not include Transaction access
# 58cea969-3536-4950-b0b6-753ffeae8e64
# My Analytics API key with everything
# 50c4c457-d91a-44b6-a6e1-437d1f35e50a

# My Account name for 43 enablement controller
# customer1

# My Global Account name
# customer1_b7686ddf-6680-43f3-bbeb-303c027344e2

# My API Key
# ff11d48d-37ac-4c41-ad9e-11554aa65216

# Hybrid EUM account
# test-eum-account-joelschoenberg-1507682182576

# EUM License key
# 980b2e1b-e2cf-4069-830b-4f8d8456374b

# PART 3A: CREATE THE SCHEMA FOR THE COUNT OF REQUESTS FOR MY SERVERLESS FUNCTION
#
url = 'http://34.210.157.84:9080/events/schema/azureFunctions'
headers = {'X-Events-API-AccountName': 'customer1_b7686ddf-6680-43f3-bbeb-303c027344e2', 'X-Events-API-Key': '50c4c457-d91a-44b6-a6e1-437d1f35e50a', 'Content-type': 'application/vnd.appd.events+json;v=1'}
data = '{"schema": { "id": "string", "metricName": "string", "count": "integer" }}'
appdschema = requests.post(url, headers=headers, data=data)
print "Accessing AppDynamics..."
print "Creating schema..."
print "Return code:"
print appdschema.status_code
print

# PART 3B: ADD THE DATA FROM APPLICATION INSIGHTS INTO appd
#
url = 'http://34.210.157.84:9080/events/schema/azureFunctions'
headers = {'X-Events-API-AccountName': 'customer1_b7686ddf-6680-43f3-bbeb-303c027344e2', 'X-Events-API-Key': '50c4c457-d91a-44b6-a6e1-437d1f35e50a', 'Content-type': 'application/vnd.appd.events+json;v=1'}
data = {"id": "06e7e052-76e6-467a-9e1d-44bdfcdb71ad", "metricName": "requests/count", "count": + customMetric}
appddata = requests.post(url, headers=headers, data=data)
print "Accessing AppDynamics..."
print "Adding data..."
print appddata.content
print "Return code:"
print appddata.status_code
print
