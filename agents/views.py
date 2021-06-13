from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.shortcuts import render
from django.contrib.auth.models import User
from accounts.forms import UserForm
from accounts.models import userContact as telephn
from .models import (IsAgent, 
    Address, Profile, 
    RequestDetail as RD, 
    ProfilePic as PP,
    fund, 
    rating,
    ProfileAvatar as PA,
    IsVerified,
    InAcct,
    Veri as veri,
    )
from twilio.rest import Client
from django.dispatch import receiver, Signal
from .utils import create_agent_code#, smsModule
import requests
import json
from accounts.models import userContact
from datetime import datetime
from datetime import timedelta 
from .agent_rate import UpdateAgentRating
import random
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from .optsms import opt
import random
import string
from django.core.mail import EmailMultiAlternatives
from django.template import Context
from django.template.loader import render_to_string


user_Contact = Signal(providing_args=['user', 'is_agent'])
set_as_agent = Signal(providing_args=['user', 'telephone'])
profile_avatar = Signal(providing_args=['user', 'serial'])
send_otp = Signal(providing_args=['user', 'otp', 'telephone', 'email', 'lname'])
save_otp = Signal(providing_args=['user', 'otp', 'telephone', 'update'])

UpdateAgentRating()

def username_hold(username):
    return username

now = datetime.now()

def register(request):
    registered = False
    allowed_emails = ['gmail', 'yahoo', 'outlook', 'mail', 'zoho', 'hotmail', 'gmx', 'protonmail', 'aol', 'yandex', 'tutanota', 'icloud', 'live']
    allowed_telephone = ['080', '081', '070', '090', '091']
    if request.method == 'POST':
        try:
            user_form = UserForm(data=request.POST)
            fname = request.POST.get('first_name')
            lname = request.POST.get('last_name')
            user__name = request.POST.get('username')
            username = user__name.lower()
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
                return render(request,'agents/agents_signup.html', context)
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
                        message = str(secondsplit[0])+' cant be used to create a PMC User Account, Provide any from the allowws Emails - '+str(allowed_emails[0].title())+', '+str(allowed_emails[1].title())+', '+str(allowed_emails[2].title())+', '+str(allowed_emails[3].title())+', '+str(allowed_emails[4].title())+', '+str(allowed_emails[5].title())+', '+str(allowed_emails[6].title())+', '+str(allowed_emails[8].title())+', '+str(allowed_emails[9].title())+', '+str(allowed_emails[10].title())+', '+str(allowed_emails[11])+', '+str(allowed_emails[12].title())+'.'
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
                            return render(request,'agents/agents_signup.html', {'registered':True, 'username':username})
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
                        return render(request,'agents/agents_signup.html', context)
                context = {
                    'firstname': fname,
                    'lastname': lname,
                    'username': username,
                    'telephone': telephone,
                    'email': email,
                    'agree_term':1,
                    'registered':False,
                    'error': message}
                return render(request,'agents/agents_signup.html', context)
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
                return render(request,'agents/agents_signup.html', context)
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
            return render(request,'agents/agents_signup.html', context)
    
    else:
        context = {
        'registered':False,
        'agree_term': 0,}
        return render(request,'agents/agents_signup.html', context)



