import django_filters
from django_filters import CharFilter
# from django_filters import SelectFilter

from .models import *

class ItemFilter(django_filters.FilterSet):
    # title= CharFilter(field_name='title', lookup_expr='icontains')
    # brand = SelectFilter(field_name='brand',lookup_expr='lte')
    class Meta:
        model = Item
        fields = {'title'}
       