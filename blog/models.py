import logging
from abc import ABCMeta, abstractmethod, abstractproperty

from django.db import models
from django.urls import reverse
from django.conf import settings
from django.template.defaultfilters import slugify
from django.utils.translation import gettext_lazy as _
from django.utils.timezone import now
from django.contrib.sites.models import Site
from Jin_Blog.utils import cache_decorator, cache
from django.utils.functional import cached_property


# Create your models here.
logger = logging.getLogger(__name__)

class BaseModel(models.Model):
	id = models.AutoField(primary_key=True)
	created_time = models.DateTimeField('등록시간', default=now)
	last_mod_time = models.DateTimeField('변경시간', default=now)
	
	def get_full_url(self):
		site = Site.objects.get_current().domain
		url = 'https://{site}{path}'.format(site,self.get_absolute_url())
		return url
	
	def save(self, *args, **kwargs):
		if not isinstance(self, Article) and 'slug' in self.__dict__:
			if getattr(self, 'slug') == 'no-slug' or not self.id:
				slug = getattr(self, 'title') if 'title' in self.__dict__ else getattr(self, 'name')
				setattr(self, 'slug', slugify(slug))
		super().save(*args, **kwargs)

	@abstractmethod
	def get_absolute_url(self):
		pass

	class Meta:
		abstract = True

class Article(BaseModel):
	
	Article_Status = (
		('d', '대기'),
		('p', '게시'),
	)
	
	Comment_Status = (
		('o', '열기'),
		('c', '닫기'),
	)
	
	Page_Type = (
		('a','일반형'),
		('p','단독/전체페이지'),
	)
	
	title = models.CharField('제목', max_length=200, unique=True)
	body = models.TextField('내용')
	pub_time = models.DateTimeField('게시일', blank=True, null=True)
	status = models.CharField('상태', max_length=1, choices=Article_Status, default='p')
	comment_status = models.CharField('댓글 상태', max_length=1, choices=Comment_Status, default='o')
	type = models.CharField('타입', max_length=1, choices=Page_Type, default='a')

	#Positive = 음수를 사용하지 않을때 사용
	views = models.PositiveIntegerField('조회수', default=0)
	#사용자 삭제시 글 전부 삭제되도록 설정
	author = models.ForeignKey(settings.AUTH_USER_MODEL, verbose_name='글쓴이', on_delete=models.CASCADE)
	category = models.ForeignKey('Category', on_delete=models.CASCADE, blank=False, null=False)
	#article_order = models.Integer('정렬', blank=False,null=False,default=0)
	
	tags = models.ManyToManyField('Tag', blank=True)
	
	def __str__(self):
		return self.title

	class Meta:
		#'-article_order'
		ordering = ['-pub_time']
		get_latest_by='id'
		
		'''
		verbose_name = '블로그 글 작성'
		verbose_name_plural = verbose_name
		'''
	
	def get_absolute_url(self):
		return reverse('blog:detailbyid', kwargs={
			'article_id': self.id,
			'year' : self.created_time.year,
			'month' : self.created_time.month,
			'day' : self.created_time.day
		})
	
	def get_category_tree(self):
		tree = self.category.get_category_tree()
		names = list(map(lambda c: (c.name, c.get_absoulte_url()) ,tree))
		
		return names
	
	def save(self, *args, **kwargs):
		super().save(*args, **kwargs)
	
	def viewed(self):
		self.views += 1
		self.save(update_fields=['views'])
		
	def comment_list(self):
		cache_key = 'article_comments_{id}'.format(id=self.id)
		value = cache.get(cache_key)
		if value:
			logger.info('get article comments:{id}'.format(id=self.id))
			return value
		else:
			comments = self.comment_set.filter(is_enable=True)
			cache.set(cache_key, comments)
			logger.info('set article comments:{id}'.format(id=self.id))
			return comments

	def get_admin_url(self):
		info = (self._meta.app_label, self._meta.model_name)
		return reverse('admin:{info}_{pk}_change'.format(info,args=(self.pk,)))
	
	@cached_property
	def next_article(self):
		#__gt = self.id 보다 1큰자료 검색
		return Article.objects.filter(id__gt=self.id, status='p').order_by('id').first()
		
	@cached_property
	def prev_article(self):
		#__lt = self.id 보다 1큰자료 검색
		return Article.objects.filter(id__lt=self.id, status='p').first()


