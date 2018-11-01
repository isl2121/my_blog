from django.shortcuts import render
from django.contrib.auth.models import User, Group
import httplib2
import os

from apiclient.discovery import build
from oauth2client.service_account import ServiceAccountCredentials



def index(request):
	print(os.path.dirname(__file__))
	if request.user.get_username() != 'admin':
		template_name='blog/error_page.html'
		return render(request, template_name, {'error_description': '500 Error', 'statuscode': '403', 'comment': '서버에 접근할 권한이 없습니다.'}, status=403)
	
	get_ga_metrics()
	
	return render(request, 'servermanager/index.html')


def get_ga_metrics(medium=['ad'], source=['facebook']):
	# Remember the JSON file you downloaded? We will use it now
	# for an ouath2 authentication. Be sure it's available on this
	# path.
	credentials = ServiceAccountCredentials.from_json_keyfile_name(
		os.path.join(os.path.dirname(__file__),'./analytics.json'),'https://www.googleapis.com/auth/analytics.readonly',
	)
	http = credentials.authorize(httplib2.Http())
	
	# The URL of the discovery service.
	DISCOVERY_URI = (
		'https://analyticsreporting.googleapis.com/$discovery/rest')
    # Now we build the API connection. In that case we want to call 
    # the 'analytics' API version 4.
	analytics = build(
		'analytics', 'v4', http=http, 
		discoveryServiceUrl=DISCOVERY_URI)
		# Next we define the query we want to send to the API. There
		# are plenty of options. Link below. 
	reports = analytics.reports().batchGet(
		body={
			'reportRequests': [
				{
					# The ID of your Analytics View. Cannot find it?
					# Instructions below.
					'viewId': '128399791',
					#'dateRanges': [
					#	{
					#		'startDate': '2017-01-01',
					#		'endDate': '2017-12-31',
					#	},
					#],
					
					'metrics': [
						# This is where you define the data you want
						# to receive. Link below. In this case I 
						# want the sessions count and the conversion 
						# rate
						{'expression': 'ga:sessions'},
						{'expression': 'ga:transactionsPerVisit'},
					],
					'dimensions': [
						# Session attributes. We want to use our utm 
						# parameters, but you can also look for the
						# user's country etc.
						{'name': 'ga:medium'},
						{'name': 'ga:source'},
					],
					"dimensionFilterClauses": [
						# Let's add some filters for the Facebook
						# ad campaign
						{
							"filters": [
							    {
									"dimensionName": 'ga:medium',
									"operator": 'EXACT',
									"expressions": medium,
								},
								{
									"dimensionName": 'ga:source',
									"operator": 'EXACT',
									"expressions": source,
							    },
							],
						}
		            ],
		        }]
		}
	).execute()
    
    # Google returns a huge dict. Let's extract all infos we need
	metrics = {}
	for row in reports['reports'][0]['data'].get('rows', []):
		metrics[row['dimensions'][1]] = {
			'sessions': row['metrics'][0]['values'][0],
			'conversion_rate': row['metrics'][0]['values'][1],
		}

	return metrics