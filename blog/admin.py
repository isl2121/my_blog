from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from blog.models import Article, Category, Tag, SideBar, BlogSettings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils.html import format_html
# Register your models here.

class ArticleListFilter(admin.SimpleListFilter):
	title = _('제목')
	parameter_name = 'author'
	
	def lookups(self, request, model_admin):
		authors = list(set(map(lambda x: x.author, Article.objects.all())))
		for author in authors:
			yield(author.id, _(author.username))
	
	def queryset(self, request, queryset):
		id = self.value()
		if id:
			return queryset.filter(author__id__exact=id)
		else:
			return queryset

def close_article_comment_status(modeladmin, request, queryset):
	queryset.update(comment_status='c')

def open_article_comment_status(modeladmin, request, queryset):
	queryset.update(comment_open='o')

def article_publish(modeladmin, request, queryset):
	queryset.update(comment_status='p')

def article_tmp_save(modeladmin, request, queryset):
	queryset.update(comment_status='d')

article_publish.short_description = _('글 게시하기')
article_tmp_save.short_description = _('임시저장')
close_article_comment_status.short_description = _('댓글 잠그기')
open_article_comment_status.short_description = _('댓글 열기')

class ArticleAdmin(admin.ModelAdmin):
	list_per_page = 20
	search_filter = ('body','title')
	list_display = ( 'id', 'title','author', 'link_to_category', 'created_time', 'views', 'status', 'type')
	list_display_links = ('id', 'title')
	list_filter = (ArticleListFilter, 'status', 'type', 'category', 'tags')
	filter_horizontal = ('tags',)
	exclude = ('created_time', 'last_mod_time')
	view_on_site = True
	actions = [close_article_comment_status, open_article_comment_status, article_publish, article_tmp_save]
	
	def link_to_category(self, obj):
		info = (obj.category._meta.app_label, obj.category._meta.model_name)
		link = reverse('admin:%s_%s_change' % info, args=(obj.category.id,))
		return format_html(u'<a href="%s">%s</a>'% (link,obj.category.name))
	
	link_to_category.short_description = _('분류목록')	

class TagAdmin(admin.ModelAdmin):
	exclude = ('slug', 'last_mod_time', 'created_time')

class SideBarAdmin(admin.ModelAdmin):
	list_display = ('name', 'content', 'is_enable', 'sequence')
	exclude = ('last_mod_time', 'created_time')

class CategoryAdmin(admin.ModelAdmin):
	exclude = ('slug', 'last_mod_time', 'created_time')

class BlogSettingAdmin(admin.ModelAdmin):
	pass

admin.site.register(Article, ArticleAdmin)
admin.site.register(Category, CategoryAdmin)
admin.site.register(Tag, TagAdmin)
admin.site.register(SideBar, SideBarAdmin)
admin.site.register(BlogSettings, BlogSettingAdmin)