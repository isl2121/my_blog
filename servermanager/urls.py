from django.urls import path
from django.conf.urls import url
from . import views
from django.views.generic import TemplateView


app_name = 'servermanager'

urlpatterns = [
	url('' , views.index),
]