def new_agent_login(request, username):
    check_username = User.objects.filter(username=username)
    check_verify = IsVerified.objects.filter(user=username)
    tel = []
    telephone = []
    for x in check_verify:
        tel.append(x.telephone)
        telephone.append(x.telephone)
    verified = 0
    if str(username) in str(check_verify):
        verified = 1
        n = tel[0]
        n0_3 = n[0:4]
        n8_10 = n[8:11]
        shrtel = str(n0_3)+'xxxx'+str(n8_10)
        if request.method == 'POST':
            veri = request.POST.get('verify')
            signin = request.POST.get('signin')
            if veri == 'Verify':
                otp = request.POST.get('otp')
                print(veri)
                print(otp)
                check = IsVerified.objects.filter(telephone=telephone[0])
                for red in check:
                    otpx = red.otp
                print(check)
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
                        verified = 2
                        message = 'Congratulations '+username.title()+' your account is now verified' 
                        set_as_agent.send(sender=None, user=username)
                        return render(request, 'agents/agents_login.html', {'username':username,'verified': verified, 'message':message})
                    else:
                        message = 'The OTP '+str(otp)+' you entered is Invalid'
                        return render(request, 'agents/agents_login.html', {'username':username,'verified':verified, 'shrtel':shrtel, 'message1':message})
                else:
                    message = username.title()+' must have been verified' 
                    disabled = 'disabled'
                    return render(request, 'agents/agents_login.html', {'otp':otp, 'disabled':disabled, 'username':username,'verified':verified, 'shrtel':shrtel, 'message2':message})
            elif str('Log in') in str(signin):
                username = request.POST.get('username').lower()
                password = request.POST.get('password')
                user = authenticate(username=username, password=password)
                if user:
                    if user.is_active:
                        login(request, user)
                        return HttpResponseRedirect(reverse('agents:new_profile'))
                    else:
                        message = username.title()+', Your account has been disabled'
                        return render(request, 'agents/agents_login.html', {'message1':message, 'username':username,'verified':2,})
                else:
                    message = 'Invalid Login Details'
                    return render(request, 'agents/agents_login.html', {'message2':message, 'username':username,'verified':2,})
        else:
            return render(request, 'agents/agents_login.html', {'username':username,'verified':verified, 'shrtel':shrtel})
    else:
        message = 'Sorry! No verification details found for '+username.title() 
        return render(request, 'agents/agents_login.html', {'message1':message,'fake': username,'verified':verified})
        
        


@login_required
def profile_add(request):
    username = request.user
    user_str = str(username).lower()
    try:
        check_agent = IsAgent.objects.get(user=user_str)
    except Exception as e:
        errordict1 = {}
        errorList = []
        title = 'Access Denied'
        error = 'You are not authorised to view this page'
        errordict1['title'] = title
        errordict1['message'] = error
        errorList.append(dict(errordict1))
        return render(request, 'user/request.html', {'errordict1': errorList})
        #return HttpResponseRedirect(reverse('users:request'))
    print(check_agent)
    if str(user_str) in str(check_agent):
        verified = False
        if request.method == 'POST':
            street = request.POST.get('street')
            city = request.POST.get('city')
            state = request.POST.get('state')
            street = str(street)
            city = str(city)
            print(street,city,state)
            state = str(state)
            validate = Address.objects.filter(user=user_str)
            if str(user_str) in str(validate):
                errorList =[]
                errordict ={}
                title = 'Your have already completed this action'
                error = 'If your wish to update visit the Account Update'
                errordict['title'] = title
                errordict['message'] = error
                errorList.append(dict(errordict))
                return HttpResponseRedirect(reverse('agents:dashboard'))
            else:
                # load_agent_location
                help_message = "Update your Profile with your Location"
                place = street + ", " + city + ", " + state
                url = "https://us1.locationiq.com/v1/search.php"
                data = {
                    'key': 'pk.d727acbbe82adec8c038afc106470c2b',
                    'q': place,
                    'format': 'json'}
                response = requests.get(url, params=data)
                data = json.loads(response.text)
                latitude = data[0]['lat']
                longitude = data[0]['lon']

                # loading IP_Address
                ip_request = requests.get('https://get.geojs.io/v1/ip.json')
                my_ip = ip_request.json()['ip']
                verified = True

                # saving data
                address = Address()
                address.user = user_str
                address.street = street
                address.city = city
                address.state = state
                address.ip_address = my_ip
                address.latitude = latitude
                address.longitude = longitude
                address.verified = verified
                address.save()
                print("Saved!")
                create_agent_code.send(sender=None, user=user_str)
                return HttpResponseRedirect(reverse('agents:dashboard'))
    else:
        errordict1 = {}
        errorList = []
        title = 'Access Denied'
        error = 'You are not authorised to view tha page'
        errordict1['title'] = title
        errordict1['message'] = error
        errorList.append(dict(errordict1))
        return render(request, 'user/request.html', {'errordict1': errordict1})
    return render(request, 'agents/new_profile.html', )


