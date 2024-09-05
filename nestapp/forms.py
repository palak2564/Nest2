# myapp/forms.py

from django import forms
from .models import NestUser , Note # Import your custom User model


class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput)

    class Meta:
        model = NestUser
        fields = ['username', 'email', 'branch', 'password1', 'password2']

    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password1'] != cd['password2']:
            raise forms.ValidationError('Passwords don’t match.')
        return cd['password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data['password1'])
        if commit:
            user.save()
        return user



class NoteUploadForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ['subject', 'branch', 'description', 'semester', 'file']
