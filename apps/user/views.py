from django.shortcuts import render,redirect,reverse
import re
from apps.user.models import User,Address
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from itsdangerous import SignatureExpired
from django.conf import settings
from django.core.mail import send_mail
from django.http import HttpResponse
from celery_tasks.tasks import send_register_active_email
from django.contrib.auth import authenticate,login,logout
from django.contrib.auth.decorators import login_required
from apps.goods.models import GoodsSKU

def register(request):
    if request.method == 'GET':
        return render(request,'register.html')
    else:
        username = request.POST['user_name']
        password = request.POST['pwd']
        email = request.POST['email']
        allow = request.POST['allow']

        if not all([username,password,email]):
            return render(request,'register.html',{'errmsg':'数据不完整'})

        if not re.match(r'^[a-z0-9][\w\.\-]*@[a-z0-9\-]+(\.[a-z]{2,5}){1,2}$',email):
            return render(request,'register.html',{'errmsg':'邮箱格式不正确'})

        if allow != 'on':
            return render(request,'register.html',{'errmsg':'请同意协议'})

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            user = None

        if user:
            return render(request,'register.html',{'errmsg':'用户名已存在'})

        user = User.objects.create_user(username,email,password)
        user.is_active = 0
        user.save()

        serializer = Serializer(settings.SECRET_KEY,3600)
        info = {'confirm':user.id}
        token = serializer.dumps(info)
        token = token.decode('utf-8')

        send_register_active_email.delay(email,username,token)

        return redirect(reverse('goods:index'))

def active(request,token):
    if request.method == 'GET':
        serializer = Serializer(settings.SECRET_KEY,3600)
        try:
            info = serializer.loads(token)
            user_id = info['confirm']
            user = User.objects.get(id=user_id)
            user.is_active = 1
            user.save()
            return redirect(reverse('user:login'))
        except SignatureExpired as e:
            return HttpResponse('激活链接已过期')

def loginView(request):
    if request.method == 'GET':
        if 'username' in request.COOKIES:
            username = request.COOKIES.get('username')
            checked = 'checked'
        else:
            username = ''
            checked = ''
        return render(request,'login.html',{'username':username,'checked':checked})
    else:
        username = request.POST['username']
        pwd = request.POST['pwd']

        if not all([username,pwd]):
            return render(request,'login.html',{'errmsg':'数据不完整'})

        try:
            user = User.objects.get(username=username)
            if user:
                # 验证密码,输入明文密码
                ret = user.check_password(pwd)
                if ret:
                    if user.is_active:
                        print('User is valid,active and authenticated')
                        login(request, user)

                        next_url = request.GET.get('next',reverse('goods:index'))
                        print(next_url)
                        response = redirect(next_url)

                        remember = request.POST['remember']
                        if remember == 'on':
                            response.set_cookie('username',username,max_age=7*24*3600)
                        else:
                            response.delete_cookie('username')
                        return response
                    else:
                        print('The password is valid,but the account has been disabled')
                        return render(request, 'login.html', {'errmsg': '账户未激活'})
                else:
                    return render(request, 'login.html', {'errmsg': '用户名或密码错误'})
        except:
            return render(request, 'login.html', {'errmsg': '账户不存在'})

@login_required
def userinfo(request):
    if request.method == 'GET':
        user = request.user
        try:
            address = Address.objects.get(user=user, is_default=True)
        except:
            address = None

        from redis import StrictRedis
        sr = StrictRedis(db=7)

        #浏览历史
        history_key = 'history_%d'%user.id
        sku_ids = sr.lrange(history_key,0,4)

        goods_li = []
        for id in sku_ids:
            goods = GoodsSKU.objects.get(id=id)
            goods_li.append(goods)

        return render(request,'user_center_info.html',{'page':'user','address':address,'goods_li':goods_li})

@login_required
def userorder(request):
    if request.method == 'GET':
        return render(request,'user_center_order.html',{'page':'order'})

@login_required
def address(request):
    if request.method == 'GET':
        user = request.user
        try:
            address = Address.objects.get(user=user, is_default=True)
        except:
            address = None

        return render(request,'user_center_site.html',{'page':'address','address':address})
    else:
        receiver = request.POST['receiver']
        addr = request.POST['addr']
        zip_code = request.POST['zip_code']
        phone = request.POST['phone']

        if not all([receiver,addr,phone]):
            return render(request,'user_center_site.html',{'errmsg':'数据不完整'})
        if not re.match('^1[0-9]{10}',phone):
            return render(request,'user_center_site.html',{'errmsg':'手机格式不正确'})

        user = request.user
        try:
            address = Address.objects.get(user=user,is_default=True)
        except:
            address = None
        if address:
            is_default = False
        else:
            is_default = True

        Address.objects.create(user=user,receiver=receiver,addr=addr,
                               zip_code=zip_code,phone=phone,is_default=is_default)
        return redirect(reverse('user:address'))

@login_required
def Logout(request):
    if request.method == 'GET':
        logout(request)
        return redirect(reverse('goods:index'))