@login_required
def dashboard(request):
   
    username = request.user
    user_str = str(username).lower()
    isAgent = IsAgent.objects.filter(user=user_str, is_agent=True)
    profile_icon = PP.objects.filter(user=user_str)
    get_fund = fund.objects.filter(user=user_str)
    for x in get_fund:
        amt1 = x.can_remite
        amt2 = x.balance
    pec = (amt2 / amt1)*100
    xd = str(amt2)[-3:]
    xc = str(amt2)[:2]
    if int(amt2) >= 10000:
        amt2 = xc+','+xd
    elif int(amt2) > 0:
        amt2 = str(amt2)[:1]+','+xd
    else:
        amt2 = '0'
    alertLIST = []
    alertdict = {}

    telephone = userContact.objects.filter(user=user_str)
    location = Address.objects.filter(user=user_str)
    transAcc = RD.objects.filter(user=user_str)
    count = RD.objects.filter(user=user_str,).count()
    page = request.GET.get('page', 1)
    paginator = Paginator(transAcc, 10)
    if str(user_str) in str(isAgent):
        if request.method == 'POST':
            limit = request.POST.get('set_limit')
            if limit.isdigit():
                currentLimit = fund.objects.filter(user=user_str)
                if int(limit) == 0:
                    title = 'An Error has occured'
                    text = 'We could not set your new request limit to '+str(limit)
                    icon = 'error'
                else:
                    limit = int(limit)
                    if str(limit) <= str(50000):
                        roundVal = round(limit, -3)
                        if roundVal == limit:
                            if str(user_str) in str(currentLimit):
                                try:
                                    for items in currentLimit:
                                        details = fund()
                                        details.pk = items.pk
                                        details.user = user_str
                                        details.can_remite = limit
                                        details.balance = limit
                                        details.created = now
                                        details.save()
                                        title = 'Request Limit Updated'
                                        text = 'Your New Request Limit has been set to '+str(limit)
                                        icon = 'success'
                                except Exception:
                                    title = 'An Error has occured'
                                    text = 'We could not set your new request limit to '+str(limit)
                                    icon = 'error'
                            else:
                                try:
                                    details = fund()
                                    details.user = user_str
                                    details.can_remite = limit
                                    details.balance = limit
                                    details.created = now
                                    details.save()
                                    title = 'New Request Limit Updated'
                                    text = 'Congratulation '+str(username).title()+' you have successfully set your very first Request limit to  '+str(limit)+' now sit back and wait for your request to pop in ... '
                                    icon = 'success'
                                except Exception:
                                    title = 'An Error has occured'
                                    text = 'We could not set your new request limit to '+str(limit)
                                    icon = 'error'
                        else:
                            roundValDown = roundVal-1000
                            title = 'An Error has occured'
                            text = "You cant set your request Limit with N"+str(limit)+", make your request in multiple of N1,000, you can try N"+str(roundValDown)+" or N"+str(roundVal)+"."
                            icon = 'error'
                    else:
                        title = 'An Error has occured'
                        text = "Please make a request limit below N50,000"
                        icon = 'error'
            else:
                cov = str(user_str).title()
                title = 'An Error has occured'
                text = "Cmon "+cov+" you cant set your request limit to "+str(limit)
                icon = 'error'
            alertdict['title'] = title
            alertdict['text'] = text
            alertdict['icon'] = icon
            alertLIST.append(dict(alertdict))
            return render(request, 'agents/agent_home.html', {'alertLIST': alertLIST})
        else:
            try:
                tableList = paginator.page(page)
            except PageNotAnInteger:
                tableList = paginator.page(1)
            except EmptyPage:
                tableList = paginator.page(paginator.num_pages)
            acctrate = rating.objects.filter(user=user_str)

            t=0
            a=0
            d=0
            e=0
            z={}
            zz=[]
            c={}
            counted=[]
            for data in transAcc:
                #print(data.user+' Transaction '+data.rcode+' from '+str(data.customer))
                t+=1
                if data.has_accepted:
                    #print('Accepted = ' + str(data.has_accepted))
                    a+=1
                elif data.has_declined:
                    #print('Accepted = ' + str(data.has_accepted)+' was Declined')
                    d+=1
                else:
                    #print('Accepted = ' + str(data.has_accepted)+' Expired')
                    e+=1
                print(str(a),str(e),str(d)+'/'+str(t))
            z['total']=t
            z['accept']=a
            z['declined']=d
            z['expired']=e
            zz.append(dict(z))
            for num in range(count+1):
                counted.append(num)
            if t != 0:
                rate1={}
                rate2={}
                rate3={}
                acctrate={}
                acc = (a/t)*100
                dec = (d/t)*100
                exp = (e/t)*100
                cal = int((t-e)/t*100)
                acctrate['rating']=cal
                rate1['rating']=int(acc)
                rate1['rating1']=acc
                rate2['rating'] = int(dec)
                rate2['rating2'] = dec
                rate3['rating'] = int(exp)
                rate3['rating3'] = exp
                print(acc,dec,exp,cal)
            else:
                rate1=0
                rate2=0
                rate3=0
                acctrate={}
                cal = 0
                acctrate['rating'] = cal
            user_get = request.user
            user_use = str(user_get).lower() 
            avilfund = InAcct.objects.filter(user=user_use)
            if str('<QuerySet []>') in str(avilfund) :
                money = 0
                profit = 0
            else:
                for data in avilfund:
                    money = int(data.balance)
                    profit = float(data.xtrafund)
            profit = int(profit)
            if money >= 10000:
                ready = "yes"
            else:
                ready = "no"
            total = money + profit
            print('sasasa',profile_icon)
            context = {
                'tranAcc':transAcc,
                'table10': tableList,
                'telephone': telephone,
                'location': location,
                'zz':zz,
                'count':counted,
                'rating':rate1,
                'rating2':rate2,
                'rating3':rate3,
                'arating': acctrate,
                'profile_image':profile_icon,
                'moneyavil':money,
                'pec':int(pec),
                'amt2':amt2,
                'page_id':'Dashborad',
                'profit':profit,
                'dashboard': True,
                'ready':ready,
                'total':total
            }
            return render(request, 'agents/agent_home.html', context)
    else:
        return HttpResponseRedirect(reverse('users:request'))


