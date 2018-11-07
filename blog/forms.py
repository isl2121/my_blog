from django import forms
from servermanager.models import EmailSendLog

#class Sendmailform(forms.Form):
class Sendmailform(forms.ModelForm):
	
	class Meta:
		model = EmailSendLog
		fields = ('title','sender','content')
		widgets = {
			'title' : forms.TextInput(attrs={'class': 'form-control'}),
			'sender' : forms.EmailInput(attrs={'class' : 'form-control'}),
			'content' : forms.Textarea(attrs={'class':'form-control post-input','placeholder' : '내용을 입력하여주십시요.'})
		}
'''	
	title = forms.CharField(max_length=1000,widget=forms.TextInput(attrs={'class': 'form-control'}))
	email = forms.CharField(max_length=100,widget=forms.TextInput(attrs={'class' : 'form-control'}))
	content = forms.CharField(widget=forms.Textarea(attrs={'class':'form-control user-status-box post-input'}))
'''