from django.core.cache import cache
from hashlib import md5
from django.conf import settings
import logging

logger = logging.getLogger(__name__)



def get_md5(str):
	m = md5(str.encode('utf-8'))
	return m.hexdigest()

def cache_decorator(expiration=3*60):
	def wrapper(func):
		def news(*args,**kwargs):
			key = ''
			try:
				view = args[0]
				key = view.get_cache_key()
			except:
				key = None
				pass
			if not key:
				unique_str = repr((func, args, kwargs))
				m = md5(unique_str.encode('utf-8'))
				key = m.hexdigest()
			value = cache.get(key)
			if value:
				logger.info('cache_decorator get cache:%s key:%s' %(func.__name__,key))
				return value
			else:
				logger.info('cache_decorator set cache:%s key:%s') %(func.__name__,key)
				value = func(*args,**kwargs)
				cache.set(key,value,expiration)
				return value
				
		return news
		
	return wrapper


def get_blog_setting():
    from blog.models import BlogSettings
    if not BlogSettings.objects.count():
        setting = BlogSettings()
        setting.sitename = 'Blog'
        setting.site_description = 'Hello this is my Blog'
        setting.site_keywords = 'Django,Python'
        setting.article_sub_length = 300
        setting.sidebar_article_count = 10
        setting.sidebar_comment_count = 5
        setting.show_google_adsense = False
        setting.open_site_comment = True
        setting.analyticscode = ''
        setting.save()
    value = BlogSettings.objects.first()
    return value