@login_required
def userRequest(request,user,amount,RCode,RDate,RTime):
    xList = []
    aa = []
    xdata = []
    now = datetime.now()
    username = request.user
    user_str = str(username).lower()
    profile_icon = PP.objects.filter(user=user_str)
    code = RD.objects.filter(rcode=RCode)
    for data in code:
        numSaved = data.n
        xList.append(numSaved)
    num = xList
    num = int(num[0])
    ax = RTime.split(":")
    aa.append(ax[0])
    aa.append(ax[1])
    currentTimeX = now.strftime("%H:%M")
    currentTime = now.strftime("%H:%M:%S")
    currentTimeSplited = currentTimeX.split(":")
    ab = '00'
    if aa[1].startswith('0'):
        if int(aa[1]) == 00:
            cc = int(aa[1]) + 5
            if str(aa[1]) == ab:
                if int(aa[0]) >= 23:
                    nowTime = '00:' + str(0) + str(cc)
                    xdata.append(nowTime)
                    print(nowTime)
                else:
                    nowTime = str(aa[0]) + ':' + str(0) + str(cc)
                    xdata.append(nowTime)
                    print(nowTime)
        else:
            cc = int(aa[1]) + 5
            if cc < 10:
                nowTime = str(aa[0])+':'+str(0)+str(cc)
                xdata.append(nowTime)
                print(nowTime)
            else:
                nowTime = str(aa[0])+':'+str(cc)
                xdata.append(nowTime)
                print(nowTime)
    if int(aa[1]) == 55:
        ee = int(aa[0]) + 1
        if int(aa[0]) >= 23:
            pass
            #print('n'+str(final) + ' - ' + str(aa[0]) + str(aa[1]) + ' - Time is now ' + '00:' + str(0)+str(00))
        else:
            nowTime = str(ee)+':'+str(0)+str(00)
            xdata.append(nowTime)
            print(nowTime)
    if int(aa[1]) > 55 and int(aa[1]) <= 59:
        cc = int(aa[1]) + 5
        dd = cc - 60
        ee = int(aa[0])+1
        if int(aa[0]) >= 23:
            nowTime = '00:'+str(0)+str(dd)
            xdata.append(nowTime)
            print(nowTime)
        else:
            nowTime = str(ee)+':'+str(0)+str(dd)
            xdata.append(nowTime)
            print(nowTime)
    if int(aa[1]) == 00 and int(aa[1]) < 9 and str(aa[1]) != ab:
        cc = int(aa[1]) + 5
        ee = int(aa[0])+1
        nowTime = str(ee)+':'+str(0)+str(cc)
        xdata.append(nowTime)
        print(nowTime)
    if int(aa[1]) >= 10 and int(aa[1]) <= 54:
        cc = int(aa[1]) + 5
        nowTime = str(aa[0])+':'+str(cc)
        xdata.append(nowTime)
        print(nowTime)

    ndata = str(xdata[0])+':'+str(ax[2])
    RM = ax[0]+'.'+ax[1]
    RM = float(RM)

    NM = xdata[0]
    NMsplit = NM.split(":")
    NM = NMsplit[0]+'.'+NMsplit[1]
    NM = float(NM)

    CM = currentTimeSplited[0]+'.'+currentTimeSplited[1]
    CM = float(CM)

    visited = 'section1'
    n=1
    xoi = RDate.split('-')
    xqw = xoi[1][0:3]
    rDate = str(xqw)+' '+str(xoi[0])+', '+str(xoi[2])
    print(RM,NM,CM)
    if num <= n:
        if RM < NM:
            if CM <= NM:
                context = {
                    'RCode': RCode,
                    'RDate': RDate,
                    'rDate':rDate,
                    'RTime': RTime,
                    'currentTime': currentTime,
                    'profile_image':profile_icon,
                    'ndata': ndata,
                    'requested':user,
                    'amount':amount,
                    'visited': visited,
                    'num': num,
                }
                return render(request, 'agents/request_page.html', context)
            else:
                visited = 'section3'
                num = num + 1
                context = {
                    'RCode': RCode,
                    'RDate': RDate,
                    'rDate':rDate,
                    'RTime': RTime,
                    'profile_image':profile_icon,
                    'currentTime': currentTime,
                    'ndata': ndata,
                    'requested': user,
                    'amount': amount,
                    'visited': visited
                }
                for details in code:
                    newdetails = RD()
                    newdetails.pk = details.pk
                    newdetails.user = details.user
                    newdetails.customer = details.customer
                    newdetails.amount = details.amount
                    newdetails.rcode = details.rcode
                    newdetails.rtime = details.rtime
                    newdetails.rdate = details.rdate
                    newdetails.n = num
                    newdetails.send = True
                    newdetails.url = details.url
                    newdetails.has_accepted = False
                    newdetails.update = details.update
                    newdetails.created = details.created
                    newdetails.save()
                    print("Updated!")
                    return render(request, 'agents/request_page.html', context)
    else:
        visited = 'section2'
        context = {
            'RCode': RCode,
            'RDate': RDate,
            'rDate':rDate,
            'profile_image':profile_icon,
            'RTime': RTime,
            'currentTime': currentTime,
            'ndata': ndata,
            'requested': user,
            'amount': amount,
            'visited': visited
        }
        return render(request, 'agents/request_page.html', context)


