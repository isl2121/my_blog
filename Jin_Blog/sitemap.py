from django.contrib.sitemaps import Sitemap
from blog.models import Article, Category, Tag
from django.urls import reverse

class StaticViewSitemap(Sitemap):
	priority = 0.5
	changefreq = 'daily'
	
	def items(self):
		return ['blog:index',]
	
	def location(self, item):
		return reverse(item)

class ArticleSiteMap(Sitemap):
	changefreq = 'monthly'
	priority = '0.6'
	
	def items(self):
		return Article.objects.filter(status='p')
	
	def lastmod(self, obj):
		return obj.last_mod_time

class CategorySiteMap(Sitemap):
	changefreq = 'Weekly'
	priority = '0.6'
	
	def itmes(self):
		return Category.objects.all()
	
	def lastmod(self, obj):
		return obj.last_mod_time

class TagSiteMap(Sitemap):
	chagefreq = 'Weekly'
	priority = '0.3'
	
	def items(self):
		return Tag.objects.all()
	
	def lastmod(self, obj):
		return obj.last_mod_time