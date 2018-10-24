
from django.urls import path
from . import views


app_name = 'blog'
urlpatterns = [
	path(r'', views.IndexView.as_view(), name='index'),
    path(r'page/<int:page>/', views.IndexView.as_view(), name='index_page'),
	
]