from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from checkout.models import Checkout
from history.models import History, Activity, design
from .models import isNewUser as NU, userSocial
from accounts.models import userContact, userContact as phn
from agents.models import (
    RequestDetail as RD, 
    SentFunc as SF, 
    visited, 
    RCode as RC,
    ProfilePic as PP,
    rating,
    IsAgent as an_agent,
     Address, 
    Veri,
     fund
    )
from django.contrib.auth.models import User
from django.dispatch import receiver, Signal
from twilio.rest import Client
import random
from datetime import datetime
import secrets

import requests
import json 

import socket
import geocoder
from geolocation.main import GoogleMaps

from agents.agent_rate import *


from .signals import *


#COLOR SETTINGS
color = {
    'b98115e5e48d': '#777',
    'x3d1d64c33a1': '#2CA8FF',
    'c06b0da163b2': '#18ce0f',
    'aad50f5cd895': '#f96332',
    'k768bf130de8': '#FFB236',
    'af897e0d653b': '#FF3636',
    'e4645fd2cbc1': '#9368E9',
}
color_ = {
    'a777': 'black',
    'a2CA8FF': 'azure',
    'a18ce0f': 'green',
    'af96332': 'orange',
    'aFFB236': 'yellow',
    'aFF3636': 'red',
    'a9368E9': 'purple',
}
dImage = {
    'a9eecfcb0db2': 'sidebar-1',
    'f8bf9ce8b6ec': 'sidebar-2',
    'u7298430cad8': 'sidebar-3',
    'e7298430cad8': 'sidebar-4',
    'c3cc83ef9f8d': 'sidebar-5',

}


selected_agent = Signal(providing_args=['agent', 'user', 'amount','RCode'])
send_update = Signal(providing_args=['update', 'RCode'])
request_decline = Signal(providing_args=['agent', 'user', 'amount'])
request_sent = Signal(providing_args=['agent', 'user', 'amount', 'sent'])
save_request_details = Signal(providing_args=['agent', 'RCode', 'amount', 'cos'])
save_request_details_update = Signal(providing_args=['agent','RCode' 'user', 'amount'])
update_sms_func = Signal(providing_args=['RCode', 'value'])
payment_send = Signal(providing_args=['user', 'agent', 'RCode', 'pattern'])
rcode_used = Signal(providing_args=['RCode'])
sms_sent = Signal(providing_args=['RCode'])

@login_required
def home(request):
    try:
        UpdateAgentRating()
        print('worked')
    except:
        print('didnot work')
    try: 
        host_name = socket.gethostname() 
        host_ip = socket.gethostbyname(host_name) 
        print("Hostname :  ",host_name) 
        print("IP : ",host_ip) 
    except: 
        print("Unable to get Hostname and IP") 
    try:
        myloc = geocoder.ip('me')
        print(myloc)
        print(myloc.latlng[0],myloc.latlng[1])
        lat = str(myloc.latlng[0])
        lng = str(myloc.latlng[1])
    except:
        lat = '0'
        lng = '0'

    #try:
    api_key='AIzaSyAnUZPC05a-bgDA7lzvVRHxSOaCgGfmw1M'

    latlngk = lat+','+lng
    base_url = "https://maps.googleapis.com/maps/api/geocode/json"
    endpoint = f"{base_url}?latlng={latlngk}&key={api_key}"
    # see how our endpoint includes our API key? Yes this is yet another reason to restrict the key
    try:
        r = requests.get(endpoint)
    except:
        pass
    try:
        if r.status_code not in range(200, 299):
            loco = 'loading error'
    except:
        pass
    try:
        results = r.json()['results'][0]
        lat = results['geometry']['location']['lat']
        lng = results['geometry']['location']['lng']
        city = results['address_components'][2]['long_name']
        state = results['address_components'][3]['long_name']
        loco = city+', '+state+'.'
    except:
        loco = 'location error'
    

    username = request.user
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    user_str = str(username).lower()
    his = History.objects.filter(user=username)
    profile_icon = PP.objects.filter(user=user_str)
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=user_str)[0:4]
    if unread > 99:
        unread = '99+'
    if request.method == 'POST':
        print('good')
        xxList = {}
        new = []
        amount = request.POST.get('amount')
        if (amount.isdigit()):
            if int(amount) == 0:
                error = 'Request Error'
                status = "You cant make a request with "+str(amount)
                alert = 1
                xxList['v1'] = alert
                xxList['v2'] = error
                xxList['v3'] = status
                new.append(dict(xxList))
                data = {'loco': loco,'error': new, 'profile_image':profile_icon,'history':his,'notify':acts,'bgImg': ximg,'color':colorx, 'unread':unread}
                return render(request, 'user/request.html', data)
            else:
                try:
                    val = int(amount)
                    if int(amount) <= 50000:
                        roundVal = round(val, -3)
                        if roundVal == val:
                            Url = str("https://passmecash.com/users/request/agents/above/"+str(val))
                            return HttpResponseRedirect(Url)
                        else:
                            roundValDown = roundVal-1000
                            error = 'Request Error'
                            status = "You cant make a request with N"+str(amount)+", make your request in multiple of N1,000, you can try N"+str(roundValDown)+" or N"+str(roundVal)+"."
                            alert = 1
                            xxList['v1'] = alert
                            xxList['v2'] = error
                            xxList['v3'] = status
                            new.append(dict(xxList))
                            return render(request, 'user/request.html', {'loco': loco,'history':his,'error': new,'bgImg': ximg,'color':colorx, 'profile_image':profile_icon,'notify':acts, 'unread':unread})
                    else:
                            error = 'Request Error'
                            status = "Please make a request below N50,000"
                            alert = 2
                            xxList['v1'] = alert
                            xxList['v2'] = error
                            xxList['v3'] = status
                            new.append(dict(xxList))
                            return render(request, 'user/request.html', {'loco': loco,'history':his,'error': new,'bgImg': ximg,'color':colorx, 'profile_image':profile_icon,'notify':acts, 'unread':unread})
                except ValueError:
                    error = 'Request Error'
                    status = "You cant make a request with that amount"
                    alert = 1
                    xxList['v1'] = alert
                    xxList['v2'] = error
                    xxList['v3'] = status
                    new.append(dict(xxList))
                    return render(request, 'user/request.html', {'loco': loco,'history':his,'error': new, 'bgImg': ximg,'color':colorx,'profile_image':profile_icon,'notify':acts, 'unread':unread})
        else:
            error = 'Request Error'
            status = "Your request amount cant be "+str(amount)
            alert = 1
            xxList['v1'] = alert
            xxList['v2'] = error
            xxList['v3'] = status
            new.append(dict(xxList))
            return render(request, 'user/request.html', {'loco': loco,'error': new,'history':his, 'bgImg': ximg,'color':colorx,'profile_image':profile_icon,'notify':acts, 'unread':unread})
    else:
        context = {'loco': loco,'profile_image':profile_icon}
        check = an_agent.objects.filter(user=username)
        verified = Address.objects.filter(user=username,)
        for agent in check:
            print(agent.is_agent)
            if agent.is_agent == True:
                for xdata in verified:
                    if xdata.verified != True:
                        return HttpResponseRedirect(reverse('agents:new_profile'))
                    else:
                        return HttpResponseRedirect(reverse('agents:dashboard'))
            else:
                check_new = NU.objects.filter(user=username)
                for x in check_new:
                    if x.is_new:
                        print(x.is_new)
                return render(request, 'user/request.html', {'loco': loco,'history':his,'error': new,'bgImg': ximg,'color':colorx, 'profile_image':profile_icon,'notify':acts, 'unread':unread})
        check_new = NU.objects.filter(user=username)
        for x in check_new:
            if x.is_new:
                new = str(x.is_new)
            else:
                new = 'False'
            context = {'loco': loco,'profile_image':profile_icon,'history':his, 'newx':new, 'notify':acts,'bgImg': ximg,'color':colorx, 'unread':unread}
        return render(request, 'user/request.html', {'loco': loco,'history':his,'bgImg': ximg,'color':colorx, 'profile_image':profile_icon,'notify':acts, 'unread':unread})


