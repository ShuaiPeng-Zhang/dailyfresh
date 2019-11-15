from django.conf.urls import url,include
from apps.goods import views

urlpatterns = [
    url(r'^$',views.index,name='index'),
]