def agentResponse(request,num,RCode,value):
    code = RD.objects.filter(rcode=RCode)
    if value == 'accept':
        if num <= 1:
            num = num + 1
            for details in code:
                newdetails = RD()
                newdetails.pk = details.pk
                newdetails.user = details.user
                newdetails.customer = details.customer
                newdetails.amount = details.amount
                newdetails.rcode = details.rcode
                newdetails.rtime = details.rtime
                newdetails.rdate = details.rdate
                newdetails.url = details.url
                newdetails.n = num
                newdetails.has_accepted = True
                newdetails.has_declined = details.has_declined
                newdetails.send = details.send
                newdetails.update = details.update
                newdetails.created = details.created
                newdetails.save()
                print("Accepted and Updated!")
                response = "Accepted"
                send = 'You have '+response+' the request'
                print(send)
                return render(request, 'agents/responsePage.html', {'send': send})
    else:
        if num <= 1:
            num = num + 1
            for details in code:
                newdetails = RD()
                newdetails.pk = details.pk
                newdetails.user = details.user
                newdetails.rcode = details.rcode
                newdetails.customer = details.customer
                newdetails.amount = details.amount
                newdetails.rtime = details.rtime
                newdetails.rdate = details.rdate
                newdetails.url = details.url
                newdetails.n = num
                newdetails.has_accepted = details.has_accepted
                newdetails.has_declined = True
                newdetails.send = details.send
                newdetails.update = details.update
                newdetails.created = details.created
                newdetails.save()
                print("Declined! not Update!")
                response = "Declined"
                send = 'You have '+response+' the request'
                data = veri()
                data.user = 'Value'
                data.rcode = RCode
                data.save()
                
                print(send)
                return render(request, 'agents/responsePage.html', {'send': send})


