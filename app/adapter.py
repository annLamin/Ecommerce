from django.conf import settings
from allauth.account.adapter import DefaultAccountAdapter

class MyAccountAdapter(DefaultAccountAdapter):
    def get_login_redirect_url(self, request):
        if (request.user.user_type=='admin'):
            return '/admin_home/'
       
        elif (request.user.user_type=='buyer'):
            return '/'
        elif (request.user.user_type=='supervisor'):
            return '/supervisor_home/'
        elif (request.user.user_type=='sales_person'):
            return '/sales_person_home/'
        elif (request.user.user_type=='quality_control'):
            return '/qc_home/'
        elif (request.user.user_type=='logistic'):
            return '/logistic_home/'