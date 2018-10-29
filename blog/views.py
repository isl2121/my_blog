from django.shortcuts import render
from django.views.generic import ListView, DetailView
from django.core.paginator import Paginator
from Jin_Blog.utils import custom_paginator
from .models import Article, Tag, Category
from django.shortcuts import get_object_or_404
from django.db.models import Q

import logging
logger = logging.getLogger(__name__)


class ArticleListView(ListView):
	#템플릿 이름
	template_name = 'blog/article_index.html'
	context_object_name = 'article_list'
	
	page_type = '카테고리'
	page_kwarg = 'page'
	
	paginate_by = 3
	page_numbers_range = 5
	
	queryset = ''
	
	def page_number(self):
		page = self.request.GET.get("page")
		current_page = int(page) if page else 1
		return current_page
	
	def get_queryset_data(self):
		raise NotImplementedError()
        
	def get_queryset(self):
		queryset = self.get_queryset_data()
		return queryset

class CategoryDetailView(ArticleListView):
	
	def get_queryset_data(self):
		slug = self.kwargs['category_name']
		category = get_object_or_404(Category, slug=slug)
		
		categoryname = category.name
		self.categoryname = categoryname

		categorynames = list(map(lambda c: c.name, category.get_sub_categorys()))
		article_list = Article.objects.filter(category__name__in=categorynames, status='p')
		return article_list

	def get_context_data(self, **kwargs):
		context = super(CategoryDetailView, self).get_context_data(**kwargs)
		
		categoryname = self.categoryname
		try:
			categoryname = categoryname.split('/')[-1]
		except:
			pass
		
		context['all_tags'] = Tag.objects.all()
		context['page_type'] = CategoryDetailView.page_type
		context['page_range'] = custom_paginator(context['paginator'], context['page_obj'], 5)
		context['tag_name'] = categoryname
		
		return context

class IndexView(ArticleListView):

	def get_queryset_data(self):
		
		if 'search' in self.kwargs:
			search = self.kwargs['search']
			article_list = Article.objects.filter(Q(body__icontains=search) | Q(title__icontains=search), type='a', status='p')
		else:
			article_list = Article.objects.filter(type='a', status='p')
		
		return article_list
	
	def get_context_data(self, **kwargs):
		context = super(IndexView, self).get_context_data( **kwargs)
		context['all_tags'] = Tag.objects.all()
		context['page_range'] = custom_paginator(context['paginator'], context['page_obj'], 5)
		
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
		self.name = tag_name
		article_list = Article.objects.filter(tags__name=tag_name)
		return article_list

	def get_context_data(self, **kwargs):
		context = super(TagDetailView,self).get_context_data(**kwargs)
		
		context['page_type'] = TagDetailView.page_type
		context['tag_name'] = self.name
		context['all_tags'] = Tag.objects.all()
		context['page_range'] = custom_paginator(context['paginator'], context['page_obj'], 5)
		return context


def page_not_found_view(request, exception, template_name='blog/error_page.html'):
	if exception:
		logger.error(exception)
	url = request.get_full_path()
	return render(request, template_name, {'error-description': '404 NotFound', 'statuscode': '404', 'comment': '페이지를 찾을수 없습니다.'}, status=404)


def server_error_view(request, template_name='blog/error_page.html'):
	return render(request, template_name, {'error-description': 'Permission Denied', 'statuscode': '500', 'comment': '서버에 접속할수 없습니다.'}, status=500)


def permission_denied_view(request, exception, template_name='blog/error_page.html'):
	if exception:
		logger.error(exception)
	return render(request, template_name, {'error-description': '500 Error', 'statuscode': '403', 'comment': '서버에 접근할 권한이 없습니다.'}, status=403)