def test(request):
    xList = {}
    new = []
    agent = 'i love cheese'
    num = 1
    xList['v1'] = num
    xList['v2'] = agent
    new.append(dict(xList))
    context = {
        'agent':agent,
        'num':num,
        'list': new,
    }
    return render(request, 'user/test.html', context)

@login_required
def agent_list(request, amount):
    username = request.user
    user_str = str(username).lower()
    agent_pick = fund.objects.filter(balance__gte=amount)
    #user_str = str(username).title()
    profile_icon = PP.objects.filter(user=user_str)
    RCode1 = secrets.token_hex(12)
    RCode = 'PMC-'+RCode1
    verify = RC.objects.filter(rcode=RCode)
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=user_str)[0:4]
    if unread > 99:
        unread = '99+'
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    if amount >= 1000:
        cleared = 'not cleared'
        while cleared != 'cleared':
            if str(RCode) in str(verify):
                print("New RCode Created but it exist creating new one!")
                RCode = secrets.token_hex(12)
                verified = RC()
                verified.rcode = RCode
                verified.save()
                print("Newly RCode Created but not used!")
                cleared = 'cleared'
            else:
                verified = RC()
                verified.rcode = RCode
                verified.save()
                print("New RCode Created but not used!")
                cleared = 'cleared'
        RCode = RCode
        username = request.user
        user_str = str(username).lower()
        dList = {}
        all_list = []
        for data in agent_pick:
            agent_loc = Address.objects.filter(user=data.user)
            agent_contact = phn.objects.filter(user=data.user)
            profile_iconx = PP.objects.filter(user=data.user)
            rated = rating.objects.filter(user=data.user)
            agent_detail = User.objects.all()
            sent = 'False'
            #for pic in profile_iconx:
            dList['agent_image'] = profile_iconx
            dList['agent_rating'] = rated
            dList['sent'] = True
            dList['RCode'] = RCode
            dList['amount_request'] = amount
            for xdata in agent_loc:
                dList['agent_name'] = xdata.user
                place = xdata.city + ', ' + xdata.state
                dList['agent_location'] = place
                for ydata in agent_contact:
                    dList['agent_telephone'] = ydata.telephone
                    for zdata in agent_detail:
                        if str(zdata) == xdata.user:
                            dList['agent_fName'] = zdata.first_name
                            dList['agent_lName'] = zdata.last_name
                            #if str(data.user) == str(profile_iconx.user):
                            all_list.append(dict(dList))
        all_listx = all_list
        return render(request, 'user/agent_list.html', {'bgImg': ximg,'color':colorx, 'all_listx': all_listx,'profile_image':profile_icon,'notify':acts, 'unread':unread})
    else:
        data = {'v1':'1', 'v2':'Invalid Request', 'v3':'Invalid Amount Requested'}
        return render(request, 'user/request.html', data)


