from django.contrib import admin

from .models import EmailSendLog

class EmailSEndLogAdmin(admin.ModelAdmin):
	list_display = ('title', 'sender','receiver', 'send_result', 'created_time')
	readonly_fields = ('title', 'sender','receiver', 'send_result', 'created_time')

	def has_add_permission(self, request):
		return False

admin.site.register(EmailSendLog, EmailSEndLogAdmin)