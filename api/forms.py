# from django.forms import ModelForm
# from . models import url
#
# class MyForm(ModelForm):
# 	class Meta:
# 		model=url
# 		fields = '__all__'

from django import forms


class ApprovalForm(forms.Form):
    url =  forms.CharField(max_length=5000)