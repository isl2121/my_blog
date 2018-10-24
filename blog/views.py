from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Article, Tag, Category
from django.shortcuts import get_object_or_404

import logging
logger = logging.getLogger(__name__)


class ArticleListView(ListView):
	#템플릿 이름
	template_name = 'article/article_index.html'
	context_object_name = 'article_list'
	
	page_type = '카테고리'
	paginate_by = 10
	page_kwarg = 'page'
	
	queryset = Article.objects.filter(type='a', status='p')
	
	@property
	def page_number(self):
		page_kwarg = self.page_kwarg
		page = self.kwargs.get(page_kwarg) or self.request.GET.get(page_kwarg) or 1
		return page

class IndexView(ArticleListView):

	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data( **kwargs)
		return context
	

class ArticleDetailView(DetailView):
	template_name = 'blog/article_detail.html'
	model = Article
	pk_url_kwarg = 'article_id'
	context_object_name = 'article'

	def get_object(self, queryset=None):
		obj = super(ArticleDetailView, self).get_object()
		obj.viewd()
		self.object = obj
		return obj
		
	def get_context_data(self, **kwargs):
		articleid = int(self.kwargs[self.pk_url_kwarg])
		comment_from = Commen
		
		
		
	
	
	

def index(request):
	
	return render(request, 'share_layout/base_layout.html' )
	