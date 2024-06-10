from django.shortcuts import render,redirect
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.contrib.auth  import authenticate, login, logout
from django.contrib import messages
from django.db import IntegrityError
from django.views.decorators.csrf import csrf_protect
from .models import Channel , Video_uplode, Phone_numbers ,Verified_users , ldtable
from django.http import JsonResponse
from django.core.serializers.json import DjangoJSONEncoder
from django.contrib.sessions.backends.db import SessionStore
import json
from youtube.settings import TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN , TWILIO_PHONE_NUMBER
import random
from twilio.rest import Client

@csrf_protect

# Create your views here.
def index(request):
    videos = Video_uplode.objects.exclude(private=True)
    if request.user.is_authenticated:
        uid = request.user
        verified = False 
        check = None 
        try:
            check = Verified_users.objects.get(uid = uid)
            verified = True
        except Exception as e:
            print(e)


        try:
             # Assuming you want to get a single Channel object
            channel = Channel.objects.get(uid=uid , private=False)
            try:
                pchannel = Channel.objects.get(uid = uid , private=True)
                return render(request, 'yt1/index.html', { 'pcc': True , 'cc': True, 'pimg': pchannel.channel_image.url , 'pslug': pchannel.slug , 'img': channel.channel_image.url ,'slug': channel.slug , 'videos':videos , 'verified':verified , 'name':check.collage_id.channel_name if check else None , 'verifyslug':check.collage_id.slug if check else None})
            except Channel.DoesNotExist:
                return render(request, 'yt1/index.html', {'cc': True, 'img': channel.channel_image.url ,'slug': channel.slug , 'videos':videos , 'verified':verified , 'name':check.collage_id.channel_name if check else None , 'verifyslug':check.collage_id.slug if check else None})
        except Channel.DoesNotExist:
            try:
                pchannel = Channel.objects.get(uid = uid , private=True)
                return render(request, 'yt1/index.html', { 'pcc': True , 'cc': False, 'pimg': pchannel.channel_image.url , 'pslug': pchannel.slug , 'videos':videos , 'verified':verified , 'name':check.collage_id.channel_name if check else None , 'verifyslug':check.collage_id.slug if check else None})
            except Channel.DoesNotExist:
                return render(request, 'yt1/index.html', { 'videos':videos , 'verified':verified , 'name':check.collage_id.channel_name if check else None , 'verifyslug':check.collage_id.slug if check else None})
    return render(request, 'yt1/index.html', {'videos':videos})

def userchannel(request,slug_val):
    if request.user.is_authenticated:
        try:
            channel = Channel.objects.get(slug=slug_val)
            if channel.uid.username == request.user.username:
                videos = Video_uplode.objects.filter(cid = channel.cid)
                return render(request,'yt1/show_channel.html',{'cname':channel.channel_name , 'cdisc':channel.channel_disc, 'cimg':channel.channel_image.url , 'username': channel.uid , 'videos':videos , 'cid':channel.cid})
            else:
                return redirect('index')
            
        except Channel.DoesNotExist:
            print(" channel dose not exist how you are clicking the channel icon ")
            return redirect('index')
    else:
        return redirect('login')
    
def puserchannel(request,slug_val):
    if request.user.is_authenticated:
        try:
            channel = Channel.objects.get(slug=slug_val)
            if channel.uid.username == request.user.username:
                videos = Video_uplode.objects.filter(cid = channel.cid)
                return render(request,'yt1/show_channel.html',{ 'pcc': True , 'cname':channel.channel_name , 'cdisc':channel.channel_disc, 'cimg':channel.channel_image.url , 'username': channel.uid , 'videos':videos , 'cid':channel.cid})
            else:
                return redirect('index')
            
        except Channel.DoesNotExist:
            print(" channel dose not exist how you are clicking the channel icon ")
            return redirect('index')
    else:
        return redirect('login')    


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        fname = request.POST['fname']
        lname = request.POST['lname']
        email = request.POST['email']
        pass1 = request.POST['pass1']
        pass2 = request.POST['pass2']
        if username and fname and lname and email and pass1 and pass2:
            try:
                if len(username) > 11:
                    messages.error(request,'Username must be under 11 char and should be alpha numeric')
                    return redirect('index')
                if not username.isalnum():
                    messages.error(request,'Username should be alpha numeric')
                    return redirect('index')
                if (pass1 == pass2):
                    myuser = User.objects.create_user(username, email, pass1)
                    myuser.first_name = fname
                    myuser.last_name = lname
                    myuser.save()
                    messages.success(request, "Your iCoder has been successfully created")
                    return redirect('index')
                else:
                    messages.error(request, " Passwords do not match")
                    return redirect('index')
            except IntegrityError as e:
                messages.error(request, e)
                return redirect('index')
        else:
            messages.error(request, 'Fill all Entries..')
            return redirect('index')
    else:
        messages.error(request, 'Try again..')
        return redirect('index')

