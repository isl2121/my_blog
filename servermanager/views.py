from django.shortcuts import render
from django.contrib.auth.models import User, Group
import httplib2
import os
import json
from oauth2client.client import SignedJwtAssertionCredentials
from os.path import join, getsize


import logging
logger = logging.getLogger(__name__)

#pip install oauth2client==1.5.2
#https://ga-dev-tools.appspot.com/account-explorer/

from django import template


register = template.Library()

def index(request):

	logger.error(request.user.get_username())
	
	if request.user.get_username() not in ['admin','dev_admin']:
		template_name='blog/error_page.html'
		return render(request, template_name, {'error_description': '500 Error', 'statuscode': '403', 'comment': '서버에 접근할 권한이 없습니다.'}, status=403)
	
	ANALYTICS_CREDENTIALS_JSON = os.path.join(os.path.dirname(__file__),'./analytics.json')
	ANALYTICS_VIEW_ID = '184256714'
 
    # The scope for the OAuth2 request.
	SCOPE = 'https://www.googleapis.com/auth/analytics.readonly'
 
    # The location of the key file with the key data.
	KEY_FILEPATH = ANALYTICS_CREDENTIALS_JSON
 
    # Load the key file's private data.
	with open(KEY_FILEPATH) as key_file:
		_key_data = json.load(key_file)
 
	_credentials = SignedJwtAssertionCredentials(_key_data['client_email'], _key_data['private_key'], SCOPE)
    
	context = {
		'token': _credentials.get_access_token().access_token,
		'view_id': ANALYTICS_VIEW_ID,
	}
	print(context)
	return render(request, 'servermanager/index.html', context)



