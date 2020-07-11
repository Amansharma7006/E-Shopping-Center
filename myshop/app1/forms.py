from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField
from django_countries.widgets import CountrySelectWidget
from .models import UserProfile

class UserUpdateForm(forms.ModelForm):
    email=forms.EmailField()
    first_name=forms.CharField(max_length=50)
    last_name=forms.CharField(max_length=50)
    class Meta:
        model= User
        fields=['username','email','first_name','last_name']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model=UserProfile
        fields=['profile_pic',]





PAYMENT_CHOICES= (
    ('S','Stripe'),
    ('P','PayPal'),
)


class CheckoutForm(forms.Form):
    shipping_address=forms.CharField(required=False)
    shipping_address2=forms.CharField(required=False)
    shipping_country = CountryField(blank_label='(select country)').formfield(required=False,)
    shipping_state=forms.CharField(required=False)
    shipping_zip=forms.CharField(required=False)

    billing_address=forms.CharField(required=False)
    billing_address2=forms.CharField(required=False)
    billing_country = CountryField(blank_label='(select country)').formfield(required=False,)
    billing_state=forms.CharField(required=False)
    billing_zip=forms.CharField(required=False)

    same_billing_address=forms.BooleanField(required=False)
    set_default_shipping=forms.BooleanField(required=False)
    use_default_shipping=forms.BooleanField(required=False)

    set_default_billing=forms.BooleanField(required=False)
    use_default_billing=forms.BooleanField(required=False)

    payment_option=forms.ChoiceField(widget=forms.RadioSelect(),choices=PAYMENT_CHOICES)

class CouponForm(forms.Form):
    code=forms.CharField(widget=forms.TextInput(attrs={
        'class':'form-control',
        'placeholder': 'Promo code',
        'aria-label':'Recipient\'s username',
        'aria-describedby':'basic-addon2'
    }))

class RefundForm(forms.Form):
    ref_code= forms.CharField()
    message=forms.CharField(widget=forms.Textarea(attrs={
        'rows':4
    }))
    email=forms.EmailField()

class PaymentForm(forms.Form):
    stripeToken = forms.CharField(required=False)
    save = forms.BooleanField(required=False)
    use_default = forms.BooleanField(required=False)



class SignupForm(UserCreationForm):
    email=forms.EmailField()
    first_name=forms.CharField(max_length=50)
    last_name=forms.CharField(max_length=50)
    class Meta:
        model= User
        fields=['username','email','first_name','last_name','password1','password2']
