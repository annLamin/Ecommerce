from django import template
from app.models import CartProduct

register = template.Library()


@register.filter
def cart_item_count(user):
    
    qs = CartProduct.objects.filter(cart__buyer=user)
    if qs.exists():
        return qs[0].product.count()
    return 0