class Category(BaseModel):
	name = models.CharField('분류명', max_length = 30, unique=True)
	parent_category = models.ForeignKey('self', verbose_name='선분류 카테고리', blank=True, null=True, on_delete=models.CASCADE)
	slug = models.SlugField(default='no-slug', max_length=60, blank=True)
	
	class Meta:
		ordering = ['name']
		verbose_name = 'category'
		verbose_name_plural = verbose_name

	
	def get_absolute_url(self):
		return reverse('blog:category_detail', kwargs={'category_name': self.slug})

	def __str__(self):
		return self.name


	def get_category_tree(self):
		category = []
		
		def parse(category):
			category.append(category)
			if category.parent_category:
				parse(category.parent_category)
		
		parse(self)
		return category

	def get_sub_categorys(self):
		categorys = []
		all_categorys = Category.objects.all()

		def parse(category):
			if category not in categorys:
				categorys.append(category)
			childs = all_categorys.filter(parent_category=category)
			for child in childs:
				if category not in categorys:
					categorys.append(child)
				parse(child)
				
		parse(self)
		return categorys

class Tag(BaseModel):
	name = models.CharField('Tag', max_length=30, unique=True)
	slug = models.SlugField(default='no-slug', max_length=60, blank=True)
	
	def __str__(self):
		return self.name
	
	def get_absolute_url(self):
		return reverse('blog:tag_detail', kwargs={'tag_name':self.slug})
	
	def get_article_count(self):
		return Article.objects.filter(tags__name=self.name).distinct().count()
	
	class Meta:	
		ordering = ['name']
		verbose_name = 'Tag'
		verbose_name_plural = verbose_name

class SideBar(models.Model):
	name = models.CharField('이름', max_length=30,unique=True)
	content = models.TextField('내용')
	sequence = models.IntegerField('정렬',unique=True)
	is_enable = models.BooleanField('사용여부', default=True)
	created_time = models.DateTimeField('등록시간', default=now)
	last_mod_time = models.DateTimeField('변경시간',default=now)
	
	class Meta:
		ordering = ['sequence']
		verbose_name = 'Sidebar'
		verbose_name_plural = verbose_name
	
	def __str__(self):
		return self.name

class BlogSettings(models.Model):
	sitename = models.CharField('사이트명', max_length=200, null=False, blank=False, default='My Blog')
	site_description = models.TextField('사이트 설명', max_length=1000,null=False,blank=False, default='Hello this is My Blog')
	site_keywords = models.TextField('사이트키워드', max_length=1000, null=False, blank=False, default='Blog')
	article_sub_length = models.IntegerField('글길이 제한',default=300)	
	sidebar_article_count = models.IntegerField('사이드바 글 수',default=10)
	sidebar_comment_count = models.IntegerField('사이드바 댓글수',default=5)
	open_site_comment = models.BooleanField('사이트 댓글 설정', default = True)
	show_google_adsense = models.BooleanField('구글광고설정', default=False)
	google_adsense_codes = models.TextField('구글에드센스 코드',max_length=2000, null=True, blank=True, default='')
	show_analytics = models.BooleanField('아날리틱스 설정', default=True)
	analyticscode = models.TextField('Analytics Code', max_length=1000, null=True, blank=True)
	resource_path = models.CharField('리소스 파일', max_length=300,null=False, default='/var/www/resource/')
	
	class Meta:
		verbose_name = 'Blog Settings'
		verbose_name_plural = verbose_name
	
	def __str__(self):
		return self.sitename
	
	def clean(self):
		if BlogSettings.objects.exclude(id=self.id).count():
			raise ValidationError(_('블로그 설정은 하나만 가능합니다.'))
	
	def save(self, *args, **kwargs):
		super().save(*args,**kwargs)
		from Jin_Blog.utils import cache
		cache.clear()