def loginuser(request):
    if request.method == 'POST':
        username = request.POST['loginusername']
        password = request.POST['pass']
        if username and password:
            try:
                user= authenticate(request , username = username , password = password)
                if user is not None:
                    login(request, user) 
                    messages.success(request, "Successfully Logged In")
                    return redirect("index")
                else:
                    messages.success(request, "Invalid credentials! Please try again")
                    return redirect("index") 
            except Exception as e:
                messages.error(request, e)
                return redirect('index')
        else:
            messages.error(request, 'Fill all Entries..')
            return redirect('index')
    else:
        messages.error(request, 'Try again..')
        return redirect('index')

def logoutuser(request):
    logout(request)
    messages.success(request, "Loged out")
    return redirect('index')

def createchannelx(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            channelname= request.POST['channelname']
            channeldisc = request.POST['channeldisc']
            channelimage = request.FILES.get('channelimage')
            uid = request.user 
            slug = "channel"+ str(uid)
            x = Channel.objects.filter(uid = uid , private = False)
            if x:
                return JsonResponse({'msg': False})
            else:
                if channelname and channeldisc and channelimage and uid:
                    try:
                        channel = Channel.objects.create( uid = uid , channel_name = channelname , channel_disc = channeldisc , channel_image = channelimage , slug = slug , private= False)
                        # messages.success(request , "Channel Created....")
                        channel.save()
                        success = True
                        return JsonResponse({'msg': success , 'img': channel.channel_image.url , 'name': channel.channel_name}, encoder=DjangoJSONEncoder)
                    except Exception as e:
                        return JsonResponse({'msg': e})
                else:
                    print("fill all entryes")
                    print(channelname)
                    print(channeldisc)
                    print(channelimage)
        else:
            print("Try again....") 
    else:
        print("ppoooyoy")

def createprivatechannelx(request):
    if request.user.is_authenticated:
        if request.method=='POST':
            collagename= request.POST['collagename']
            collagedisc = request.POST['collagedisc']
            collageimage = request.FILES.get('collageimage')
            uid = request.user 
            slug = "privatechannel"+ str(uid)
            x = Channel.objects.filter(uid = uid , private = True)
            if x:
                return JsonResponse({'msg': False})
            else:
                if collagename and collagedisc and collageimage and uid:
                    try:
                        channel = Channel.objects.create( uid = uid , channel_name = collagename , channel_disc = collagedisc , channel_image = collageimage , slug = slug , private=True)
                        # messages.success(request , "Channel Created....")
                        channel.save()
                        success = True
                        return JsonResponse({'msg': success , 'img': channel.channel_image.url , 'name': channel.channel_name}, encoder=DjangoJSONEncoder)
                    except Exception as e:
                        return JsonResponse({'msg': e})
                else:
                    print("fill all entryes")
                    print(collagename)
                    print(collagedisc)
                    print(collageimage)
        else:
            print("Try again....") 
    else:
        print("ppoooyoy")        

def uplodevideo(request,val):
    print("kaka0")
    if request.user.is_authenticated:
        if request.method == 'POST':
            channel_name = request.POST['channel']
            video = request.FILES.get('video')
            vtitle = request.POST['vtitle']
            vdisc = request.POST['vdisc']
            vthumb = request.FILES.get('vthumb')
            catogery = request.POST['Catogery']
            uid = request.user.username
            private = False
            print("kaka1")
            if channel_name and video and vtitle and vdisc and vthumb and uid:
                print("kaka2")
                try:
                    if val == 'p' :
                        ucheck = Channel.objects.get(uid = request.user , private = True)
                        private = True
                    else:
                        ucheck = Channel.objects.get(channel_name = channel_name)
                    print("kaka3")
                    if ucheck.uid.username == uid:
                        print("kaka4")
                        uplode = Video_uplode.objects.create(cid=ucheck, video = video, video_title = vtitle, video_disc = vdisc, video_thumbnail = vthumb, catogery=catogery , private = private)
                        uplode.save()
                        return JsonResponse({
                            'uplode':True, 
                            'thumbnail':uplode.video_thumbnail.url,
                            'title':uplode.video_title, 
                            'duration':uplode.video_duration,
                            'cname': uplode.cid.channel_name, 
                            'slug':uplode.slug
                            } , encoder=DjangoJSONEncoder)
                        print("DONE UPLODE............................")
                    else:
                        print("You are not the user of this channel how are you uploding video")
                        return redirect('index')
                except Exception as e:
                    print(e)
                    return redirect('index')
            else:
                print("Fill all entries")    
        else:
            print("Try again....")
    else:
        return redirect('login')
    
def uplodenumber(request):
    print("come")
    if request.user.is_authenticated:
        if request.method == 'POST':
            number = request.POST['phone_number']
            cname = request.POST['channel']
            uid = request.POST['uid']
            if number and cname and uid:
                print("recieve")
                try:
                    channel = Channel.objects.get(uid = uid , private=True)
                    if channel.uid.username == request.user.username:
                        print("verified")
                        numberuplode = Phone_numbers.objects.create(collage_id = channel , number=number)
                        numberuplode.save()
                        print("done")
                        return JsonResponse({
                            'pcc': True,
                            'msg': "Number_Uploded_Successful"
                        })
                    else:
                        pass  
                except Exception as e:
                    print(e)
                    return redirect('index')
            else:
                pass  
        else:
            pass
    else:
        pass   

session = SessionStore()     

def sendotp(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            number = request.POST['Phonenumber']
            if number:
                try:
                    check = Phone_numbers.objects.get(number=number)
                    otp = ''.join([str(random.randint(0, 9)) for _ in range(6)])
                    print(otp)
                    client = Client(TWILIO_ACCOUNT_SID,TWILIO_AUTH_TOKEN)
                    message = client.messages.create(
                        body=f'Your OTP is: {otp}',
                         from_= TWILIO_PHONE_NUMBER,
                        to=f'+91{number}' 
                    )

                    userinfo = {'user_id':request.user.username , 'number':number , 'otp':otp}
                    session['userinfo'] = userinfo
                    session.save()
                    print(session['userinfo'])
                    return JsonResponse({'sent': True})
                except Exception as e:
                    print(f'you are not subscribed to any channel{e}')
            else:
                pass
        else:
            pass   

def verify(request):
    if request.user.is_authenticated:
        if request.user.username == session['userinfo']['user_id']:
            if request.method == 'POST':
                otp = request.POST['otp']
                if otp:
                    try:
                        if otp == session['userinfo']['otp']:
                            check = Phone_numbers.objects.get(number = session['userinfo']['number'])
                            verified = Verified_users.objects.create(uid = request.user , collage_id = check.collage_id )
                            verified.save()

                            return JsonResponse({'verified':True , 'name':check.collage_id.channel_name , 'slug':check.collage_id.slug}) 

                            pass
                        else:
                            pass
                        print("otp entered")
                        pass
                    except Exception as e:
                        pass
                else:
                    pass
            else:
                pass
        else:
            pass       
    else:
        pass         

def videoplay(request,slug_val):
    video = Video_uplode.objects.get(vid = slug_val)
    print(video)
    print("get")
    sidevideos1 = Video_uplode.objects.filter(cid = video.cid)
    sidevideos2 = Video_uplode.objects.exclude(cid = video.cid)
    like = False
    dislike = False
    try:
        check = ldtable.objects.get(uid=request.user , vid = video)
        like = check.like
        dislike = check.dislike
        return render(request, 'yt1/play.html' , {'like': like , 'dislike':dislike , 'mainvideo':video , 'ownvideos': sidevideos1 , 'elsevideos':sidevideos2})
    except Exception as e:
        like = False
        dislike = False
        return render(request, 'yt1/play.html' , {'like': like , 'dislike':dislike , 'mainvideo':video , 'ownvideos': sidevideos1 , 'elsevideos':sidevideos2})

    print('getboth')

def subscribedvideos(request, slug_val):
    if request.user.is_authenticated:
        try:
            verifieduser = Verified_users.objects.get(uid = request.user)
            channel = Channel.objects.get(cid = verifieduser.collage_id.cid , private=True)
            videos = Video_uplode.objects.filter(cid = channel.cid , private=True)
            return render(request,'yt1/subscribedview.html',{'cname':channel.channel_name , 'cdisc':channel.channel_disc, 'cimg':channel.channel_image.url , 'username': channel.uid , 'cid':channel.cid , 'videos':videos})
        except Exception as e:
            return redirect('index')
        
    else:
        return redirect('index')
    
def like(request):
    if request.user.is_authenticated:
        if request.method == 'POST':
            vidslug = request.POST.get('slug')
            print(vidslug)
            vid = Video_uplode.objects.get(slug=vidslug)
            try:
                like = ldtable.objects.get(vid=vid , uid= request.user)
                if(like.like):
                    like.delete()
                    return JsonResponse({'like': False , 'dislike':False , 'none':True})
                elif(like.dislike):
                    like.like = True
                    like.dislike = False
                    like.save()

                    return JsonResponse({'like': True , 'dislike':False , 'none':False})
            except ldtable.DoesNotExist:
                newentry = ldtable.objects.create(vid = vid , uid=request.user , like=True , dislike=False)
                return JsonResponse({'like': True , 'dislike':False , 'none':False})
        else:
            pass
    else:
        pass

def dislike(request):
    print('hello')
    if request.user.is_authenticated:
        if request.method == 'POST':
            vidslug = request.POST.get('slug')
            print(vidslug)
            vid = Video_uplode.objects.get(slug=vidslug)
            try:
                dislike = ldtable.objects.get(vid=vid , uid= request.user)
                if(dislike.dislike):
                    dislike.delete()
                    return JsonResponse({'like': False , 'dislike':False , 'none':True})
                elif(dislike.like):
                    dislike.like = False
                    dislike.dislike = True
                    dislike.save()
                    return JsonResponse({'like': False , 'dislike':True , 'none':False})
            except ldtable.DoesNotExist:
                newentry = ldtable.objects.create(vid = vid , uid=request.user , like=False , dislike=True)
                return JsonResponse({'like': False , 'dislike':True , 'none':False})
        else:
            pass
    else:
        pass