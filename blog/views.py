from django.shortcuts import render
from django.views.generic import ListView, DetailView

from .models import Article, Tag, Category
from django.shortcuts import get_object_or_404


import logging
logger = logging.getLogger(__name__)


class ArticleListView(ListView):
	#템플릿 이름
	template_name = 'blog/article_index.html'
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
		context['all_tags'] = Tag.objects.all()
		return context
	

class ArticleDetailView(DetailView):
	template_name = 'blog/article_detail.html'
	model = Article
	pk_url_kwarg = 'article_id'
	context_object_name = 'article'
		
	def get_object(self, queryset=None):
		obj = super(ArticleDetailView, self).get_object()
		obj.viewed()
		self.object = obj
		return obj
	
	def get_context_data(self, **kwargs):
		context = super(ArticleDetailView, self).get_context_data(**kwargs)
		
		context['next_article'] = self.object.next_article
		context['prev_article'] = self.object.prev_article
		
		return context

class TagListView(ListView):
	template_name = ''
	context_object_name = 'tag_list'
	
	def get_queryset(self):
		tags_list = []
		tags = Tag.object.all()
		for t in tags:
			t.article_set.count()

class TagDetailView(ArticleListView):
	
	page_type = '태그목록'
	name = ''
	
	def get_queryset_data(self):
		slug = self.kwargs['tag_name']
		tag = get_object_or_404(Tag, slug=slug)
		tag_name = tag.name
		print(tag_name)
		
		self.name = tag_name
		article_list = Article.objects.filter(tags__name=tag_name)
		return article_list

	def get_context_data(self, **kwargs):
		print('here --------------------------')
		tag_name = self.name
		kwargs['page_type'] = TagDetailView.page_type
		kwargs['tag_name'] = tag_name
		return super(TagDetailView, self).get_context_data(**kwargs)


def index(request):
	
	return render(request, 'share_layout/base_layout.html' )
	