from django import forms
from yelp.models import business_id_test1


class ApprovalForm(forms.ModelForm):#bound to a django Model
    biz_id = forms.CharField(max_length=5000)
    # id = forms.IntegerField()

    class Meta:
        model = business_id_test1#links the model
        fields = ('biz_id',)#fields to include, could include more than one, comma saves datatype as tuple