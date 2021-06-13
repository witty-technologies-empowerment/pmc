from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from agents.models import IsAgent as an_agent, Address
from .forms import UserForm
from .models import userContact as telephn
from agents.models import IsAgent
from user.models import isNewUser as NU
from agents.models import (
    ProfileAvatar as PA, 
    ProfilePic, 
    IsVerified, 
    ProfilePic as PP,
    )
from django.dispatch import receiver, Signal
import random
from user.signals import user_current_location
from django.contrib.auth.models import User
from datetime import datetime
from datetime import timedelta  
from twilio.rest import Client
from django.conf import settings 
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string
import random
import string

#import wx
#from screeninfo import get_monitors


set_as_agent = Signal(providing_args=['user', 'telephone'])
user_Contact = Signal(providing_args=['user', 'telephone'])
profile_avatar = Signal(providing_args=['user', 'serial'])
send_otp = Signal(providing_args=['user', 'otp', 'telephone', 'email', 'lname'])
save_otp = Signal(providing_args=['user', 'otp', 'telephone', 'update'])


now = datetime.now()


def register(request):
    registered = False


    #app = wx.App()
    #width, height = wx.GetDisplaySize()
    #print(width, height)
    allowed_emails = ['gmail', 'yahoo', 'outlook', 'mail', 'zoho', 'hotmail', 'gmx', 'protonmail', 'aol', 'yandex', 'tutanota', 'icloud', 'live']
    allowed_telephone = ['080', '081', '070', '090', '091']
    if request.method == 'POST':
        action = request.POST.get('func')
        if str(action) == 'Register':
            try:
                user_form = UserForm(data=request.POST)
                fname = request.POST.get('first_name')
                lname = request.POST.get('last_name')
                user_name = request.POST.get('username')
                username = user_name.lower()
                email = request.POST.get('email')
                telephone = request.POST.get('telephone')
                pwd = request.POST.get('password')
                pwd2 = request.POST.get('re_type_password')
                agree_term = request.POST.get('agree_term')
                #username = user_name.lower()
                check_username = User.objects.filter(username=username)
                check_email = User.objects.filter(email=email)
                check_telephone = telephn.objects.filter(telephone=telephone)
                tel_prefix = telephone[0:3]
                email_used =[]
                for x in check_email:
                    email_used.append(x.email)
                firstsplit = email.split('@')
                secondsplit = firstsplit[1].split('.')
                if agree_term != 'on':
                    message = 'Hello '+username.title()+' You need to agree to our Terms of Service.'
                    context = {
                    'firstname': fname,
                    'lastname': lname,
                    'username': username,
                    'telephone': telephone,
                    'email': email,
                    'registered':False,
                    'error': message}
                    return render(request,'accounts/signup.html', context)
                elif len(pwd) > 0:
                    if pwd != pwd2:
                        message = username.title()+', Your Passwords dont match'
                    elif len(pwd) < 8:
                        left = 8 - len(pwd)
                        message = username.title()+', Your password should be above 8 charaters, You have currently used '+str(len(pwd))+' remains '+str(left)+' charaters left.'
                    elif len(pwd) > 16:
                        message = username.title()+', thats a very secure password but make it below 16 charaters, you currently used '+str(len(pwd))+'.'
                    elif str(username) in str(check_username):
                        xlist = []
                        for x in range(5):
                            value = random.randint(111, 999)
                            xlist.append(value)
                        message = 'Hmmm... Seems the Username '+username.title()+' has been taken, you can try, '+str(username+str(xlist[0]))+', '+str(username+str(xlist[1]))+', '+str(username+str(xlist[2]))+', '+str(username+str(xlist[3]))+', '+str(username+str(xlist[4]))+'.'
                    elif str(telephone) in str(check_telephone):
                        message = str(telephone)+' has been used'
                    elif str(tel_prefix) not in str(allowed_telephone):
                        message = 'Telephone prefix '+str(tel_prefix)+' is not allowed try numbers with '+str(allowed_telephone[0])+', '+str(allowed_telephone[1])+', '+str(allowed_telephone[2])+', '+str(allowed_telephone[3])+', '+str(allowed_telephone[4])+' Prefix.'
                    elif len(telephone) < 11 or len(telephone) > 12:
                        message = "Invalid Telephone Number"
                    elif str(email) in str(email_used):
                        message = "The Email - "+email.title()+" has been used"
                    elif len(secondsplit[0]) == 0 or len(secondsplit[0]) <= 2:
                        message = 'Invalid Email'
                    elif len(secondsplit[1]) == 0 or len(secondsplit[1]) <= 1:
                        message = 'Invalid Email'
                    elif str(secondsplit[0]) not in str(allowed_emails):
                            message = str(secondsplit[0])+' cant be used to create a PMC User Account, Provide any from the allowed Emails - '+str(allowed_emails[0].title())+', '+str(allowed_emails[1].title())+', '+str(allowed_emails[2].title())+', '+str(allowed_emails[3].title())+', '+str(allowed_emails[4].title())+', '+str(allowed_emails[5].title())+', '+str(allowed_emails[6].title())+', '+str(allowed_emails[8].title())+', '+str(allowed_emails[9].title())+', '+str(allowed_emails[10].title())+', '+str(allowed_emails[11])+', '+str(allowed_emails[12].title())+'.'
                    else:
                        try:
                            if user_form.is_valid():
                                user = user_form.save(commit=False)
                                user.set_password(user.password)
                                user_Contact.send(sender=None, user=username, telephone=telephone)
                                serial = random.randint(1, 70)
                                profile_avatar.send(sender=None, user=username, serial=serial)
                                otp = ran_gen(32,'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789')
                                save_otp.send(sender=None, user=username, otp=otp, telephone=telephone, update='no')
                                #username_hold(username)
                                user.save()
                                registered = True
                                otp = random.randint(100000, 999999)
                                send_otp.send(sender=None, user=username, otp=otp, telephone=telephone, email=email, lname=lname)
                                return render(request,'accounts/signup.html', {'registered':True, 'username':username})
                        except Exception as e:
                            print(e)
                            context = {
                                'firstname': fname,
                                'lastname': lname,
                                'username': username,
                                'telephone': telephone,
                                'email': email,
                                'agree_term':1,
                                'registered':False,
                                'error': str(username.title())+', Your details did not save, Try again later or Contact PMC'}
                            return render(request,'accounts/signup.html', context)
                    context = {
                        'firstname': fname,
                        'lastname': lname,
                        'username': username,
                        'telephone': telephone,
                        'email': email,
                        'agree_term':1,
                        'registered':False,
                        'error': message}
                    return render(request,'accounts/signup.html', context)
                else:
                    message = username.title()+', the Passwords cant be empty.'
                    context = {
                        'firstname': fname,
                        'lastname': lname,
                        'username': username,
                        'telephone': telephone,
                        'email': email,
                        'agree_term': 1,
                        'registered':False,
                        'error': message}
                    return render(request,'accounts/signup.html', context)
            except Exception as e:
                message = 'All fields cant be Empty'
                context = {
                    'firstname': fname,
                    'lastname': lname,
                    'username': username,
                    'telephone': telephone,
                    'email': email,
                    'agree_term': 0,
                    'registered':False,
                    'error': message}
                return render(request,'accounts/signup.html', context)
        else:
            start = request.POST.get('email')
            context = {
                'email': start,
                'registered':False,
                'agree_term': 0,
                }
            return render(request,'accounts/signup.html', context)
    else:
        context = {
        'registered':False,
        'agree_term': 0,}
        return render(request,'accounts/signup.html', context)
            


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        user_str = str(username).lower()
        password = request.POST.get('password')
        pass_lower = str(password).lower()
        check = IsVerified.objects.filter(user=user_str)
        if str(user_str)+' is verified' in str(check):
            user = authenticate(username=user_str, password=password)
            if user:
                if user.is_active:
                    login(request, user)
                    #user_current_location.send(self.request.user, request=self.request)
                    return HttpResponseRedirect(reverse('users:request'))
                else:
                    response = "Your account was inactive."
                    return render(request, 'accounts/login.html', {'response': response})
            else:
                response = "Invalid Login details"
                return render(request, 'accounts/login.html', {'response': response})
        else:
            check = an_agent.objects.filter(user=username)
            valuex = 'Nil'
            for value in check:
                valuex = value.is_agent
            if valuex == False:
                Url = str("/agents/new_agent_login/verify/new-account/for-"+username)
                return HttpResponseRedirect(Url)
            else:
                Url = str("/accounts/registration/user/verify/new-account/for-"+username)
                return HttpResponseRedirect(Url)
    else:
        return render(request, 'accounts/login.html')


