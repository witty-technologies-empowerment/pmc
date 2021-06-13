from django import forms
from .models import userContact
from django.contrib.auth.models import User




class UserForm(forms.ModelForm):
    username = forms.CharField(max_length=30, required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(max_length=254)
    password = forms.CharField(widget=forms.PasswordInput())
    re_type_password = forms.CharField(widget=forms.PasswordInput())


    class Meta():
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password', 're_type_password',)


class UserAddForm(forms.ModelForm):
     class Meta():
         model = userContact
         fields = ('telephone',)
