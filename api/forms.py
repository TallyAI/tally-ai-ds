from django import forms
from api.models import url


class ApprovalForm(forms.ModelForm):#bound to a django Model
    url = forms.CharField(max_length=5000)
    # id = forms.IntegerField()

    class Meta:
        model = url#links the model
        fields = ('url',)#fields to include, could include more than one, comma saves datatype as tuple