def new_user_login(request, username, path):
    check_username = User.objects.filter(username=username)
    check_verify = IsVerified.objects.filter(user=username)
    for e in check_username:
        u_email = e.email
        lname = e.last_name
    tel = []
    telephone = []
    for x in check_verify:
        xtele = x.telephone
        tel.append(x.telephone)
        telephone.append(x.telephone)
    verified = 0
    if str(username) in str(check_verify):
        verified = 1
        n = tel[0]
        n0_3 = n[0:4]
        n8_10 = n[8:11]
        shrtel = u_email
        if request.method == 'POST':
            veri = request.POST.get('verify')
            signin = request.POST.get('signin')
            if veri == 'Verify':
                otp = request.POST.get('otp')
                if otp == '':
                    message = 'Field is required'
                    return render(request, 'accounts/login-1.html', {'message1':message,'fake': username, 'shrtel':shrtel, 'username':username, 'verified':verified, 'path':path})
                check = IsVerified.objects.filter(telephone=telephone[0])
                for red in check:
                    otpx = red.otp
                if str(username)+' is not verified' in str(check):
                    if int(otp) == int(otpx):
                        for item in check:
                            details = IsVerified()
                            details.pk = item.pk
                            details.user = item.user
                            details.otp = item.otp
                            details.verified = True
                            details.telephone = item.telephone
                            details.created = item.created
                            details.save()
                        if path == 'agent':
                            set_as_agent.send(sender=None, user=username)
                        verified = 2
                        message = 'Congratulations '+username.title()+' your account is now verified' 
                        return render(request, 'accounts/login-1.html', {'username':username,'verified': verified, 'message':message, 'path':path})
                    else:
                        message = 'The OTP '+str(otp)+' you entered is Invalid'
                        return render(request, 'accounts/login-1.html', {'username':username,'verified':verified, 'shrtel':shrtel, 'message1':message, 'path':path})
                else:
                    message = username.title()+' must have been verified' 
                    disabled = 'disabled'
                    return render(request, 'accounts/login-1.html', {'otp':otp, 'disabled':disabled, 'username':username,'verified':verified, 'shrtel':shrtel, 'message':message, 'path':path})
            elif veri == 'Resend':
                check = IsVerified.objects.filter(user=username)
                for otp in check:
                    otpx = otp.otp
                now = datetime.now()
                use = now + timedelta(minutes=5)
                time = use.strftime("%b %d, %Y %H:%M:%S") 
                send_otp.send(sender=None, user=username, otp=otpx, telephone=xtele, email=u_email, lname=lname)
                message = 'Your code has been resent'
                return render(request, 'accounts/login-1.html', {'username':username,'verified':verified, 'shrtel':shrtel, 'message3':message, 'retry_time':time, 'path':path})
            elif str('Log in') in str(signin):
                username = request.POST.get('username').lower()
                password = request.POST.get('password')
                user = authenticate(username=username, password=password)
                if user:
                    if user.is_active:
                        item = NU()
                        item.user = username
                        item.save()
                        login(request, user)
                        return HttpResponseRedirect(reverse('users:request'))
                    else:
                        message = username.title()+', Your account has been disabled'
                        return render(request, 'accounts/login-1.html', {'message1':message, 'username':username,'verified':2, 'path':path})
                else:
                    message = 'Invalid Login Details'
                    return render(request, 'accounts/login-1.html', {'message2':message, 'username':username,'verified':2, 'path':path})
        else:
            return render(request, 'accounts/login-1.html', {'username':username,'verified':verified, 'shrtel':shrtel, 'path':path})
    else:
        message = 'Sorry! No verification status found for '+username.title() +', try reverifying your account'
        return render(request, 'accounts/login-1.html', {'message1':message,'fake': username,'verified':verified, 'path':path})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('users:request'))