@login_required
def agent_selected(request,details,others,amount,RCode,sent):
    username = request.user
    RCode_checker = RC.objects.filter(rcode=RCode)
    check_sent_sms = SF.objects.filter(rcode=RCode)
    visits = visited.objects.filter(rcode=RCode)
    get_design = design.objects.filter(user=username)
    acts = Activity.objects.filter(user=username)[0:4]
    unread = Activity.objects.filter(opened=False).count()
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    print(RCode_checker)
    RCode_len = str(RCode)
    if len(RCode_len) == 28:
        if str(RCode) in str(RCode_checker):
            if str('Sms pending '+str(RCode)) in str(check_sent_sms):
                code = RD.objects.filter(rcode=RCode)
                time = []
                for items in code:
                    print(items.rcode)
                    #time = time.appemd
                    # cnd(items.added)
                #print(time)
                agent = details
                if str(RCode) in str(code):
                    xxList = {}
                    new = []
                    if str('has NOT Accepted the request with ID '+str(RCode)) in str(code):
                        success = 'Reqest Sent!'
                        status = "Waiting for "+agent.title()+" Response"
                        process = '02'
                        alert = 1
                        xxList['v1'] = alert
                        xxList['v2'] = status
                        xxList['v3'] = success
                        new.append(dict(xxList))
                        context = {
                            'list': new,
                            'timed': process,
                            'time':process,
                            'bgImg': ximg,
                            'color':colorx,
                            'notify':acts,
                            'unread':unread,
                            'amount':amount,
                            'agent':agent,
                            }
                        print('has sent but not accepted')
                        return render(request, 'user/agent_selected.html', context)
                    elif str('has Declined this request with ID '+str(RCode)) in str(code):
                        veri = Veri.objects.filter(rcode=RCode)
                        if str(RCode+' - ' +'1') in str(veri):
                            status = ", Has Declined your request please head back and select a different agent"
                            declined = "<a href='" + str("https://passmecash.com/users/request/agents/above/"+str(amount))+"'> Click to Head Back</a>"
                            success = 'Request Declined!'
                            status = agent.title()+" Has declined your request."
                            process = '05'
                            alert = 3.7
                            xxList['v1'] = alert
                            xxList['v2'] = status
                            xxList['v3'] = success
                            xxList['v4'] = declined
                            new.append(dict(xxList))
                            context = {
                                'list': new,
                                'timed': process,
                                'time':process,
                                'notify':acts,
                                'bgImg': ximg,
                                'color':colorx,
                                'unread':unread,
                                'agent':agent,
                                'amount':amount,
                                }
                            print(agent+' declined the request')
                            dec = Veri.objects.filter(rcode=RCode)
                            for x in dec:
                                item = Veri()
                                item.pk = x.pk
                                item.user = x.user
                                item.rcode = x.rcode
                                item.count = str(int(x.count)+1)
                                item.created = x.created
                                item.save()
                            return render(request, 'user/agent_selected.html', context)
                        else:
                            Url = str("https://passmecash.com/users/request/agents/above/"+str(amount))
                            return HttpResponseRedirect(Url)
                    elif str('has Accepted this request with ID '+str(RCode)) in str(code):
                        now = datetime.now()
                        RTime = now.strftime("%H:%M:%S")
                        newTime = RTime.split(':')
                        if str(' has been redirected') in str(code):
                            success = 'Request Completed!'
                            status = agent.title()+" has accepted to PASS YOU CASH"
                            process = '03'
                            alert = 1
                            xxList['v1'] = alert
                            xxList['v2'] = status
                            xxList['v3'] = success
                            new.append(dict(xxList))
                            getdetails = Checkout.objects.filter(rcode=RCode)
                            for items in getdetails:
                                user_login = items.user
                                agent = items.agent
                                Rcode = items.rcode
                                pattern = items.patternkey
                            Url = 'https://passmecash.com/checkout/payment/!/user=!'+user_login+'/agent=!'+agent+'/refcode=!'+Rcode+'/PatternKey=!'+pattern+'/'
                            context = {
                                'list': new,
                                'timed': process,
                                'status':status,
                                'amount':amount,
                                'notify':acts,
                                'bgImg': ximg,
                                'color':colorx,
                                'unread':unread,
                                'time':process,
                                'status':status,
                                'agent':agent,
                                }
                            print('User redirected...BLESS God')
                            return HttpResponseRedirect(Url)
                        else:
                            update = True
                            status = "You will be Redirected to pay for the request with ID "+str(RCode)+" Shortly"
                            process = '04'
                            success = 'Thanks for using PassMeCash!'
                            alert = 1
                            xxList['v1'] = alert
                            xxList['v2'] = status
                            xxList['v3'] = success
                            new.append(dict(xxList))
                            context = {
                                'list': new,
                                'timed': process,
                                'status':status,
                                'time':process,
                                'notify':acts, 
                                'bgImg': ximg,
                                'color':colorx,
                                'unread':unread,
                                'amount':amount,
                                'status':status,
                                'agent':agent,
                                }
                            send_update.send(sender=None, update=update, RCode=RCode)
                            userx = request.user
                            user_login = str(userx).lower()
                            pattern = secrets.token_urlsafe(35)
                            payment_send.send(sender=None, user=user_login, agent=agent, RCode=RCode, pattern=pattern)
                            print('now request has been accepted will be redirecting in less that 2 sec')
                            return render(request, 'user/agent_selected.html', context)
                    else:
                        agent = details
                        username = request.user
                        user_str = str(username).lower()
                        try:
                            get_tele = userContact.objects.filter(user=agent)
                            for x in get_tele:
                                telephone = x.telephone
                            selected_agent.send(sender=None, agent=agent, telephone=telephone, user=user_str, amount=amount, RCode=RCode)
                            print("Sending request to "+agent)
                            process = '03'
                            alert = 1
                            success = 'Great!'
                            status = "Sending your request to . . . "+agent.title()
                            xxList['v1'] = alert
                            xxList['v2'] = status
                            xxList['v3'] = success
                            new.append(dict(xxList))
                            context = {
                                'list': new,
                                'timed': process,
                                'status':status,
                                'time':process,
                                'notify':acts,
                                'bgImg': ximg,
                                'color':colorx,
                                'unread':unread,
                                'amount':amount,
                                'status':status,
                                'agent':agent,
                                }
                            return render(request, 'user/agent_selected.html', context)
                        except Exception as e:
                            error = "PMC Could not connect to a Server"
                            print(e)
                            if str('not visited') in str(visits):
                                for item in visits:
                                    newValue = visited()
                                    newValue.pk = item.pk
                                    newValue.rcode = item.rcode
                                    newValue.visit = int(item.visit) + 1
                                    newValue.created = item.created
                                    newValue.save()
                                    print('got here')
                                xxList = {}
                                new = []
                                agent = details
                                process = '03'
                                alert = 4
                                status = "Network Connection Error"
                                xxList['v1'] = alert
                                xxList['v2'] = status
                                xxList['v3'] = error
                                new.append(dict(xxList))
                                context = {
                                'list': new,
                                'timed': process,
                                'status':status,
                                'agent':agent,
                                'notify':acts,
                                'unread':unread,
                                'amount':amount,
                                'bgImg': ximg,
                                'color':colorx,
                                'time':process,
                                'status':status,
                                'agent':agent,
                                }
                                return render(request, 'user/agent_selected.html', context)
                            else:
                                username = request.user
                                unread = Activity.objects.filter(opened=False).count()
                                acts = Activity.objects.filter(user=username)[0:4]
                                if unread > 99:
                                    unread = '99+'
                                if str('page 5 time(s)') not in str(visits):
                                    alert = 4
                                    for item in visits:
                                        newValue = visited()
                                        newValue.pk = item.pk
                                        newValue.rcode = item.rcode
                                        newValue.visit = int(item.visit) + 1
                                        newValue.created = item.created
                                        newValue.save()
                                    agent = details
                                    process = '03'
                                    if str('page 1 time(s)') in str(visits):
                                        status = "Just a sec let PMC reconnect"
                                        alert = 3.5
                                    elif str('page 2 time(s)') in str(visits): 
                                        error = 'Reconnecting'
                                        status = "Just a sec let PMC reconnect"
                                        alert = 3.5
                                    elif str('page 3 time(s)') in str(visits): 
                                        error = 'Connection Error'
                                        status = "PMC Could not reconnect to ConnectionServer"
                                        alert = 3
                                    elif str('page 4 time(s)') in str(visits): 
                                        error = 'Connection Error'
                                        process = '03'
                                        status = "Check your connection and Try Again"
                                        alert = 3
                                    else:
                                        error = 'Connection Error'
                                        status = "ConnectionServer Timeout"

                                    xxList = {}
                                    new = []
                                    xxList['v1'] = alert
                                    xxList['v2'] = status
                                    xxList['v3'] = error
                                    new.append(dict(xxList))
                                    context = {
                                        'list': new,
                                        'timed': process,
                                        'status':status,
                                        'agent':agent,
                                        'notify':acts,
                                        'bgImg': ximg,
                                        'color':colorx,
                                        'unread':unread,
                                        'amount':amount,
                                        'time':process,
                                        'status':status,
                                        'agent':agent,
                                        }
                                    return render(request, 'user/agent_selected.html', context)
                                else:
                                    delete = RD.objects.filter(rcode=RCode)
                                    delete.delete()
                                    print('Request did not send and has been deleted!')
                                    Url = str("https://passmecash.com/users/request/agents/above/"+str(amount))
                                    return HttpResponseRedirect(Url)
                else:
                    username = request.user
                    unread = Activity.objects.filter(opened=False).count()
                    acts = Activity.objects.filter(user=username)[0:4]
                    if unread > 99:
                        unread = '99+'
                    if str('not visited') in str(visits):
                        error = "processing"
                        for item in visits:
                            newValue = visited()
                            newValue.pk = item.pk
                            newValue.rcode = item.rcode
                            newValue.visit = int(item.visit) + 1
                            newValue.created = item.created
                            newValue.save()
                        alert = 3.5
                        agent = details
                        process = '03'
                        status = "PMC is generating New Transaction ID "
                        xxList = {}
                        new = []
                        xxList['v1'] = alert
                        xxList['v2'] = status
                        xxList['v3'] = error
                        new.append(dict(xxList))
                        context = {
                            'list': new,
                            'timed': process,
                            'status':status,
                            'agent':agent,
                            'time':process,
                            'notify':acts,
                            'unread':unread,
                            'bgImg': ximg,
                            'color':colorx,
                            'amount':amount,
                            'status':status,
                            'agent':agent,
                            }
                        cos = request.user
                        cos_lower = str(cos).lower()
                        save_request_details.send(sender=None,RCode=RCode,cos=cos_lower,amount=amount,user=agent,value=sent)
                        return render(request, 'user/agent_selected.html', context)
                    else:
                        username = request.user
                        unread = Activity.objects.filter(opened=False).count()
                        acts = Activity.objects.filter(user=username)[0:4]
                        if unread > 99:
                            unread = '99+'
                        error = 'Error'
                        if str('page 6 time(s)') not in str(visits):
                            alert = 3.5
                            for item in visits:
                                newValue = visited()
                                newValue.pk = item.pk
                                newValue.rcode = item.rcode
                                newValue.visit = int(item.visit) + 1
                                newValue.created = item.created
                                newValue.save()
                            agent = details
                            process = '02'
                            if str('page 4 time(s)') in str(visits): 
                                status = "Just a sec PMC will redirect you back and create a new 'Transaction ID' "
                            elif str('page 5 time(s)') in str(visits): 
                                status = "Just a sec PMC will redirect you back and create a new 'Transaction ID' "
                            else:
                                status = "PMC could not generate Transaction ID due to 'Transaction ID Error' "
                           
                            xxList = {}
                            new = []
                            xxList['v1'] = alert
                            xxList['v2'] = status
                            xxList['v3'] = error
                            new.append(dict(xxList))
                            context = {
                                'list': new,
                                'timed': process,
                                'status':status,
                                'amount':amount,
                                'notify':acts,
                                'unread':unread,
                                'bgImg': ximg,
                                'color':colorx,
                                'agent':agent,
                                'time':process,
                                'status':status,
                                'agent':agent,
                                }
                            return render(request, 'user/agent_selected.html', context)
                        else:
                            Url = str("https://passmecash.com/users/request/agents/above/"+str(amount))
                            return HttpResponseRedirect(Url)
            elif str('Sms port created with ID '+str(RCode)) in str(check_sent_sms):
                agent = details
                process = '03'
                error = 'Transaction ID Error' 
                xxList = {}
                new = []
                alert = 5
                if str('not visited') in str(visits):
                    for item in visits:
                        newValue = visited()
                        newValue.pk = item.pk
                        newValue.rcode = item.rcode
                        newValue.visit = int(item.visit) + 1
                        newValue.created = item.created
                        newValue.save()
                    agent = details
                    status = "The Transaction ID you are trying to access has been used "
                    xxList['v1'] = alert
                    xxList['v2'] = status
                    xxList['v3'] = error
                    new.append(dict(xxList))
                    context = {
                    'list': new,
                    'timed': process,
                    'status':status,
                    'agent':agent,
                    'time':process,
                    'notify':acts,
                    'bgImg': ximg,
                    'color':colorx,
                    'unread':unread,
                    'amount':amount,
                    'status':status,
                    'agent':agent,
                    }
                    return render(request, 'user/agent_selected.html', context)
                else:
                    if str('page 6 time(s)') not in str(visits):
                        for item in visits:
                            newValue = visited()
                            newValue.pk = item.pk
                            newValue.rcode = item.rcode
                            newValue.visit = int(item.visit) + 1
                            newValue.created = item.created
                            newValue.save()
                        agent = details
                        process = '04'
                        if str('page 1 time(s)') in str(visits): 
                            status = "PMC will try to create a new Transaction ID . . . "
                            alert = 3.5
                        elif str('page 2 time(s)') in str(visits): 
                            status = "PMC is generating New Transaction ID "
                            alert = 3.5
                        elif str('page 3 time(s)') in str(visits): 
                            status = "generating . . . "
                            alert = 3.5
                        elif str('page 4 time(s)') in str(visits): 
                            status = "PMC could not generate new Transaction ID "
                        else:
                            alert = 3.5
                            status = "Just a sec PMC will redirect you back "
                        xList = {}
                        new = []
                        xxList['v1'] = alert
                        xxList['v2'] = status
                        xxList['v3'] = error
                        new.append(dict(xxList))
                        context = {
                            'list': new,
                            'timed': process,
                            'status':status,
                            'amount':amount,
                            'bgImg': ximg,
                            'color':colorx,
                            'notify':acts,
                            'unread':unread,
                            'agent':agent,
                            'time':process,
                            }
                        return render(request, 'user/agent_selected.html', context)
                    else:
                        Url = str("https://passmecash.com/users/request/agents/above/"+str(amount))
                        return HttpResponseRedirect(Url)
            else:
                username = request.user
                unread = Activity.objects.filter(opened=False).count()
                acts = Activity.objects.filter(user=username)[0:4]
                if unread > 99:
                    unread = '99+'
                agent = details
                process = '05'
                status = "PMC is processing your request "
                sent = True
                xxList = {}
                new = []
                num = 0
                xxList['v1'] = num
                xxList['v2'] = status
                new.append(dict(xxList))
                context = {
                    'agent': agent,
                    'status': status,
                    'list': new,
                    'bgImg': ximg,
                    'color':colorx,
                    'notify':acts,
                    'unread':unread,
                    'amount':amount,
                    'timed':process,
                }
                update_sms_func.send(sender=None,RCode=RCode,value=sent)
                return render(request, 'user/agent_selected.html', context)
        else:
            agent = details
            process = '03'
            error = "Error404: "
            xxList = {}
            new = []
            alert = 5
            if str(RCode) not in str(visits):
                newValue = visited()
                newValue.rcode = str(RCode)
                newValue.visit = 1
                newValue.save()
                agent = details
                status = "Transaction ID Not Found"
                xxList['v1'] = alert
                xxList['v2'] = status
                xxList['v3'] = error
                new.append(dict(xxList))
                context = {
                    'list': new,
                    'timed': process,
                    'status':status,
                    'agent':agent,
                    'bgImg': ximg,
                    'color':colorx,
                    'amount':amount,
                    'notify':acts, 
                    'unread':unread,
                    'time':process,
                    'status':status,
                    'agent':agent,
                }
                return render(request, 'user/agent_selected.html', context)
            else:
                if str('page 4 time(s)') not in str(visits):
                    for item in visits:
                        newValue = visited()
                        newValue.pk = item.pk
                        newValue.rcode = item.rcode
                        newValue.visit = int(item.visit) + 1
                        newValue.created = item.created
                        newValue.save()
                    agent = details
                    process = '04'
                    if str('page 1 time(s)') in str(visits): 
                        status = "Rechecking Transaction ID Again "
                        alert = 3.5
                    elif str('page 2 time(s)') in str(visits): 
                        status = "SORRY! No Transaction with ID "+str(RCode)
                        alert = 4
                    else:
                        alert = 3.5
                        status = "Just a sec PMC will redirect you back "

                    xxList['v1'] = alert
                    xxList['v2'] = status
                    xxList['v3'] = error
                    new.append(dict(xxList))
                    context = {
                        'list': new,
                        'timed': process,
                        'status':status,
                        'amount':amount,
                        'bgImg': ximg,
                        'color':colorx,
                        'notify':acts,
                        'unread':unread,
                        'agent':agent,
                        'time':process,
                        }
                    return render(request, 'user/agent_selected.html', context)
                else:
                    delete = visited.objects.filter(rcode=RCode)
                    delete.delete()
                    Url = str("https://passmecash.com/users/request/agents/above/"+str(amount))
                    return HttpResponseRedirect(Url)
    else:
        xxList = {}
        new = []
        alert = 5
        process = '03'
        error = 'Error 401: '
        if str(RCode) not in str(visits):
            newValue = visited()
            newValue.rcode = str(RCode)
            newValue.visit = 1
            newValue.save()
            agent = details
            status = 'Unauthorized Transaction ID detected' 
            xxList['v1'] = alert
            xxList['v2'] = status
            xxList['v3'] = error
            new.append(dict(xxList))
            context = {
                'list': new,
                'timed': process,
                'status':status,
                'amount':amount,
                'notify':acts,
                'unread':unread,
                'bgImg': ximg,
                'color':colorx,
                'agent':agent,
                'time':process,
                'status':status,
                'agent':agent,
            }
            return render(request, 'user/agent_selected.html', context)
        else:
            if str('page 4 time(s)') not in str(visits):
                for item in visits:
                    newValue = visited()
                    newValue.pk = item.pk
                    newValue.rcode = item.rcode
                    newValue.visit = int(item.visit) + 1
                    newValue.created = item.created
                    newValue.save()
                agent = details
                process = '04'
                if str('page 1 time(s)') in str(visits): 
                    status = "Rechecking Transaction ID Again"
                elif str('page 2 time(s)') in str(visits): 
                    status = "SORRY! "+str(RCode)+" is Unauthorized"
                else:
                    alert = 3.5
                    status = "Just a sec PMC will redirect you back "

                xxList['v1'] = alert
                xxList['v2'] = status
                xxList['v3'] = error
                new.append(dict(xxList))
                context = {
                    'list': new,
                    'timed': process,
                    'status':status,
                    'agent':agent,
                    'bgImg': ximg,
                    'color':colorx,
                    'notify':acts,
                    'unread':unread,
                    'time':process,
                    'amount':amount,
                    }
                return render(request, 'user/agent_selected.html', context)
            else:
                delete = visited.objects.filter(rcode=RCode)
                delete.delete()
                Url = str("https://passmecash.com/users/request/agents/above/"+str(amount))
                return HttpResponseRedirect(Url)



