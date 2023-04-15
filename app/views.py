from django.shortcuts import render, redirect,get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from .models import *
from django.contrib import messages
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth .mixins import  LoginRequiredMixin
from django.contrib.auth.models import Group
from allauth.account.decorators import verified_email_required
from .forms import *
from django.views.generic import ListView, DetailView,View,TemplateView,FormView
from django.views.generic.edit import CreateView
from django.urls import reverse,reverse_lazy
from .decorators import allowed_users
from django.core.cache import cache
from django.db.models import Q,F
import datetime
from .filters import ItemFilter


def confirm_delete_cat(request,cid):
    cat = get_object_or_404(Category,pk=cid) 
    cat.delete()
    messages.success(request, 'Success!! Category Deleted Sucessfully')
    return redirect('/admin_view_category/')
def confirm_delete_bra(request,bid):
    bra = get_object_or_404(Brand,pk=bid) 
    bra.delete()
    messages.success(request, 'Success!! Brand Deleted Sucessfully')
    return redirect('/admin_view_brand/')
def confirm_delete_news(request,nid):
    new = get_object_or_404(News,pk=nid) 
    new.delete()
    messages.success(request, 'Success!! News Deleted Sucessfully')
    return redirect('/admin_view_news/')

def confirm_delete_advert(request,aid):
    ads = get_object_or_404(Advert,pk=aid) 
    ads.delete()
    messages.success(request, 'Success!! Advert Deleted Sucessfully')
    return redirect('/admin_view_advert/')


