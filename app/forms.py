from django import forms
from django.contrib.auth import authenticate
from django.forms import widgets
from .models import *
from django.core.validators import MinValueValidator
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import UserCreationForm
from django_countries.fields import CountryField



class UserForm(UserCreationForm):
    full_name = forms.CharField()
    email = forms.EmailField()
    user_type=forms.Select()
   
    
   
    class Meta:
        model = User
        fields = ('full_name','email','password1','password2')
        widgets = {
            'email' : forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}),
            'password1' : forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}),
            'password2' : forms.PasswordInput(attrs={'class':'form-control','placeholder':'Confirm Password'})
        }
    def clean_email(self):
        email = self.cleaned_data['email'].lower()
        try:
            user = User.objects.get(email=email)
        except Exception as e:
            return email



class AccountAuthenticationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('email','password')
        widgets = {
            'email' : forms.EmailInput(attrs={'class':'form-control','placeholder':'Email'}),
            'password' : forms.PasswordInput(attrs={'class':'form-control','placeholder':'Password'}),
            }
    def clean(self):
        if self.is_valid:
            email = self.cleaned_data['email']
            password = self.cleaned_data['password']
            if not authenticate(email=email,password=password):
                raise forms.ValidationError('Invalid Credentials')
  

class ProductForm(forms.ModelForm):
    category = forms.Select(),
    title = forms.CharField(required=True),
    brand = forms.CharField(required=True),
    attribute = forms.CharField(required=False),
    price= forms.IntegerField(required=True),
    description= forms.CharField(required=True),
    quantity= forms.IntegerField(required=True),
    image = forms.ImageField(required=True),
    image2 = forms.ImageField(required=True),
    image3 = forms.ImageField(required=True),
    image4 = forms.ImageField(required=True),
    class Meta:
        model = Item
        fields = ('category','brand', 'title','attribute','price','description','quantity','image','image2','image3','image4')

class ProductUpdateForm(forms.ModelForm):
    category = forms.Select(),
    title = forms.CharField(required=True),
    brand = forms.CharField(required=True),
    attribute=forms.Select(),
    price= forms.IntegerField(required=True),
    description= forms.CharField(required=True),
    quantity= forms.IntegerField(required=True),
    image = forms.ImageField(required=True),
    image2 = forms.ImageField(required=True),
    image3 = forms.ImageField(required=True),
    image4 = forms.ImageField(required=True),
    class Meta:
        model = Item
        fields = ('category','brand', 'title','attribute','price','description','quantity','image','image2','image3','image4')

class NewsUpdateForm(forms.ModelForm):
    title = forms.CharField(required=True),
    message = forms.CharField(required=True),
    image = forms.ImageField(required=True),
    
    class Meta:
        model = News
        fields = ('title','message','image')

class AdvertUpdateForm(forms.ModelForm):
    title = forms.CharField(required=True),
    message = forms.CharField(required=True),
    contact = forms.CharField(required=True),
    image = forms.ImageField(required=True),
    
    class Meta:
        model = Advert
        fields = ('title','message','contact', 'image')


class AttributeForm(forms.ModelForm):
    title = forms.CharField(required=True)
    one = forms.CharField(required=False)
    two = forms.CharField(required=False)
    three = forms.CharField(required=False)
    four = forms.CharField(required=False)
    five = forms.CharField(required=False)
    six = forms.CharField(required=False)
    seven = forms.CharField(required=False)
    eight = forms.CharField(required=False)

    class Meta:
        model = ItemAttribute
        fields = ('title','one', 'two','three','four', 'five','six', 'seven','eight')

class ProductQuantityUpdateForm(forms.ModelForm):
    quantity= forms.IntegerField(required=True),
    class Meta:
        model = Item
        fields = ('quantity',)
    

class CategoryForm(forms.ModelForm):
    title = forms.CharField(required=True),
    image = forms.ImageField(required=True),

    class Meta:
        model = Category
        fields = ('title','image',)
class CategoryUpdateForm(forms.ModelForm):
    title = forms.CharField(required=True),
    image = forms.ImageField(required=True),

    class Meta:
        model = Category
        fields = ('title','image',)
        
class BrandForm(forms.ModelForm):
    title = forms.CharField(required=True),
    category = forms.Select(),
    
    class Meta:
        model = Brand
        fields = ('title','category')
class UpdateAttributeForm(forms.ModelForm):
    title = forms.CharField(required=True)
    one = forms.CharField(required=False)
    two = forms.CharField(required=False)
    three = forms.CharField(required=False)
    four = forms.CharField(required=False)
    five = forms.CharField(required=False)
    six = forms.CharField(required=False)
    seven = forms.CharField(required=False)
    eight = forms.CharField(required=False)

    class Meta:
        model = ItemAttribute
        fields = ('title','one', 'two','three','four', 'five','six', 'seven','eight')

class BrandUpdateForm(forms.ModelForm):
    title = forms.CharField(required=True),
    category = forms.Select(),
    class Meta:
        model = Brand
        fields = ('title','category')
        
class AdvertForm(forms.ModelForm):
    title = forms.CharField(required=True),
    image = forms.ImageField(required=True),
    message=forms.CharField(required=True)
    contact =forms.CharField(required=True)
    class Meta:
        model = Advert
        fields = ('title','image','message','contact')

class NewsForm(forms.ModelForm):
    title = forms.CharField(required=True),
    image = forms.ImageField(required=True),
    message=forms.CharField(required=True)
    
    
    class Meta:
        model = News
        fields = ('title','image', 'message')

class CheckoutForm(forms.ModelForm):
    name =forms.CharField(required=True)
    home_address=forms.CharField(required=True)
    google_plus = forms.CharField(required = True)
    mobile=forms.CharField(required=True)
    email=forms.CharField(required=False)
    class Meta:
        model = Order
        fields = ["name", "home_address",'google_plus',
                  "mobile", "email"]

class ContactForm(forms.ModelForm):
    full_name = forms.CharField(required=True),
    email = forms.EmailField(required=True),
    telephone = forms.CharField(required=False),
    message = forms.CharField(required=False),
    
    class Meta:
        model = Contact
        fields = ('full_name','email', 'telephone','message')


# class QuantityForm(models.Model):
#     quantity=forms.PositiveIntegerField(default=1)
#     class Meta:
#         model =  CartProduct
#         fields = ['quantity']