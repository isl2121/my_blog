from django.db import models

# Create your models here.
class EmailSendLog(models.Model):
	sender = models.CharField('발신인', max_length=200)
	receiver = models.CharField('수신인', max_length=200)
	title = models.CharField('제목', max_length=300)
	content = models.TextField('내용')
	send_result = models.BooleanField('결과', default=False)
	created_time = models.DateTimeField('등록시간', auto_now_add=True)
	
	def __str__(self):
		return self.title
	
	class Meta:
		verbose_name = 'EmailSend Log'
		verbose_name_plural = verbose_name
		ordering = ['-created_time']