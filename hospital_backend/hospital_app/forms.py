from django import forms
from hospital_app.models import HospitalUser, Hospital


class HospitalSignUpForm(forms.Form):
    """
    Custom form for hospital registration.
    """
    # Account fields
    username = forms.CharField(
        max_length=150,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Choose a username'})
    )
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Create password'}),
        required=True
    )
    
    # Hospital fields
    hospital_name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter hospital name'})
    )
    hospital_phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Hospital phone number'})
    )
    hospital_region = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter region'})
    )
    hospital_city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter city'})
    )
    hospital_address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Full hospital address'})
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if HospitalUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email is already in use.")
        return email

    def clean_username(self):
        username = self.cleaned_data.get('username')
        if HospitalUser.objects.filter(username=username).exists():
            raise forms.ValidationError("This username is already in use.")
        return username


class HospitalProfileForm(forms.ModelForm):
    """
    Form for managing Hospital profile information.
    Allows editing of hospital details including name, phone, location, and address.
    """
    name = forms.CharField(
        max_length=255,
        required=True,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nom de l\'hôpital'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Numéro de téléphone'})
    )
    region = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Région'})
    )
    city = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ville'})
    )
    address = forms.CharField(
        max_length=255,
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'placeholder': 'Adresse', 'rows': 3})
    )

    class Meta:
        model = Hospital
        fields = ('name', 'phone', 'region', 'city', 'address')
