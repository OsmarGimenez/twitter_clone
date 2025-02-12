from django import forms 
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Post, Profile
from django.core.validators import MaxLengthValidator

class UserRegisterForm(UserCreationForm):
    password2 = forms.CharField(widget=forms.PasswordInput, label='Confirm Password')
    first_name = forms.CharField(max_length=30, widget=forms.TextInput(attrs={'autofocus': True}))  

    class Meta:
        model = User
        fields = ['first_name', 'username', 'email']  

    def clean_password2(self):
        password1 = self.cleaned_data.get('password1')  
        password2 = self.cleaned_data.get('password2')
        if password1 != password2:
            raise forms.ValidationError("Passwords must match")
        return password2
    
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email:
            if User.objects.filter(email=email).exists():
                raise forms.ValidationError("Este correo electrónico ya está en uso.")
        return email

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image', 'bio']  

class PostForm(forms.ModelForm):
    content = forms.CharField(
        widget=forms.Textarea(attrs={
            'class': 'form-control w-100 contentsBox', 
            'rows': '3',
            'placeholder': '¿Qué está pasando?'
        }),
        max_length=280,
        validators=[MaxLengthValidator(280)]
    )

    class Meta:
        model = Post
        fields = ['content']

class UserUpdateForm(forms.ModelForm):
	class Meta:
		model = User
		fields = ['first_name', 'username']

class SearchForm(forms.Form):
    query = forms.CharField(label='Buscar usuarios', max_length=100)