def withdraw(request):
    
    username = request.user
    user_str = str(username).lower()
    transAcc = RD.objects.filter(user=user_str)
    count = RD.objects.filter(user=user_str,).count()
    profile_icon = PP.objects.filter(user=user_str)

    t=0
    a=0
    d=0
    e=0
    z={}
    zz=[]
    c={}
    counted=[]
    for data in transAcc:
        #print(data.user+' Transaction '+data.rcode+' from '+str(data.customer))
        t+=1
        if data.has_accepted:
            #print('Accepted = ' + str(data.has_accepted))
            a+=1
        elif data.has_declined:
            #print('Accepted = ' + str(data.has_accepted)+' was Declined')
            d+=1
        else:
            #print('Accepted = ' + str(data.has_accepted)+' Expired')
            e+=1
        print(str(a),str(e),str(d)+'/'+str(t))
    z['total']=t
    z['accept']=a
    z['declined']=d
    z['expired']=e
    zz.append(dict(z))
    for num in range(count+1):
        counted.append(num)
    if t != 0:
        rate1={}
        rate2={}
        rate3={}
        acctrate={}
        acc = (a/t)*100
        dec = (d/t)*100
        exp = (e/t)*100
        cal = int((t-e)/t*100)
        acctrate['rating']=cal
        rate1['rating']=int(acc)
        rate1['rating1']=acc
        rate2['rating'] = int(dec)
        rate2['rating2'] = dec
        rate3['rating'] = int(exp)
        rate3['rating3'] = exp
        print(acc,dec,exp,cal)
    else:
        rate1=0
        rate2=0
        rate3=0
        acctrate={}
        cal = 0
        acctrate['rating'] = cal
    user_get = request.user
    user_use = str(user_get).lower() 
    avilfund = InAcct.objects.filter(user=user_use)
    if str('<QuerySet []>') in str(avilfund) :
        money = 0
        profit = 0
    else:
        for data in avilfund:
            money = int(data.balance)
            profit = float(data.xtrafund)
    profit = int(profit)
    if money >= 10000:
        ready = "yes"
    else:
        ready = "no"
    total = money + profit
    context = {
        'zz':zz,
        'page_id': 'Withdraw',
        'withdraw': True,
        'profile_image':profile_icon,
        'trans': True,
    }
    return render(request, 'agents/withdraw.html', context)


def topup(request):
    username = request.user
    user_str = str(username).lower()
    transAcc = RD.objects.filter(user=user_str)
    count = RD.objects.filter(user=user_str,).count()
    profile_icon = PP.objects.filter(user=user_str)

    t=0
    a=0
    d=0
    e=0
    z={}
    zz=[]
    c={}
    counted=[]
    for data in transAcc:
        #print(data.user+' Transaction '+data.rcode+' from '+str(data.customer))
        t+=1
        if data.has_accepted:
            #print('Accepted = ' + str(data.has_accepted))
            a+=1
        elif data.has_declined:
            #print('Accepted = ' + str(data.has_accepted)+' was Declined')
            d+=1
        else:
            #print('Accepted = ' + str(data.has_accepted)+' Expired')
            e+=1
        print(str(a),str(e),str(d)+'/'+str(t))
    z['total']=t
    z['accept']=a
    z['declined']=d
    z['expired']=e
    zz.append(dict(z))
    for num in range(count+1):
        counted.append(num)
    if t != 0:
        rate1={}
        rate2={}
        rate3={}
        acctrate={}
        acc = (a/t)*100
        dec = (d/t)*100
        exp = (e/t)*100
        cal = int((t-e)/t*100)
        acctrate['rating']=cal
        rate1['rating']=int(acc)
        rate1['rating1']=acc
        rate2['rating'] = int(dec)
        rate2['rating2'] = dec
        rate3['rating'] = int(exp)
        rate3['rating3'] = exp
        print(acc,dec,exp,cal)
    else:
        rate1=0
        rate2=0
        rate3=0
        acctrate={}
        cal = 0
        acctrate['rating'] = cal
    user_get = request.user
    user_use = str(user_get).lower() 
    avilfund = InAcct.objects.filter(user=user_use)
    if str('<QuerySet []>') in str(avilfund) :
        money = 0
        profit = 0
    else:
        for data in avilfund:
            money = int(data.balance)
            profit = float(data.xtrafund)
    profit = int(profit)
    if money >= 10000:
        ready = "yes"
    else:
        ready = "no"
    total = money + profit
    context = {
        'zz':zz,
        'page_id': 'Withdraw',
        'topup': True,
        'trans': True,
        'profile_image':profile_icon,
    }
    return render(request, 'agents/topup.html', context)