def profile(request, username, pk):
    profileView = True
    login = str(request.user).lower()
    profile_icon = PP.objects.filter(user=username)
    research = User.objects.filter(username=username)
    if str(login) != str('anonymoususer'):
        authenticated = True
        if login == username:
            find = User.objects.filter(username=username)
            context = {
                'username':username,
                'profile':find,
                'profile_image':profile_icon,
                'authenticated':authenticated,
                'profileView':False,
            }
            return render(request, 'accounts/profile.html', context)
        else:
            find = User.objects.filter(username=username)
            context = {
                'username':username,
                'profile':find,
                'profile_image':profile_icon,
                'authenticated':authenticated,
                'profileView':profileView,
            }
            return render(request, 'accounts/profile.html', context)
        profileView = True
        check_user = str(request.user).lower()
    else:
        authenticated = False
        if check_user != username:
            find = User.objects.filter(username=username)
            for items in find:
                username = items.username
                pk = items.pk
        context = {
            'username':username,
            'pk':pk,
            'not':'not',
            'authenticated':authenticated,
            'profileView':profileView,
        }
        return render(request, 'accounts/profile.html', context)


def recover(request):
    return render(request, 'accounts/recover.html')


""" -----------------Functions ---------------------- """

@receiver(user_Contact)
def user_contact_save(sender, **kwargs):
    data = kwargs
    details = telephn()
    details.user = data['user']
    details.telephone = data['telephone']
    details.save()
    print("Saved!")