#def user_profile(request, username):
#    if request.method == "POST":
#        action = request.POST.get('edit')
#        if str(action) == 'edit':
#           return HttpResponseRedirect(reverse('users:user_profile_edit'))
#    return render(request, 'user/user_profile.html')


def user_profile(request, username):
    username = request.user
    user_str = str(username).lower()
    profile_icon = PP.objects.filter(user=user_str)
    details = User.objects.filter(username=username)
    add = Address.objects.filter(user=username)
    tele = phn.objects.filter(user=username)
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=user_str)[0:4]
    social = userSocial.objects.filter(user=username)
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    allow = "disabled"
    allow2 = "edit"
    if request.method == "POST":
        action = request.POST.get('edit')
        if str(action) == 'edit':
            allow = ''
            allow2 = 'edited'
            data = {
                'pix': profile_icon,
                'address':add,
                'telephone':tele,
                'bgImg': ximg,
                'color':colorx,
                'notify':acts,
                'unread':unread,
                'social':social,
                'allow': allow,
                'allow2': allow2,
                'details': details,
            }
            return render(request, 'user/user_profile.html',data)
        else:
            email = request.POST.get('email')
            fname = request.POST.get('fname')
            lname = request.POST.get('lname')
            street = request.POST.get('address')
            city = request.POST.get('city')
            state = request.POST.get('state')
            about_me = request.POST.get('about_me')
            me_facebook = request.POST.get('me_facebook')
            me_twitter = request.POST.get('me_twitter')
            me_google = request.POST.get('me_google')
            # date_joined, email, first_name, groups, 
            #id, is_active, is_staff, is_superuser, 
            #last_login, last_name, logentry, password, user_permissions, username
            for x in details:
                item = User()
                item.pk = x.pk
                item.username = x.username
                item.email = email
                item.first_name = fname
                item.last_name = lname
                item.id = x.id
                item.is_active = x.is_active
                item.is_staff = x.is_staff
                item.is_superuser = x.is_superuser
                item.last_login = x.last_login
                item.password = x.password
                item.save()
            if str(username) in add:
                for y in add:
                    items = Address()
                    items.pk = y.pk
                    items.user = y.user
                    items.street = street
                    items.city = city
                    items.state = state
                    items.country = y.country
                    items.added = y.added
                    items.ip_address = y.ip_address
                    items.latitude = y.latitude
                    items.longitude = y.longitude
                    items.verified = y.verified
                    items.created = y.created
                    items.save()
            else:
                items = Address()
                items.user = username
                items.street = street
                items.city = city
                items.state = state
                items.save()
            if str(username) in social:
                for z in social:
                    itemz = userSocial()
                    itemz.user = z.user
                    itemz.pk = z.pk 
                    itemz.facebook = me_facebook
                    itemz.twitter = me_twitter
                    itemz.google = me_google
                    itemz.about = about_me
                    itemz.created = z.created
                    itemz.save()
            else:
                itemz = userSocial()
                itemz.user = username
                itemz.facebook = me_facebook
                itemz.twitter = me_twitter
                itemz.google = me_google
                itemz.about = about_me
                itemz.save()

            data = {
                'mode':'Editind Mode',
                'time': '00001',
                'pix': profile_icon,
                'address':add,
                'bgImg': ximg,
                'color':colorx,
                'telephone':tele,
                'notify':acts,
                'unread':unread,
                'social':social,
                'text': 'Applying Changes PLEASE WAIT. . .',
                'details': details,
                'allow': allow,
                'allow2': allow2,
            }
            return render(request, 'user/user_profile.html',data)
    data = {
        'details': details,
        'social':social,
        'address':add,
        'bgImg': ximg,
        'notify':acts,
        'unread':unread,
        'color':colorx,
        'telephone':tele,
        'allow': allow,
        'pix': profile_icon,
        'allow2': allow2,
    }
    return render(request, 'user/user_profile.html',data)