def setlimit(request):
    username = request.user
    user_str = str(username).lower()
    transAcc = RD.objects.filter(user=user_str)
    count = RD.objects.filter(user=user_str,).count()
    profile_icon = PP.objects.filter(user=user_str)

    t=0
    a=0
    d=0
    e=0
    z={}
    zz=[]
    c={}
    counted=[]
    for data in transAcc:
        #print(data.user+' Transaction '+data.rcode+' from '+str(data.customer))
        t+=1
        if data.has_accepted:
            #print('Accepted = ' + str(data.has_accepted))
            a+=1
        elif data.has_declined:
            #print('Accepted = ' + str(data.has_accepted)+' was Declined')
            d+=1
        else:
            #print('Accepted = ' + str(data.has_accepted)+' Expired')
            e+=1
        print(str(a),str(e),str(d)+'/'+str(t))
    z['total']=t
    z['accept']=a
    z['declined']=d
    z['expired']=e
    zz.append(dict(z))
    for num in range(count+1):
        counted.append(num)
    if t != 0:
        rate1={}
        rate2={}
        rate3={}
        acctrate={}
        acc = (a/t)*100
        dec = (d/t)*100
        exp = (e/t)*100
        cal = int((t-e)/t*100)
        acctrate['rating']=cal
        rate1['rating']=int(acc)
        rate1['rating1']=acc
        rate2['rating'] = int(dec)
        rate2['rating2'] = dec
        rate3['rating'] = int(exp)
        rate3['rating3'] = exp
        print(acc,dec,exp,cal)
    else:
        rate1=0
        rate2=0
        rate3=0
        acctrate={}
        cal = 0
        acctrate['rating'] = cal
    user_get = request.user
    user_use = str(user_get).lower() 
    avilfund = InAcct.objects.filter(user=user_use)
    if str('<QuerySet []>') in str(avilfund) :
        money = 0
        profit = 0
    else:
        for data in avilfund:
            money = int(data.balance)
            profit = float(data.xtrafund)
    profit = int(profit)
    if money >= 10000:
        ready = "yes"
    else:
        ready = "no"
    total = money + profit
    context = {
        'zz':zz,
        'page_id': 'Withdraw',
        'setlimit': True,
        'trans': True,
        'profile_image':profile_icon,
    }
    return render(request, 'agents/setlimit.html', context)


#def responsePage(request,send):
#    return render(request, 'agents/responsePage.html', {'send': send})


#signal connet


#===============FUNCTIONS=====================#


@receiver(user_Contact)
def user_contact_save(sender, **kwargs):
    data = kwargs
    details = telephn()
    details.user = data['user']
    details.telephone = data['telephone']
    details.save()
    print("Saved!")


@receiver(set_as_agent)
def now_an_agent(sender, **kwargs):
    data = kwargs
    details = IsAgent()
    details.user = data['user']
    details.is_agent = True
    details.save()
    print("New Agent "+data['user']+" Saved!")



@receiver(profile_avatar)
def profile_avatar_save(sender, user, serial, **kwargs):
    print('image no '+str(serial))
    image = PA.objects.filter(title=serial)
    for item in image:
        details = PP()
        details.user = user
        details.picture = item.image
        details.save()
        print("Avatar Saved!")


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
        details.created
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
    # account_sid = 'ACb799c4197deaaf52c87f41c13808b51e' 
    # auth_token = '65cb9b3a4161a397dd8c1f68a0aa0322'   

    # #account_sid = 'AC058e3ac8b1386c28177b7e856603a1b2'
    # #auth_token = 'd046384012799d57cf6c07b99ec31ad1' #'+12054488520'
    # superadmin = '+2348106529115'
    # sam = '+2348067331567'
    # otp = otp
    # tele = '+234'+telephone[1:]
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



    '''
    codeList = []
    codeDict = {}
    for x in range(2):
        code = random.randint(900000000000000000, 999999999999999999)
        codeDict["code"] = code
        print(code)
        codeList.append(dict(codeDict))
    codex = codeList
    print(codex)'''

#================= FUCTIONS =================#
def ran_gen(size, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for x in range(size))