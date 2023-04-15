from django.contrib import admin
from django import forms
from django.contrib.auth.admin import UserAdmin
from app.models import User
from .models import *
# Register your models here.
class UserAccount(UserAdmin):
    list_display = ('email','date_joined','user_type','last_login','is_admin','is_staff' )
    search_fields = ('email',)
    readonly_fields = ('id','date_joined','last_login') 

    filter_horizontal = ()
    list_filter = ()
    fieldsets = ()
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2'),
        }),
    )
    ordering = ('email',)

admin.site.register(User, UserAccount)

@admin.register(Item)
class appAdmin(admin.ModelAdmin):
    list_display=['id' ,'title','quantity', 'category','price']
    search_fields=['title','brand']

@admin.register(Logistic)
class appAdmin(admin.ModelAdmin):
    list_display=['full_name']
    search_fields=['full_name']

@admin.register(Cart)
class appAdmin(admin.ModelAdmin):
    list_display=['id','total','created_at']
    search_fields=['id']

@admin.register(CartProduct)
class appAdmin(admin.ModelAdmin):
    list_display=['id','cart','product', 'quantity','rate','subtotal']
    search_fields=['id']

@admin.register(Sales_Person)
class appAdmin(admin.ModelAdmin):
    list_display=['full_name']
    search_fields=['full_name']

@admin.register(Sup_user)
class appAdmin(admin.ModelAdmin):
    list_display=['full_name']
    search_fields=['full_name']

@admin.register(Buyer)
class appAdmin(admin.ModelAdmin):
    list_display=['full_name']
    search_fields=['full_name']

@admin.register(Order)
class appAdmin(admin.ModelAdmin):
    list_display=['id','name','home_address','total']
    search_fields=['name']

@admin.register(Category)
class appAdmin(admin.ModelAdmin):
    list_display=['id','title', 'image']
    search_fields=['title']



@admin.register(Brand)
class appAdmin(admin.ModelAdmin):
    list_display=['id','title']
    search_fields=['title']

@admin.register(ItemAttribute)
class appAdmin(admin.ModelAdmin):
    list_display=['id','title',]
    search_fields=['title']

@admin.register(News)
class appAdmin(admin.ModelAdmin):
    list_display=['id','title', 'image']
    search_fields=['title']

@admin.register(Advert)
class appAdmin(admin.ModelAdmin):
    list_display=['id','title', 'image']
    search_fields=['title']