def user_profile_edit(request, username):
    return render(request, 'user/user_profile_edit.html')


def reciept(request):
    username = request.user
    his = History.objects.filter(user=username)
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=username)[0:4]
    social = userSocial.objects.filter(user=username)
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    data ={
        'history': his,
        'bgImg': ximg,
        'notify':acts,
        'unread':unread,
        'color':colorx,
        }
    return render(request, 'user/recipt.html', data)


def act(request):
    username = request.user
    his = History.objects.filter(user=username)
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=username)[0:4]
    social = userSocial.objects.filter(user=username)
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    data = {
        'history': his,
        'notify':acts,
        'unread':unread,
        'bgImg': ximg,
        'color':colorx,
        }
    return render(request, 'user/act.html', data)


def setting(request, username):
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=username)[0:4]
    if unread > 99:
        unread = '99+'
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    if request.method == 'POST':
        bgimg = request.POST.get('bgimg')
        filterx = request.POST.get('filter')
        image = request.POST.get('image')
        filterx = filterx[1:]
        dimg = image[1:]
        if str(filterx) in color:
            filters = color[filterx]
        if str(dimg) in dImage:
            imagex = dImage[dimg]
        get_user = design.objects.filter(user=username)
        if str(username) not in str(get_user):
            item = design()
            item.user = username
            item.background = True
            item.color = filters
            item.img = imagex
            item.save()
        else:
            for x in get_user:
                item = design()
                item.pk = x.pk
                item.user = username
                item.background = True
                item.color = filters
                item.img = imagex
                item.created = x.created
                item.save()
        data = {
            'color':colorx,
            'bgImg':ximg,
            'time':'0000002',
            'unread':unread,
            'text': 'Applying Changes PLEASE WAIT . . .',
            'notify':acts,
            }
        return render(request, 'user/settings.html', data)
    data = {
            'color':colorx,
            'bgImg':ximg,
            'unread':unread,
            'notify':acts,
            }
    return render(request, 'user/settings.html', data)


