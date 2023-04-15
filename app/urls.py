from django.urls import path
from django.conf import settings
from django.conf.urls.static import static

from . import views 
from .views import *
app_name = 'app'
urlpatterns = [ 
   
    path('', views.home, name="home"),
    path("product/<slug:slug>/", ItemDetailView.as_view(), name="product"),
    path("search/", SearchView.as_view(), name="search"),
    path('shop/', views.shop, name="shop"),
    path('product-list/', views.product_list, name='product-list'),
    path('category-product-list/<int:cat_id>/', views.category_product_list, name="category-product-list"),
    path('brand-product-list/<int:brand_id>/', views.brand_product_list, name="brand-product-list"),
    path('logout/', logout_view.as_view(), name ='userLogout'),
   
   
    #buyers
    path('buyer_home/', views.buyer_home, name="buyer-home"),
    path('order-summary/', OrderSummaryView.as_view(), name="order-summary"),
    # path("product/<slug:slug>/", ItemDetailView.as_view(), name="product"),
    path("add-to-cart/<int:pro_id>/", add_to_cart.as_view(), name="addtocart"),
    path("manage-cart/<int:cp_id>/", ManageCartView.as_view(), name="managecart"),
    path("empty-cart/", EmptyCartView.as_view(), name="emptycart"),
    # path('buyerallproducts/', BuyerAllproductView.as_view(), name="buyer-allproduct-product"),
    # path('request_item/', views.request_item, name="Buyer-Request-Form"),
    path('checkout/', CheckoutView.as_view(), name="checkout"),
    path("user_registration/",views.user_registration, name="userregistration"),
    path("profile/", BuyerProfileView.as_view(), name="buyerprofile"),
    path("profile/<int:pk>/", BuyerOrderDetailView.as_view(), name="buyerorderdetail"),
    path("contact/",views.contact, name="Contact-Us"),
    # path("edit_buyer/<int:uid>/", views.edit_buyer, name="editbuyer"),

    
    #admin
    path('confirm_delete_cat/<int:cid>/', views.confirm_delete_cat, name = 'Admin-Admin-Home'),
    path('confirm_delete_bra/<int:bid>/', views.confirm_delete_bra, name = 'Admin-Admin-Home'),
    path('confirm_delete_news/<int:nid>/', views.confirm_delete_news, name = 'Admin-Admin-Home'),
    path('confirm_delete_advert/<int:aid>/', views.confirm_delete_advert, name = 'Admin-Admin-Home'),
    path('admin_home/', views.admin_home, name="Home-Page"),
    path('admin_add_product/', views.admin_add_product, name="admin_add_product"),
    path('admin_edit_product/<int:pid>/', views.edit_product, name = 'Edit-Product'),
    path('admin_edit_news/<int:nid>/', views.admin_edit_news, name = 'Edit-News'),
    path('admin_edit_advert/<int:aid>/', views.admin_edit_advert, name = 'Edit-Advert'),
    path('admin_edit_product_quantity/<int:pid>/', views.edit_product_quantity, name = 'Edit-Product'),
    path('admin_add_category/', views.admin_add_category, name="admin_add_category"),
    path('admin_edit_category/<int:cid>/', views.edit_category, name = 'Edit-Category'),
    path('admin_add_brand/', views.admin_add_brand, name="admin_add_brand"),
    path('admin_edit_brand/<int:bid>/', views.edit_brand, name = 'Edit-Brand'),
    path('admin_edit_attribute/<int:aid>/', views.edit_attribute, name = 'Edit-Attribute'),
    path('admin_add_news/', views.admin_add_news, name="admin_add_news"),
    path('admin_view_news/', views.admin_view_news, name="admin_view_news"),
    path('admin_view_advert/', views.admin_view_advert, name="admin_view_advert"),
    path('admin_view_contacts/', views.admin_view_contacts, name="admin_view_contact"),
    path('admin_add_advert/', views.admin_add_advert, name="admin_add_advert"),
    path('admin_add_attributes/', views.admin_add_attributes, name="admin_add_attributes"),
    path('admin_view_attributes/', views.admin_view_attributes, name="admin_view_attribute"),
    path('admin_add_sales/', views.admin_add_sales, name="admin_add_sales"),
    path('admin_add_logistic/', views.admin_add_logistic, name="admin_add_logistic"),
    path('admin_view_sales/', views.admin_view_sales, name="admin_view_sales"),
    path('admin_view_users/', views.admin_view_users, name="admin_view_users"),
    path('admin_view_logistics/', views.admin_view_logistics, name="admin_view_logistics"),
    path('all_orders/',views.orders, name = 'orders'),
    path('admin_view_products/', views.admin_view_products, name="admin_view_products"),
    path('admin_view_category/', views.admin_view_category, name="admin_view_category"),
    path('admin_view_brand/', views.admin_view_brand, name="admin_view_brand"),
    path('admin_view_customers/', views.admin_view_customers, name="admin_view_customers"),
    path('admin_view_new_products/', views.admin_view_new_products, name="admin_view_new_products"),
    # path('admin_view_supervisor/', views.admin_view_supervisor, name="Home-Page"),
    # path('admin_view_sellers/', views.admin_view_sellers, name="Home-Page"),
    # path('admin_report/', views.admin_report, name="report"),
    # path('admin_view_q_controllers/', views.admin_view_q_controllers, name="Home-Page"),
    # path('admin_view_sales_persons/', views.admin_view_sales_persons, name="Home-Page"),
    # path('admin_view_buyers/', views.admin_view_buyers, name="Home-Page"),
    # path('admin_approved_items/', views.admin_approved_items, name="Home-Page"),
    # path('admin_view_request_items/', views.admin_view_request_items, name="Home-Page"),
    # path('admin_pending_products/', views.admin_pending_products, name="Home-Page"),
    # path('admin_pending_sales/', views.admin_pending_sales, name="Home-Page"),
    path("admin_pending_sales/<int:pk>/", AdminOrderDetailView.as_view(), name="adminorderdetail"),
    # path('admin_approved_sales/', views.admin_approved_sales, name="Home-Page"),
    # path("admin_approved_sales/<int:pk>/", AdminapprovedOrderDetailView.as_view(), name="adminapprovedorderdetail"),
    # path('admin_view_order/', views.admin_view_order, name="Home-Page"),
    path("admin_view_order/<int:pk>/", AdminallOrderDetailView.as_view(), name="adminallorderdetail"),

   # Logistic
    path('logistic_home/', views.logistic_home, name="logistic-home") ,
    path('logistic_view_approved_sales/', views.logistic_view_approved_sales,name ='approved-home'),
    path('logistic_view_approved_sales/<int:pk>/', LogisticOrderDetailView.as_view(), name="logisticOrderDetailView"),
    path("logistic_view_approved_sales-<int:pk>-change/",LogisticOrderStatuChangeView.as_view(), name="logisticorderstatuschange"),
    path('logistic_view_pending_sales/', views.logistic_view_pending_sales,name ='pending-home'),
    path('logistic_print_reciept/<int:pk>/', LogisticPrintReciept.as_view(), name="Print-Reciept"),
   

  
    #Sales Person urls
    path('sales_person_home/', views.sales_person_home, name="Home-Page"),
    path('sales_view_items/', views.sales_view_items, name="Home-Page"),
    path('sales_view_approved_sales/', views.sales_view_approved_sales, name="Approved_sales"),
    path('sales_view_approved_sales/<int:pk>/', SalesOrderDetailView.as_view(), name="salesOrderDetailView"),
    path('sales_view_pending_sales/', views.sales_view_pending_sales, name="pending_sales"),
    path("sales_view_approved_sales-<int:pk>-change/",PaymentStatuChangeView.as_view(), name="paymentstatuschange"),

    # path('sales_view_request_item/', views.sales_view_request_item, name="sales_view_request"),
    # path('sales_view_buyers/', views.sales_view_buyers, name="Home-Page"),
    # path('sales_view_items/', views.sales_view_items, name="Home-Page"),
    # path('sales_view_sellers/', views.sales_view_sellers, name="Sellers"),
    # path('sales_view_approved_sales/', views.sales_view_approved_sales, name="Approved_sales"),
    # path('sales_view_approved_sales/<int:pk>/', SalesOrderDetailView.as_view(), name="salesOrderDetailView"),
    # path('sales_view_pending_sales/', views.sales_view_pending_sales, name="pending_sales"),
    # path("sales_view_approved_sales-<int:pk>-change/",PaymentStatuChangeView.as_view(), name="paymentstatuschange"),

   
]


