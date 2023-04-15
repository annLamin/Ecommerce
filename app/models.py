from django.contrib.auth.models import User, BaseUserManager, AbstractBaseUser, PermissionsMixin
from django.conf import settings
from django.utils import timezone
from django.shortcuts import reverse
from django.db import models
from hydara_ecommerce.utils import unique_slug_generator
from django.db.models.signals import pre_save
# from mptt.models import TreeForeignKey


# Create your models here.

USERNAME_FIELD = 'email'
class UserManager(BaseUserManager):

    def create_user(self, email, password=None):
        if not email:
            raise ValueError('Users must have an email address')
        user = self.model(
            email = self.normalize_email(email),
        )
        user.set_password(password)
        user.save(using=self._db)
        return user
         
    def create_superuser(self, email, password):
        user = self.create_user(
        email = self.normalize_email(email),
        password = password,)
        user.is_admin = True
        user.is_staff = True
        user.is_superuser = True
        user.save(using=self._db)
        return user


class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(verbose_name="email",max_length=254, unique=True)
    date_joined = models.DateTimeField(verbose_name="date joined",auto_now_add=True)
    user_type=models.CharField(max_length=100,default='admin')
    last_login = models.DateTimeField(verbose_name="last login",auto_now=True)
    is_admin = models.BooleanField(default=False)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    hide_email = models.BooleanField(default=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def has_perm(self,perm, obj=None):
        return self.is_admin

    def has_module_perms(self, app_label):
        return True

class Sup_user(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,unique=True)
    full_name=models.CharField(max_length=30,blank=False)
    def __str__(self):
        return self.full_name


class Sales_Person(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,unique=True)
    full_name=models.CharField(max_length=30,blank=False)
    def __str__(self):
        return '%s %s' % (self.full_name)


class Buyer(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,unique=True)
    full_name = models.CharField( blank=False, max_length=30)
    joined_on = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return '%s %s' % (self.full_name)


class Category(models.Model):
    title = models.CharField(max_length=200, unique=True)
    image = models.ImageField(upload_to='category')
   
    def __str__(self):
        return self.title
    
class Brand(models.Model):
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, unique=True)
    # image = models.ImageField(upload_to='brand')

    def __str__(self):
        return self.title

class Logistic(models.Model):
    user=models.OneToOneField(settings.AUTH_USER_MODEL,on_delete=models.PROTECT,unique=True)
    full_name=models.CharField(max_length=30,blank=False)
    def __str__(self):
        return '%s %s' % (self.full_name)


class ItemAttribute(models.Model):
    title = models.CharField(max_length=100, blank=True, null=True)
    one = models.CharField(max_length=100, blank=True, null=True)
    two=models.CharField(max_length=100, blank=True, null=True)
    three = models.CharField(max_length=100, blank=True, null=True)
    four = models.CharField(max_length=100, blank=True, null=True)
    five = models.CharField(max_length=100, blank=True, null=True)
    six = models.CharField(max_length=100, blank=True, null=True)
    seven = models.CharField(max_length=100, blank=True, null=True)
    eight = models.CharField(max_length=100, blank=True, null=True)
    def __str__(self):
        return self.title
 
class Item(models.Model):
    title = models.CharField(max_length=200)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    attribute = models.ForeignKey(ItemAttribute, on_delete=models.CASCADE, null=True, blank=True)
    image = models.ImageField(upload_to="products")
    image2 = models.ImageField(upload_to="products")
    image3 = models.ImageField(upload_to="products")
    image4 = models.ImageField(upload_to="products")
    price = models.PositiveIntegerField()
    description = models.TextField(max_length=200)
    quantity=models.PositiveIntegerField(default=1)
    view_count = models.PositiveIntegerField(default=0)
    date = models.DateTimeField(auto_now_add=True)
    slug = models.SlugField(max_length=250,null=True, blank=True)

def __str__(self):
        return self.title  

def get_add_to_cart_url(self):
        return reverse("app:add-to-cart", kwargs={
            'slug': self.slug
        })

def slug_generator(sender, instance, *args, **kwargs):
        if not instance.slug:
            instance.slug = unique_slug_generator(instance)

        
pre_save.connect(slug_generator, sender=Item)




class Cart(models.Model):
    buyer = models.ForeignKey(Buyer, on_delete=models.SET_NULL, null=True, blank=True)
    total = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):  
        return "Cart: " + str(self.id)
        
class CartProduct(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
    product = models.ForeignKey(Item, on_delete=models.CASCADE)
    rate = models.PositiveIntegerField()  
    quantity = models.PositiveIntegerField()
    subtotal = models.PositiveIntegerField()

    def __str__(self):
        return "Cart: " + str(self.cart.id) + " CartProduct: " + str(self.id)
 
ORDER_STATUS = (
    ("Received", "Received"),
    ("Processing", "Processing"),
    ("On the way", "On the way"),
    ("Completed", "Completed"),
    ("Canceled", "Canceled"),
)

PAYMENT_STATUS = (
    ("Pending", "Pending"),
    ("Processing", "Processing"),
    ("Completed", "Completed"),
    
    
)

class Order(models.Model):
    cart = models.OneToOneField(Cart, on_delete=models.CASCADE) 
    name = models.CharField(max_length=200)
    home_address = models.CharField(max_length=200)
    google_plus = models.CharField(max_length=200)
    mobile = models.CharField(max_length=20)
    email = models.EmailField(null=True, blank=True)
    subtotal = models.PositiveIntegerField()
    total = models.PositiveIntegerField()
    order_status = models.CharField(max_length=50, choices=ORDER_STATUS)
    payment_status = models.CharField(max_length=50, choices=PAYMENT_STATUS)
    created_at = models.DateTimeField(auto_now_add=True)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return "Order: " + str(self.id)

class News(models.Model):
    title = models.CharField(max_length=200,blank=False)
    message = models.CharField(max_length=200,blank=False)
    image = models.ImageField(upload_to='news')
    date=models.DateTimeField(auto_now_add=True)

class Advert(models.Model):
    title = models.CharField(max_length=200,blank=False)
    message = models.CharField(max_length=200,blank=False)
    image = models.ImageField(upload_to='news')
    contact = models.CharField(max_length=30)
    date=models.DateTimeField(auto_now_add=True)

class Contact(models.Model):
    full_name = models.CharField(max_length=200,blank=False)
    email = models.EmailField(max_length=200,blank=False)
    telephone = models.CharField(max_length=200,blank=False)
    message = models.TextField(max_length=500,blank=False)
    date=models.DateTimeField(auto_now_add=True)