class EcomMixin(object):
    def dispatch(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id")
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            if request.user.is_authenticated and request.user.buyer:
                cart_obj.buyer = request.user.buyer
                cart_obj.save()
        return super().dispatch(request, *args, **kwargs)

class OrderSummaryView(TemplateView):
    
    template_name = "buyer/shoppingcart.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        cartcount=0
        available=0
        incart = 0
        
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
        
            cart_obj = Cart.objects.get(id=cart_id)
           
            cartcount = cart_obj.cartproduct_set.all().count()
            cartp = cart_obj.cartproduct_set.all()
            for cartt in cartp:
                available = cartt.product.quantity
                incart =  cartt.quantity
                
          

        else:
            cart = None
        context = {
            'cart':cart,
            'cartcount':cartcount,
            'available':available ,
            'incart':incart
            }
        return context

class ManageCartView(View):
    def get(self, request, *args, **kwargs):
        cp_id = self.kwargs["cp_id"]
        action = request.GET.get("action")
        cp_obj = CartProduct.objects.get(id=cp_id)
        cart_obj = cp_obj.cart

        
        if action == "inc":
            cp_obj.quantity += 1
            cp_obj.subtotal += cp_obj.rate
            cp_obj.save()
            cart_obj.total += cp_obj.rate
            cart_obj.save()
            
            
            # cp_obj.product.quantity.save()
       
        elif action == "dcr":
            cp_obj.quantity -= 1
            cp_obj.subtotal -= cp_obj.rate
            cp_obj.save()
            cart_obj.total -= cp_obj.rate
            cart_obj.save()
            if cp_obj.quantity == 0:
                cp_obj.delete()
        elif action == "rmv":
            cart_obj.total -= cp_obj.subtotal
            cart_obj.save()
            cp_obj.delete()
        else:
            pass
        return redirect("app:order-summary")

class EmptyCartView(View):
    def get(self, request, *args, **kwargs):
        cart_id = request.session.get("cart_id", None)
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
            cart.cartproduct_set.all().delete()
            cart.total = 0
            cart.save()
        return redirect("app:order-summary")

class CheckoutView(EcomMixin,CreateView):
    template_name = "buyer/checkout.html"
    form_class = CheckoutForm
    success_url = reverse_lazy("app:buyerprofile")
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.buyer:
            pass
        else:
            return redirect("/accounts/login/?next=/checkout/")
        return super().dispatch(request, *args, **kwargs)


    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cart_id = self.request.session.get("cart_id", None)
        user_name = self.request.user.buyer
  
        if cart_id:
            cart = Cart.objects.get(id=cart_id)
           
        else:
            cart_obj = None
        context['cart'] = cart
        context['user_name']=user_name
        
        return context
    def form_valid(self, form):
        cart_id = self.request.session.get("cart_id")
        cart = Cart.objects.get(id=cart_id)
        cartp = cart.cartproduct_set.all()

        for cartt in cartp:
            if cartt.product.quantity >= cartt.quantity:
                cartt.product.quantity -= cartt.quantity
                cartt.product.save()
            
                if cart_id:
                    cart_obj = Cart.objects.get(id=cart_id)
                    form.instance.cart = cart_obj
                    form.instance.subtotal = cart_obj.total
                    form.instance.total = cart_obj.total
                    form.instance.order_status = "Proccessing"
                    form.instance.payment_status = "Pending"
                    del self.request.session['cart_id']
                    order = form.save()
                    messages.add_message(self.request, messages.INFO, 'Success!! Order made sucessfully')   
                else:
                    
                    return redirect("app:profile")
            else:
                messages.add_message(self.request, messages.WARNING, 'Fail Order!! Quantity in the cart is nt available')
                del self.request.session['cart_id']
                logout(self.request)
                return redirect("app:home")
        return super().form_valid(form)

   
                    
class BuyerProfileView(EcomMixin,TemplateView):
    template_name = "buyer/buyerprofile.html"

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Buyer.objects.filter(user=request.user).exists():
            pass
        else:
            return redirect("/accounts/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        buyer = self.request.user.buyer
        cartcount=0
        cart_id = self.request.session.get("cart_id", None)
        
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            cartcount = cart_obj.cartproduct_set.all().count()

        context['buyer'] = buyer
        orders = Order.objects.filter(cart__buyer=buyer).order_by("-id")
        context["orders"] = orders
        context['cartcount']=cartcount
      
        return context

class BuyerOrderDetailView(EcomMixin,DetailView):
    template_name = "buyer/buyerorderdetail.html"
    model = Order
    context_object_name = "ord_obj"
 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Buyer.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            if request.user.buyer != order.cart.buyer:
                return redirect("app:buyerprofile")
        else:
            return redirect("/accounts/login/?next=/profile/")
        return super().dispatch(request, *args, **kwargs)
def home(request):
    
   
        user_name = request.user
        top_item = Item.objects.all().order_by('-price')[:1]
        mobile = Item.objects.filter(category__title='Mobile' ).order_by('-date')[:1]
        category = Category.objects.all().order_by('id')
        category1= Category.objects.all()
        news = News.objects.all().order_by('-date')[:5]
        adverts = Advert.objects.all().order_by('-date')[:5]
        new_arivals = Item.objects.all().order_by('-date')[:4]
           
        expensive_item= Item.objects.all().order_by('-price')[:1]
        cheapest_item= Item.objects.all().order_by('price')[:1]
        new_arrival = Item.objects.filter(category__title='Mobile').order_by('-date')[:3]
        best_selling=Item.objects.all().order_by('-price')[:5]
        cartcount=0
        cart_id = request.session.get("cart_id", None)
        
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            cartcount = cart_obj.cartproduct_set.all().count()
        
    
        
        return render(request,  "index.html",
            {
            'cartcount':cartcount,
            'news':news,
            'adverts':adverts,
            'category1':category1,
            'best_selling':best_selling,
            'new_arivals':new_arivals,
            'top_item' :top_item,
            'mobile':mobile,
            'category':category,
            'expensive_item':expensive_item,
            'cheapest_item':cheapest_item,
            'new_arrival':new_arrival,
            'user_name':user_name})

class SearchView(TemplateView):
    template_name = "search.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cartcount=0
        cart_id = self.request.session.get("cart_id", None)
        
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            cartcount = cart_obj.cartproduct_set.all().count()
        kw = self.request.GET.get("keyword")
        results = Item.objects.filter(
            Q(title__icontains=kw) | Q(description__icontains=kw)| Q(category__title__icontains=kw))
        # category=Category.objects.all().order_by('-id')
        context["results"] = results
        context['cartcount']=cartcount
        return context

def product_list(request):
    data=Category.objects.all().order_by('-id')
    category1 = Category.objects.all()
    # data = data.category_set.first()
    cartcount=0
    cart_id = request.session.get("cart_id", None)
        
    if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            cartcount = cart_obj.cartproduct_set.all().count()
    cats = Category.objects.all().order_by('-id')
   
    return render(request, 'product_list.html', {'cartcount':cartcount, 'category1':category1 ,'data':data, 'cats':cats})

def category_product_list(request,cat_id):
    category=Category.objects.get(id=cat_id)
    data = Brand.objects.filter(category=category).order_by('-id')
    myFilter = ItemFilter(request.GET, queryset=data)
    data =  myFilter.qs
    cartcount=0
    cart_id = request.session.get("cart_id", None)
    cats = Category.objects.all().order_by('-id')    
    if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            cartcount = cart_obj.cartproduct_set.all().count()
    return render(request, 'category_product_list.html', {'myFilter':myFilter,'cats':cats,'cartcount':cartcount,  'category':category,'data':data,  })

def brand_product_list(request,brand_id):
    brand=Brand.objects.get(id=brand_id)
    data = Item.objects.filter(brand=brand).order_by('-id')
    for mob in data:
        print(f"helloooooo {mob.id}")
    return render(request, 'brand_product_list.html', { 'brand':brand, 'data':data})



def user_registration(request):
    categories = Category.objects.all()
    if request.method == 'POST':
            reg_form = UserForm(request.POST)
            if reg_form.is_valid():
                full_name = reg_form.cleaned_data['full_name']
                email =  reg_form.cleaned_data['email']
                password = reg_form.cleaned_data['password1']
                user=User.objects.create(email=email, user_type="buyer")
                user.set_password(reg_form.cleaned_data['password1'])
                    
                Buyer.objects.create(user=user, full_name=full_name)
                group = Group.objects.get(name='buyer')
                user.groups.add(group)
                user.save()
                messages.success(request, 'Success!! Account created sucessfully')
                return redirect('/accounts/login/')
    else:
        reg_form=UserForm()
        messages.warning(request, 'Fail!! Account was not created')
    return render(request, 'login.html',{'reg_form':reg_form, 'categories':categories})

def contact(request):
    categories = Category.objects.all()
    if request.method == 'POST':
            con_form = ContactForm(request.POST)
            if con_form.is_valid():
                full_name = con_form.cleaned_data['full_name']
                email =  con_form.cleaned_data['email']
                telephone = con_form.cleaned_data['telephone']
                message = con_form.cleaned_data['message']
                   
                Contact.objects.create(email=email,telephone=telephone,message=message, full_name=full_name)
                
                messages.success(request, 'Success!! Enquiry send sucessfully')
                return redirect('/')
    else:
        con_form=ContactForm()
        messages.warning(request, 'Fail!! Message was not send')
    return render(request, 'contact.html',{'con_form':con_form, 'categories':categories})




@login_required
@allowed_users(allowed_roles=['admin'])
def admin_home(request):
    user_name = request.user
    total_price = 0
    sale_no = 0
    t_total_price = 0
    t_sale_no = 0
    orders= Order.objects.all().count()
    no_contacts= Contact.objects.all().count()
    total_prod= Item.objects.all().count()
    users = User.objects.all().count()
    customers = Buyer.objects.all().count()
    date = timezone.now().date()
    total_orders = Order.objects.all()
    products = Item.objects.filter(date__date=date).count()
    t_orders = Order.objects.filter(date__date=date)
    
    for sale in t_orders:
        t_total_price += sale.total
        t_sale_no = t_orders.count()
    for sales in total_orders:
        total_price += sales.total
        sale_no = total_orders.count()
    
    return render(request, 'admin/admin_home.html',{'no_contacts':no_contacts, 'user_name':user_name, 'sale_no':sale_no, 't_sale_no':t_sale_no, 'total_price':total_price, 't_total_price':t_total_price, 'customers':customers,'t_orders':t_orders, 'orders':orders, 'total_prod':total_prod,'users':users,'products':products})


@login_required
@allowed_users(allowed_roles=['admin'])
def orders(request):
    orders=Order.objects.all()
    return render (request, 'admin/allorders.html', {'orders':orders})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_customers(request):
    customers=Buyer.objects.all()
    return render (request, 'admin/view_buyers.html', {'customers':customers})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_contacts(request):
    contacts = Contact.objects.all()
    return render (request, 'admin/admin_view_contacts.html', {'contacts':contacts})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_new_products(request):
    date = timezone.now().date()
    products=Item.objects.filter(date__date=date)
    return render (request, 'admin/admin_view_new_products.html', {'products':products})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_add_product(request):
    user_name = request.user
    if request.method == 'POST':
        add_product = ProductForm(request.POST, request.FILES)
        if add_product.is_valid():
            title = add_product.cleaned_data['title']
            brand = add_product.cleaned_data['brand']
            attribute = add_product.cleaned_data['attribute']
            price = add_product.cleaned_data['price']
            description = add_product.cleaned_data['description']
            image = add_product.cleaned_data['image']
            image2 = add_product.cleaned_data['image2']
            image3 = add_product.cleaned_data['image3']
            image4 = add_product.cleaned_data['image4']
            category=add_product.cleaned_data['category']
            quantity=add_product.cleaned_data['quantity']
            Item.objects.create(title=title,brand=brand,attribute=attribute,  price=price,description=description, image=image ,image2=image2 ,image3=image3,image4=image4,category=category,quantity=quantity)
            messages.success(request, 'Success!! Product created sucessfully')
            return redirect('/admin_view_products/')
    else:
        add_product=ProductForm()
        messages.warning(request, "!!!ERROR!!! Try Again")
   
    return render(request, 'admin/add_product.html', {'user_name':user_name, 'add_product':add_product})

def admin_add_attributes(request):
    user_name = request.user
    if request.method == 'POST':
        add_attribute = AttributeForm(request.POST)
        if add_attribute.is_valid():
            title = add_attribute.cleaned_data['title']
            one = add_attribute.cleaned_data['one']
            two = add_attribute.cleaned_data['two']
            three = add_attribute.cleaned_data['three']
            four = add_attribute.cleaned_data['four']
            five = add_attribute.cleaned_data['five']
            six = add_attribute.cleaned_data['six']
            seven = add_attribute.cleaned_data['seven']
            eight = add_attribute.cleaned_data['eight']
            ItemAttribute.objects.create(title=title,one=one,two=two,three=three,four=four, five=five,six=six,seven=seven, eight=eight)
            messages.success(request, 'Success!! Attribute created sucessfully')
            return redirect('/admin_view_attributes/')
    else:
        add_attribute=AttributeForm()
        messages.warning(request, "!!!ERROR!!! Try Again")
   
    return render(request, 'admin/admin_add_attributes.html',{'add_attribute':add_attribute, 'user_name':user_name})
@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_attributes(request):
    user_name=request.user
    attributes = ItemAttribute.objects.all().order_by('-id')
   
    return render(request, 'admin/admin_view_attributes.html', {'attributes':attributes, 'user_name':user_name})

@login_required
@allowed_users(allowed_roles=['admin'])
def edit_product(request,pid):
    prod = get_object_or_404(Item,pk=pid)
    up_prod = ProductUpdateForm(instance=prod)
    # stk = Stock.objects.filter(quantity=0)
    user_name = request.user
    if request.method == 'POST':
            up_prod = ProductUpdateForm(request.POST, request.FILES, instance=prod)
            if up_prod.is_valid():
                up_prod.save()
                messages.success(request, 'Success!! Product updated sucessfully')
                return redirect(f'/admin_view_products/')
            else:
                messages.warning(request, "!!!ERROR!!! Try Again")
    product_list = Item.objects.all()
    return render(request, 'admin/edit_product.html', {'user_name':user_name,'up_prod':up_prod,'product_list': product_list})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_edit_news(request,nid):
    news = get_object_or_404(News,pk=nid)
    up_news = NewsUpdateForm(instance=news)
    user_name = request.user
    if request.method == 'POST':
            up_news = NewsUpdateForm(request.POST, request.FILES, instance=news)
            if up_news.is_valid():
                up_news.save()
                messages.success(request, 'Success!! News updated sucessfully')
                return redirect(f'/admin_view_news/')
            else:
                messages.warning(request, "!!!ERROR!!! Try Again")
    news_list = News.objects.all()
    return render(request, 'admin/edit_news.html', {'user_name':user_name,'up_news':up_news,'news_list': news_list})


@login_required
@allowed_users(allowed_roles=['admin'])
def admin_edit_advert(request,aid):
    ads = get_object_or_404(Advert,pk=aid)
    up_advert = AdvertUpdateForm(instance=ads)
    user_name = request.user
    if request.method == 'POST':
            up_advert = AdvertUpdateForm(request.POST, request.FILES, instance=ads)
            if up_advert.is_valid():
                up_advert.save()
                messages.success(request, 'Success!! Advert updated sucessfully')
                return redirect(f'/admin_view_advert/')
            else:
                messages.warning(request, "!!!ERROR!!! Try Again")
    advert_list = Advert.objects.all()
    return render(request, 'admin/edit_advert.html', {'user_name':user_name,'up_advert':up_advert,'advert_list': advert_list})


@login_required
@allowed_users(allowed_roles=['admin'])
def edit_product_quantity(request,pid):
    prod = get_object_or_404(Item,pk=pid)
    up_prod = ProductQuantityUpdateForm(instance=prod)
    user_name = request.user
    if request.method == 'POST':
        up_prod = ProductQuantityUpdateForm(request.POST,instance=prod)
        if up_prod.is_valid():
            up_prod.save()
            messages.success(request, 'Success!! Product updated sucessfully')
            return redirect(f'/admin_view_products/')
        else:
            messages.warning(request, "!!!ERROR!!! Try Again")
    product_list = Item.objects.all()
    return render(request, 'admin/edit_product_quantity.html', {'user_name':user_name,'up_prod':up_prod,'product_list': product_list})



@login_required
@allowed_users(allowed_roles=['admin'])
def admin_add_category(request):
    user_name = request.user
    if request.method == 'POST':
        add_category = CategoryForm(request.POST, request.FILES)
        if add_category.is_valid():
            title = add_category.cleaned_data['title']
            image = add_category.cleaned_data['image']
            Category.objects.create(title=title,image=image)
            messages.success(request, 'Success!! category created sucessfully')
            return redirect('/admin_view_category/')
    else:
        add_category=CategoryForm()
        messages.warning(request, "!!!ERROR!!! Try Again")
   
    return render(request, 'admin/add_category.html', {'user_name':user_name, 'add_category':add_category})

@login_required
@allowed_users(allowed_roles=['admin'])
def edit_category(request,cid):
    prod = get_object_or_404(Category,pk=cid)
    up_prod = CategoryUpdateForm(instance=prod)
    user_name = request.user
    if request.method == 'POST':
            up_prod = CategoryUpdateForm(request.POST, request.FILES,instance=prod)
            if up_prod.is_valid():
                up_prod.save()
                messages.success(request, 'Success!! Category updated sucessfully')
                return redirect(f'/admin_view_category/')
            else:
                messages.warning(request, "!!!ERROR!!! Try Again")
    product_list = Category.objects.all()
    return render(request, 'admin/edit_category.html', {'user_name':user_name,'up_prod':up_prod,'product_list': product_list})


@login_required
@allowed_users(allowed_roles=['admin'])
def admin_add_brand(request):
    user_name=request.user
    if request.method == 'POST':
        add_brand = BrandForm(request.POST)
        if add_brand.is_valid():
            title = add_brand.cleaned_data['title']
            category = add_brand.cleaned_data['category']
            Brand.objects.create(title=title,category=category)
            messages.success(request, 'Success!! brand created sucessfully')
            return redirect('/admin_view_brand/')
    else:
        add_brand=BrandForm()
        messages.warning(request, "!!!ERROR!!! Try Again")
   
    return render(request, 'admin/add_brand.html', {'user_name':user_name, 'add_brand':add_brand})

@login_required
@allowed_users(allowed_roles=['admin'])
def edit_brand(request,bid):
    prod = get_object_or_404(Brand,pk=bid)
    up_prod = BrandUpdateForm(instance=prod)
    user_name = request.user
    if request.method == 'POST':
            up_prod = BrandUpdateForm(request.POST,request.FILES,instance=prod)
            if up_prod.is_valid():
                up_prod.save()
                messages.success(request, 'Success!! Brand updated sucessfully')
                return redirect(f'/admin_view_brand/')
            else:
                messages.warning(request, "!!!ERROR!!! Try Again")
    product_list = Brand.objects.all()
    return render(request, 'admin/edit_brand.html', {'user_name':user_name,'up_prod':up_prod,'product_list': product_list})

@login_required
@allowed_users(allowed_roles=['admin'])
def edit_attribute(request,aid):
    prod = get_object_or_404(ItemAttribute,pk=aid)
    up_prod = UpdateAttributeForm(instance=prod)
    user_name = request.user
    if request.method == 'POST':
            up_prod = UpdateAttributeForm(request.POST,request.FILES,instance=prod)
            if up_prod.is_valid():
                up_prod.save()
                messages.success(request, 'Success!! Attribute updated sucessfully')
                return redirect(f'/admin_view_attributes/')
            else:
                messages.warning(request, "!!!ERROR!!! Try Again")
    attribute_list = ItemAttribute.objects.all()
    return render(request, 'admin/edit_attribute.html', {'user_name':user_name,'up_prod':up_prod,'product_list': product_list})


@login_required
@allowed_users(allowed_roles=['admin'])
def admin_add_advert(request):
    user_name=request.user
    if request.method == 'POST':
        add_advert = AdvertForm(request.POST, request.FILES)
        if add_advert.is_valid():
            title = add_advert.cleaned_data['title']
            image = add_advert.cleaned_data['image']
            message = add_advert.cleaned_data['message']
            contact=add_advert.cleaned_data['contact']
            Advert.objects.create(title=title,image=image, message=message,contact=contact)
            messages.success(request, 'Success!! advert created sucessfully')
            return redirect('/admin_view_advert/')
    else:
        add_advert=AdvertForm()
        messages.warning(request, "!!!ERROR!!! Try Again")
   
    return render(request, 'admin/add_advert.html', {'add_advert':add_advert})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_add_news(request):
    if request.method == 'POST':
        add_news = NewsForm(request.POST, request.FILES)
        if add_news.is_valid():
            title = add_news.cleaned_data['title']
            image = add_news.cleaned_data['image']
            message = add_news.cleaned_data['message']
            News.objects.create(title=title,image=image, message=message)
            messages.success(request, 'Success!! news created sucessfully')
            return redirect('/admin_view_news/')
    else:
        add_news=NewsForm()
        messages.warning(request, "!!!ERROR!!! Try Again")
   
    return render(request, 'admin/add_news.html', {'add_news':add_news})


class AdminallOrderDetailView(DetailView):
    template_name = "admin/adminallorderdetail.html"
    model = Order
    context_object_name = "ord_obj"
 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Sup_user.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            
        else:
            return redirect("/login/?next=/admin_home/")

        return super().dispatch(request, *args, **kwargs)

class AdminOrderDetailView(DetailView):
    template_name = "admin/adminorderdetail.html"
    model = Order
    context_object_name = "ord_obj"
 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Sup_user.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            
        else:
            return redirect("/login/?next=/admin_home/")
        return super().dispatch(request, *args, **kwargs)

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_add_sales(request):
    if request.method == 'POST':
            add_form = UserForm(request.POST, request.FILES)
            if add_form.is_valid():
                email = add_form.cleaned_data['email']
                full_name = add_form.cleaned_data['full_name']
                password = add_form.cleaned_data['password1']
                user=User.objects.create(email=email, user_type="sales_person")
                user.set_password(add_form.cleaned_data['password1'])
                user.save()
                Sales_Person.objects.create(user=user, full_name=full_name)
                group = Group.objects.get(name='sales_person')
                user.groups.add(group)
              
                
                messages.success(request, 'Success!! Account created sucessfully')
                return redirect('/admin_view_sales/')
    else:
        add_form=UserForm()
    return render(request, 'admin/admin_add_sales.html',{'add_form':add_form})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_sales(request):
    sales = Sales_Person.objects.all()
    return render(request, 'admin/admin_view_sales.html',{'sales':sales})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_users(request):
    users = User.objects.all()
    return render(request, 'admin/admin_view_users.html',{'users':users})


@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_products(request):
    user_name = request.user
    products = Item.objects.all()
    return render(request, 'admin/admin_view_products.html',{'user_name':user_name, 'products':products})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_category(request):
    category = Category.objects.all()
    return render(request, 'admin/admin_view_category.html',{'category':category})

@login_required
@allowed_users(allowed_roles=['admin'])    
def admin_view_brand(request):
    brand = Brand.objects.all()
    return render(request, 'admin/admin_view_brand.html',{'brand':brand})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_view_news(request):
    news = News.objects.all()
    return render(request, 'admin/admin_view_news.html',{'news':news})

@login_required
@allowed_users(allowed_roles=['admin'])   
def admin_view_advert(request):
    advert = Advert.objects.all()
    return render(request, 'admin/admin_view_advert.html',{'advert':advert})

@login_required
@allowed_users(allowed_roles=['admin'])
def admin_add_logistic(request):
    if request.method == 'POST':
            add_form = UserForm(request.POST)
            if add_form.is_valid() :
                email = add_form.cleaned_data['email']
                full_name = add_form.cleaned_data['full_name']
                password = add_form.cleaned_data['password1']
                user=User.objects.create(email=email, user_type="logistic")
                user.set_password(add_form.cleaned_data['password1'])
                user.save()
                Logistic.objects.create(user=user, full_name=full_name)
                group = Group.objects.get(name='logistic')
                user.groups.add(group)
              
                
                messages.success(request, 'Success!! Account created sucessfully')
                return redirect('/admin_view_logistics/')
    else:
        add_form=UserForm()
    return render(request, 'admin/admin_add_logistic.html',{'add_form':add_form})
def admin_view_logistics(request):
    logistics = Logistic.objects.all()
    return render(request, 'admin/admin_view_logistics.html',{'logistics':logistics})


class ItemDetailView(DetailView):
    model = Item
    template_name = "product.html"
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        url_slug = self.kwargs['slug']
        product = Item.objects.get(slug=url_slug)
        product.view_count += 1
        product.save()
        related_product = Item.objects.filter(category=product.category).exclude(id=product.id)[:4]
        cartcount=0
        cart_id = self.request.session.get("cart_id", None)
        
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            cartcount = cart_obj.cartproduct_set.all().count()
        
        context['product'] = product
        context['cartcount'] = cartcount
        context['related_product']=related_product
        
        return context


def shop(request):
    categories = Item.objects.all().order_by('-id')
    
    return render(request,'shop.html',{'categories':categories,} )

class add_to_cart(EcomMixin,TemplateView):
    template_name = "buyer/addtocart.html"
    # success_url = reverse_lazy("app:order-summary")
   
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # get product id from requested url
        product_id = self.kwargs['pro_id']
        suggest_items = Item.objects.all().order_by('view_count')[:4]

        # get product
        product_obj = Item.objects.get(id=product_id)
       
       
        # check if cart exists
        cart_id = self.request.session.get("cart_id", None)
        cartcount=0
        # cart_obj = Cart.objects.get(id=cart_id)
        # cartcount = cart_obj.cartproduct_set.all().count()
        if cart_id:
            cart_obj = Cart.objects.get(id=cart_id)
            this_product_in_cart = cart_obj.cartproduct_set.filter(product=product_obj)
            cartcount = cart_obj.cartproduct_set.all().count()
           
            
         

            # item already exists in cart
            if this_product_in_cart.exists():
                cartproduct = this_product_in_cart.last()
                cartproduct.quantity += 1
                cartproduct.subtotal += product_obj.price
                cartproduct.save()
                cart_obj.total += product_obj.price
                cart_obj.save()
                messages.add_message(self.request, messages.INFO, 'Success!! Order made sucessfully')
        
            # new item is added in cart
            else:
               
                   
                cartproduct = CartProduct.objects.create(
                    cart=cart_obj,
                    product=product_obj,
                    rate=product_obj.price,
                    quantity=1,
                    subtotal=product_obj.price)
                cart_obj.total += product_obj.price
                cart_obj.save()
                messages.add_message(self.request, messages.INFO, 'Success!! Item added to cart sucessfully')
              
                # messages.add_message(request, messages.INFO, 'Success!! Item added to cart sucessfully')   
                

        else:
            cart_obj = Cart.objects.create(total=0)
            self.request.session['cart_id'] = cart_obj.id
            cartproduct = CartProduct.objects.create(
                cart=cart_obj, product=product_obj, rate=product_obj.price, quantity=1, subtotal=product_obj.price)
            cart_obj.total += product_obj.price
            cart_obj.save()
            
            messages.add_message(self.request, messages.INFO, 'Success!! Item added to cart sucessfully')
        context = {
            'suggest_items':suggest_items,
            'cartcount':cartcount
        }
       
        return context



@login_required
@allowed_users(allowed_roles=['buyer'])
def buyer_home (request):
    username = request.user.buyer
    top_item = Item.objects.all().order_by('-price')[:1]
    latest_phone = Item.objects.filter(category__title='Mobile').order_by('-date')[:1]
    latest_computer = Item.objects.filter(category__title='Computer').order_by('-date')[:1]
    latest_watch = Item.objects.filter(category__title='Watch').order_by('-date')[:1]
    latest_clock = Item.objects.filter(category__title='Clock').order_by('-date')[:1]
    latest_accessories = Item.objects.filter(category__title='Accessories').order_by('-date')[:1]
    top_5_item = Item.objects.all().order_by('-price')[:5]
    top_dis = Item.objects.all().order_by('quantity')[:3]
    expensive_item= Item.objects.all().order_by('-price')[:1]
    cheapest_item= Item.objects.all().order_by('price')[:1]
    new_arivals= Item.objects.all().order_by('-date')[:4]
    new_arival= Item.objects.all().order_by('-date')[:1]
    best_sales = Item.objects.all().order_by('price')[:5]
    quantity_item = Item.objects.all().order_by('-quantity')[:5]
    quantity_item = Item.objects.all().order_by('-quantity')[:1]
        
    # currency = Currency.objects.all()
    # print(currency.cfa)
    return render(request, "buyer/buyer_home.html", {
        'username':username,
        'top_item' :top_item,
            'latest_phone':latest_phone,
            'new_arival':new_arival,
            'latest_computer': latest_computer,
            'latest_watch':latest_watch,
            'latest_clock':latest_clock,
            'quantity_item':quantity_item,
            'latest_clock':latest_clock,
            'cheapest_item':cheapest_item,
            'expensive_item':expensive_item   })

class logout_view(View):
    def get(self, request):
        logout(request)
        return redirect("app:home")

#Logistics
@login_required
@allowed_users(allowed_roles=['logistic'])
def logistic_home(request):
    user_name= request.user.logistic
    orders = Order.objects.filter(payment_status=('Completed'), order_status=('Completed')).order_by('-id')
    
    return render (request, 'logistic/logistic_home.html', {'user_name':user_name,'orders':orders})

@login_required
@allowed_users(allowed_roles=['logistic'])
def logistic_view_approved_sales(request):
    a_orders = Order.objects.filter(payment_status=('Completed')).order_by('-id')
  
    return render(request, 'logistic/completeorder.html' ,{'a_orders':a_orders})

@login_required
@allowed_users(allowed_roles=['logistic'])
def logistic_view_pending_sales(request):
    a_orders = Order.objects.exclude(payment_status=('Completed')).order_by('-id')
    
    return render(request, 'logistic/logistic_pending_sales.html' ,{'a_orders':a_orders})


class LogisticOrderDetailView(DetailView):
    template_name = "logistic/logisticorderdetail.html"
    model = Order
    context_object_name = "ord_obj"
 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Logistic.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            
        else:
            return redirect("/login/?next=/logistic_home/")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context

class LogisticOrderStatuChangeView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Logistic.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            
        else:
            return redirect("/login/?next=/logistic_home/")
        return super().dispatch(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.order_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("app:logisticOrderDetailView", kwargs={"pk": order_id}))

# @login_required()
# @allowed_users(allowed_roles=['logistic'])
# def logistic_print_reciept(request,oid):
#     order = get_object_or_404(Order,pk=oid)
#     total_price = order.total
#     # amount_paid = payment.total_amount
#     # balance = total_balance(total_price,payment.sale.total_amount_paid)
#     user_name = request.user.logistic
#     orders = Order.objects.filter(id=oid)

#     orders = orders.cart.cartproduct_set.all()
   
#     print(orders)
#     return render(request, 'logistic/logistic_print_reciept.html', {'total_price':total_price, 'orders':orders,'order':order,'user_name':user_name,'title': 'Print Reciept'})

class LogisticPrintReciept(DetailView):
    template_name = "logistic/logistic_print_reciept.html"
    model = Order
    context_object_name = "ord_obj"
 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Logistic.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            
        else:
            return redirect("/login/?next=/logistic_home/")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["allstatus"] = ORDER_STATUS
        return context



@login_required
def sales_person_home(request):
    user_name = request.user.sales_person
    buyers = Buyer.objects.all().order_by('-id')
    total_order=0
    
    for order in Order.objects.all():
        total_order +=order.total
        # print(total_order)
    return render(request , 'sales_person/sales_person_home.html',{'user_name':user_name, 'buyers':buyers, 'total_order':total_order})


class PaymentStatuChangeView(View):
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Sales_Person.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            
        else:
            return redirect("/login/?next=/sales_person_home/")
        return super().dispatch(request, *args, **kwargs)
    def post(self, request, *args, **kwargs):
        order_id = self.kwargs["pk"]
        order_obj = Order.objects.get(id=order_id)
        new_status = request.POST.get("status")
        order_obj.payment_status = new_status
        order_obj.save()
        return redirect(reverse_lazy("app:salesOrderDetailView", kwargs={"pk": order_id}))





@login_required
def sales_view_items(request):
    items = Item.objects.filter(qc_approved=True).order_by('-id')
    return render(request, 'sales_person/sales_items.html' ,{'items':items})




@login_required
def sales_view_approved_sales(request):
    a_orders = Order.objects.filter(payment_status=('Completed')).order_by('-id')
  
    return render(request, 'sales_person/approved_sales.html' ,{'a_orders':a_orders})


@login_required
def sales_view_pending_sales(request):
    p_orders = Order.objects.exclude(payment_status='Completed').order_by('-id')
  
    return render(request, 'sales_person/pending_sale.html' ,{'p_orders':p_orders})

class SalesOrderDetailView(DetailView):
    template_name = "sales_person/salesorderdetail.html"
    model = Order
    context_object_name = "ord_obj"
 
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and Sales_Person.objects.filter(user=request.user).exists():
            order_id = self.kwargs["pk"]
            order = Order.objects.get(id=order_id)
            
        else:
            return redirect("/login/?next=/sales_person_home/")
        return super().dispatch(request, *args, **kwargs)
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # context["allstatus"] = ORDER_STATUS
        context["Pallstatus"] = PAYMENT_STATUS
        return context

        