@receiver(profile_avatar)
def profile_avatar_save(sender, user, serial, **kwargs):
    print('image no '+str(serial))
    image = PA.objects.filter(title=serial)
    for item in image:
        details = ProfilePic()
        details.user = user
        details.picture = item.image
        details.save()
        print("Avatar Saved!")


@receiver(set_as_agent)
def now_an_agent(sender, **kwargs):
    data = kwargs
    details = IsAgent()
    details.user = data['user']
    details.is_agent = True
    details.save()
    print("New Agent "+data['user']+" Saved!")


@receiver(save_otp)
def otp_saved(sender, user, otp, telephone, update, **kwargs):
    tel = telephone[0]
    if update  == 'yes':
        get = IsVerified.objects.filter(telephone=telephone)
        for items in get:
            details = IsVerified()
            details.pk = items.pk
            details.user = items.user
            details.otp = otp
            details.telephone = items.telephone
            details.created = items.created
            details.save()
    else:
        details = IsVerified()
        details.user = user
        details.otp = otp
        details.telephone = telephone
        details.created = now
        details.save()

@receiver(send_otp)
def sending_sms(sender, user, otp, telephone, email, lname, **kwargs):
    subject = 'Activate your account [PassMeCash]'
    c = {   'user': user,  
                    'otp' : otp,
                    'name': lname,}   
    text_content = render_to_string('email_signup.txt', c)
    html_content = render_to_string('email_signup.html', c)
    recipient_list = [email]
    email = EmailMultiAlternatives(subject, text_content, 'PassMeCash <noreply@passmecash.com>', recipient_list, headers={'Message-ID': 'Activate your account [PassMeCash]'})
    email.attach_alternative(html_content, "text/html")
    email.send()
    save_otp.send(sender=None, user=user, otp=otp, telephone=telephone, update='yes') 


    # RTime = now.strftime("%H:%M:%S")
    # RDate = now.strftime("%d-%B-%Y")
    # #account_sid = 'AaXVQMNw2GjHbCMVbG86p22Pur8zYwS4K9' #+15402740766
    # #auth_token = 'd56a76d9bece6121967015dfa45c6a98'

    # #account_sid = 'AC058e3ac8b1386c28177b7e856603a1b2'
    # #auth_token = 'd046384012799d57cf6c07b99ec31ad1' #'+12054488520'
    # tele = '+234'+telephone[1:]
    # account_sid = 'ACb799c4197deaaf52c87f41c13808b51e' 
    # auth_token = '65cb9b3a4161a397dd8c1f68a0aa0322'
    # superadmin = '+2348106529115'
    # sam = '+2348067331567'
    # otp = otp
    # #url = 'http://127.0.0.1:1236/agents/request/from/'+name+'/to/pass-'+str(amount)+'/'+str(RCode)+'/'+str(RDate)+'/'+str(RTime)
    # # Your Account SID from twilio.com/console
    # account_sid = account_sid
    # # Your Auth Token from twilio.com/console
    # auth_token = auth_token
    # body = 'Hello ' +user+',\nYour PassMeCash verification code is: '+str(otp)+'\nThis Code will expire in 5 minutes.'
    # client = Client(account_sid, auth_token)
    # message = client.messages.create(from_='+17652384811', body=body, to=tele)
    # if message.sid.startswith("SM"):
    #     print("OTP Sent Successfully")
    #     save_otp.send(sender=None, user=user, otp=otp, telephone=telephone, update='yes')
    #     print("otp - ", str(otp))
    # else:
    # # print(message.sid)
    #     print("SORRY!, Could not send your otp message")


#================= FUCTIONS =================#
def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))