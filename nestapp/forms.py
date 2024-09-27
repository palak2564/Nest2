from django import forms
from .models import NestUser, Note, Order, PickupLocation
from .models import Comment

class SignupForm(forms.ModelForm):
    password1 = forms.CharField(label='Password', widget=forms.PasswordInput, help_text='Enter a strong password.')
    password2 = forms.CharField(label='Confirm Password', widget=forms.PasswordInput, help_text='Re-enter your password for confirmation.')

    class Meta:
        model = NestUser
        fields = ['username', 'email', 'branch', 'password1', 'password2']
        help_texts = {
            'username': 'Enter a unique username.',
            'email': 'We will not share your email with anyone.',
        }

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if NestUser.objects.filter(username=username).exists():
            raise forms.ValidationError('This username is already taken. Please choose a different one.')
        return username

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

    def clean_file(self):
        file = self.cleaned_data.get('file')
        if file and not file.name.endswith('.pdf') and not file.name.endswith('.doc'):
            raise forms.ValidationError("Please upload a file in PDF or DOC format.")
        return file

class PrintOrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['pdf_file', 'color_option', 'pickup_location', 'fast_option']#'delivery_option' #'file_type'
        widgets = {
            'color_option': forms.RadioSelect,
            'fast_option': forms.CheckboxInput,
             # The 'delivery_option' field will be implemented in the future, 
             # and is currently commented out in the template.
            # 'delivery_option': forms.CheckboxInput,
        }

    def clean_pdf_file(self):
        pdf = self.cleaned_data.get('pdf_file')
        if pdf and not pdf.name.endswith('.pdf'):
            raise forms.ValidationError("Please upload a PDF file.")
        return pdf

    def clean_pickup_location(self):
        pickup_location = self.cleaned_data.get('pickup_location')
        # Add your validation logic here (e.g., check if the location is available)
        if not PickupLocation.objects.filter(id=pickup_location.id).exists():
            raise forms.ValidationError("Selected pickup location is not valid.")
        return pickup_location

#new code
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        labels = {
            'content': 'Add a comment'
        }
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Write your comment here...'})
        }