def set_location(request):
    return render(request, 'user/map_select_loco.html')


def view_agent(request, amount, agent):
    username = request.user
    actz = Activity.objects.filter(user=username)
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=username)[0:4]
    social = userSocial.objects.filter(user=username)
    loco = Address.objects.filter(user=agent)
    for x in loco:
        street = x.street
        city = x.city
        state = x.state
        country = x.country
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    if unread > 99:
        unread = '99+'
    data ={
        'street':street,
        'city':city,
        'state':state,
        'country':country,
        'short': acts,
        'unread': unread,
        'notify': actz,
        'bgImg': ximg,
        'color':colorx,
        }
    return render(request, 'user/view_agent.html', data)



def noti(request):
    username = request.user
    actz = Activity.objects.filter(user=username)
    unread = Activity.objects.filter(opened=False).count()
    acts = Activity.objects.filter(user=username)[0:4]
    social = userSocial.objects.filter(user=username)
    get_design = design.objects.filter(user=username)
    if str(username) in str(get_design):
        for x in get_design:
            icolor = 'a'+x.color[1:]
            ximg = x.img
            if icolor in color_:
                colorx = color_[icolor]
    else:
        colorx = 'purple'
        ximg = 'sidebar-5'
    if unread > 99:
        unread = '99+'
    data ={
        'short': acts,
        'unread': unread,
        'notify': actz,
        'bgImg': ximg,
        'color':colorx,
        }
    return render(request, 'user/noti.html', data)



