from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('signup', views.signup, name='signup'),
    path('login', views.loginuser, name='login'),
    path('logout', views.logoutuser, name='logoutuser'),
    path('createchannel',views.createchannelx, name='createchannel'),
    path('createprivatechannel',views.createprivatechannelx, name='createprivatechannel'),
    path('uplodevideo/<str:val>',views.uplodevideo, name='uplodevideo'),
    path('uplodenumber',views.uplodenumber, name='uplodenumber'),
    path('sendotp',views.sendotp, name='sendotp'),
    path('verify',views.verify, name='verify'),
    path('like',views.like, name='like'),
    path('dislike',views.dislike, name='dislike'),
    path('channel/<str:slug_val>',views.userchannel, name='userchannel'),
    path('privatechannel/<str:slug_val>',views.puserchannel, name='userchannel'),
    path('play/<str:slug_val>',views.videoplay, name='videoplay'),
    path('subscribedvideos/<str:slug_val>', views.subscribedvideos , name="subscribedvideos")
]
