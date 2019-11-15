from django.conf.urls import url,include
from apps.user import views
urlpatterns = [
    url('^register$',views.register,name='register'),
    url(r'^active/(?P<token>.*)$',views.active,name='active'),
    url(r'^loginView$',views.loginView,name='login'),
    url(r'^Logout$', views.Logout, name='logout'),
    url(r'^order$', views.userorder, name='order'),
    url(r'^address$', views.address, name='address'),
    url(r'^$',views.userinfo,name='user'),
]