#ConnectionError

    #print(type(details))
    #print(type(amount))
    #print(details)
    #agent = details
    #username = request.user
    #print(type(others))
    #print(others)
    #word = others.split("'")
    #print(word[3])
    #selected_agent.send(sender=None, agent=agent, user=username, amount=amount,RCode=RCode)



@receiver(selected_agent)
def selected_agent_hello(sender, telephone, **kwargs):
    now = datetime.now()
    data = kwargs
    name = str(data['user'])
    agent = str(data['agent'])
    amount = data['amount']
    RCode = data['RCode']
    tele = '+234'+telephone[1:]
    RTime = now.strftime("%H:%M:%S")
    RDate = now.strftime("%d-%B-%Y")
    account_sid = 'ACb799c4197deaaf52c87f41c13808b51e' 
    auth_token = '65cb9b3a4161a397dd8c1f68a0aa0322'
    #account_sid = 'AC058e3ac8b1386c28177b7e856603a1b2'
    #auth_token = 'd046384012799d57cf6c07b99ec31ad1' #'+12054488520'
    superadmin = '+2348106529115'
    sam ='+2348067331567'
    url = 'https://passmecash.com/agents/request/from/'+name+'/to/pass-'+str(amount)+'/'+str(RCode)+'/'+str(RDate)+'/'+str(RTime)
    # Your Account SID from twilio.com/console
    account_sid = account_sid
    # Your Auth Token from twilio.com/console
    auth_token = auth_token
    body = 'Hello ' +agent+',\nYou have a New Request, From - '+name+' to Pass '+str(amount)+'. \nFollow link below to accept or decline request '+url+'. \nRegards PMC'
    client = Client(account_sid, auth_token)
    message = client.messages.create(from_='+12533000256', body=body, to=tele)
    if message.sid.startswith("SM"):
        sent = True
        save_request_details_update.send(sender=None, user=agent, RCode=RCode, amount=amount, cos=name, rdate=RDate,
                                  rtime=RTime, url=url, sent=sent)
        sms_sent.send(sender=None, RCode=RCode)
        rcode_used.send(sender=None, RCode=RCode)
        print("Request Message Sent Successfully")
        print("Url - ", url)
    else:
    # print(message.sid)
        print("SORRY!, Could not send your message")


