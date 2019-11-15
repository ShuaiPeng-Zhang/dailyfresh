from django.contrib import admin
from django.conf.urls import url,include

urlpatterns = [
    url('admin/', admin.site.urls),
    url('user/',include(('apps.user.urls','apps.user'),namespace='user')),
    url('order/',include(('apps.order.urls','apps.order'),namespace='order')),
    url('cart/',include(('apps.cart.urls','apps.cart'),namespace='cart')),
    url('tinymce/',include('tinymce.urls')),
    url('^',include(('apps.goods.urls','apps.goods'),namespace='goods')),
]
