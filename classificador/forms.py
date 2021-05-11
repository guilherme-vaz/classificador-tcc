from django import forms
from django.forms import ModelForm
from .models import Search

class searchForm(ModelForm):
    class Meta:
        model = Search
        fields = '__all__'