@receiver(save_request_details)
def request_saved(sender, **kwargs):
    data = kwargs
    details = RD()
    details.user = data['user']
    details.customer = data['cos']
    details.amount = data['amount']
    details.rcode = data['RCode']
    details.save()
    print("Request Created!")


@receiver(save_request_details_update)
def request_saved_again(sender, RCode, **kwargs):
    code = RD.objects.filter(rcode=RCode)
    data = kwargs
    for details in code:
        newdetails = RD()
        newdetails.pk = details.pk
        newdetails.user = details.user
        newdetails.customer = details.customer
        newdetails.amount = details.amount
        newdetails.rcode = details.rcode
        newdetails.rtime = data['rtime']
        newdetails.rdate = data['rdate']
        newdetails.n = details.n
        newdetails.send = True
        newdetails.url = data['url']
        newdetails.has_accepted = False
        newdetails.update = details.update
        newdetails.has_declined = details.has_declined
        newdetails.created = details.created
        newdetails.save()
        print("Request Sent and Saved!")


@receiver(send_update)
def update_saved(sender, **kwargs):
    data = kwargs
    code = RD.objects.filter(rcode=data['RCode'])
    for items in code:
        details = RD()
        details.pk = items.pk
        details.user = items.user
        details.rcode = data['RCode']
        details.rtime = items.rtime
        details.customer = items.customer
        details.amount = items.amount
        details.rdate = items.rdate
        details.send = items.send
        details.url = items.url
        details.n = items.n
        details.has_accepted = items.has_accepted
        details.update = data['update']
        details.created = items.created
        details.save()
        print("Updated!")


@receiver(request_decline)
def decline_saved(sender, **kwargs):
    data = kwargs
    code = RD.objects.filter(rcode=data['RCode'])
    for items in code:
        details = RD()
        details.pk = items.pk
        details.user = items.user
        details.customer = items.customer
        details.amount = items.amount
        details.rcode = data['RCode']
        details.rtime = items.rtime
        details.rdate = items.rdate
        details.send = items.send
        details.url = items.url
        details.n = items.n
        details.has_accepted = items.has_accepted
        details.update = data['update']
        details.created = items.created
        details.save()
        print("Updated!")


@receiver(update_sms_func)
def request_sent_already(sender, **kwargs):
    data = kwargs
    RCode = data['RCode']
    check = SF.objects.filter(rcode=RCode)
    check_visit = visited.objects.filter(rcode=RCode)
    if str(RCode) in str(check):
        print('SMS Module already exits!')
        if str(RCode) in str(check_visit):
            print('Visit Module already exits!')
            print('Existing Visit Module must be refreshed ')
            print('Deleting existing visit Module...!')
            delete = visited.objects.filter(rcode=RCode)
            delete.delete()
            print('Deleted existing visit Module...!')
            print('Creating New Module...!')
            visit = visited()
            visit.rcode = RCode
            visit.save()
            print("Page Visit Counter created and Activated")
        else:
            visit = visited()
            visit.rcode = RCode
            visit.save()
            print("Page Visit Counter Activated")
    else:
        details = SF()
        details.rcode = data['RCode']
        details.check = True
        details.save()
        print("SMS Module created")
        if str(RCode) in str(check_visit):
            print('Visit Module already exits!')
            print('Deleting existing visit Module...!')
            delete = visited.objects.filter(rcode=RCode)
            delete.delete()
            print('Deleted existing visit Module...!')
            print('Creating New Module...!')
            visit = visited()
            visit.rcode = RCode
            visit.save()
            print("Page Visit Counter created and Activated")
        else:
            visit = visited()
            visit.rcode = RCode
            visit.save()
            print("Page Visit Counter Activated")
            

@receiver(rcode_used)
def rcode_has_been_used(sender,RCode,**kwargs):
    verify = RC.objects.filter(rcode=RCode)
    for items in verify:
        verified = RC()
        verified.pk = items.pk
        verified.rcode = items.rcode
        verified.used = True
        verified.created = items.created
        verified.save()
        print("New RCode Created has now been used!")



@receiver(payment_send)
def payment_save(sender, user, agent, RCode, pattern, **kwargs):
    details = Checkout()
    details.user = user
    details.agent = agent
    details.rcode = RCode
    details.patternkey = pattern
    details.failed = False
    details.pending = True
    details.approved = False
    details.save()
    print('payment info saved')

    #verify = RC.objects.filter(rcode=RCode)
    #for items in verify:
     #   verified = RC()
      #  verified.pk = items.pk
       # verified.rcode = items.rcode
        #verified.used = True
        #verified.created = items.created
        #verified.save()
        #print("New RCode Created has now been used!")


@receiver(sms_sent)
def sms_has_sent(sender,RCode,**kwargs):
    sent = SF.objects.filter(rcode=RCode)
    for items in sent:
        has_sent = SF()
        has_sent.pk = items.pk
        has_sent.rcode = items.rcode
        has_sent.sms_sent = True
        has_sent.check = True
        has_sent.created = items.created
        has_sent.save()
        print("Sms Sent and saved!")




# Exception HTTPSConnectionPool - ConnectionError
