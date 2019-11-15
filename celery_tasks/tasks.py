from celery import Celery
from django.conf import settings
from django.core.mail import send_mail

app = Celery('celery_tasks.tasks',broker='redis://127.0.0.1:6379/8',backend='redis://127.0.0.1:6379/9')

@app.task
def send_register_active_email(to_email,username,token):
    subject = '欢迎使用天天生鲜'
    message = ''
    sender = settings.EMAIL_FROM
    receiver = [to_email]
    html_message = '<h1>%s , 欢迎您成为天天生鲜注册会员</h1>请点击下面链接激活您的账户<br><br>' \
                   '<a href="http://192.168.0.11:8000/user/active/%s">点击激活</a>' % (
                       username, token)
    try:
        send_mail(subject, message, sender, receiver, html_message=html_message)
    except Exception as e:
        print(e)
    # 第一个参数是欢迎信息，2.文本类正文信息3.发件人，配置信息里有4.收件人
    # 5.html类正文信息