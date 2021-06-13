from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from .models import Checkout
from django.contrib.auth.models import User
from accounts.models import userContact as phn
from agents.models import (
    RequestDetail as RD,
    Address,
    fund,
    InAcct,
    )
from datetime import datetime
from django.contrib.auth.decorators import login_required

# Create your views here.

now = datetime.now()


@login_required
def checkout(request, user, agent, Rcode, pattern):
	details = Checkout.objects.filter(patternkey=pattern)
	userdetails = User.objects.filter(username=user)
	print(details)
	print(Rcode)
	if str('<QuerySet []>') not in str(details):
		if str('Transaction '+Rcode+' is pending') in str(details):
			check = RD.objects.filter(rcode=Rcode)
			telephonecheck = phn.objects.filter(user=user)
			for its in check:
				amount = its.amount
				date = its.rdate
				time = its.rtime
				refcode = its.rcode
			
			for aaa in telephonecheck:
				telephone = aaa.telephone
			
			for item in userdetails:
				user2 = item.username
				fname = item.first_name
				lname = item.last_name
				email = item.email
			full_name = fname+' '+lname
			a = amount.split('0')
			charge = int(a[0])*100
			total = int(amount)+int(charge)
			context = {
				'details':details,
				'amount':amount,
				'agent':agent,
				'date':date,
				'time':time,
				'refcode':refcode,
				'telephone':telephone,
				'email':email,
				'full_name':full_name,
				'user':user2,
				'charge':charge,
				'total':total,
					}
			return render(request, 'checkout/checkout.html', context)
		elif str('Transaction '+Rcode+' is approved') in str(details):
			for item in userdetails:
				user2 = item.username
			note = 'Hello! '+user2+' this Transaction has been completed'
			return render(request, 'checkout/checkout.html', {'note':note})
		elif str('Transaction '+Rcode+' is failed') in str(details):
			for item in userdetails:
				user2 = item.username
			note = 'Hello! '+user2+' this Transaction failed try again'
			return render(request, 'checkout/checkout.html', {'note':note})
		else:
			note = 'No Transaction with '+Rcode+' Found'
			return render(request, 'checkout/checkout.html', {'note':note})
	else:
			note = 'Transaction Error!'
			return render(request, 'checkout/checkout.html', {'note':note})
	#user$$
	#agent$$
	#amount (+ charge)$$
	#url
	#date \ time created
	#valid transaction ID
	#telephone
	#email
	#
	#
	#
	

@login_required
def process(request, Rcode, pattern, status):
	print(Rcode)
	print(pattern)
	print(status)
	check = Checkout.objects.filter(patternkey=pattern)
	if status == 'True':
		for items in check:
			details = Checkout()
			details.pk = items.pk
			details.user = items.user
			details.agent = items.agent
			details.rcode = items.rcode
			details.patternkey = items.patternkey
			details.failed = False
			details.pending = False
			details.approved = status
			details.created = items.created
			details.save()
		Url = "http://passmecash.com/checkout/payment/!/success/refcode=!"+str(Rcode)+"/PatternKey=!"+str(pattern)
		return HttpResponseRedirect(Url)
	else:
		checkx = Checkout.objects.filter(approved=True)
		print('>'+str(checkx))
		if str('Transaction '+Rcode+' is approved') in str(check):
			Url = "http://passmecash.com/checkout/payment/!/success/refcode=!"+str(Rcode)+"/PatternKey=!"+str(pattern)
			return HttpResponseRedirect(Url)
		else:
			for items in check:
				details = Checkout()
				details.pk = items.pk
				details.user = items.user
				details.agent = items.agent
				details.rcode = items.rcode
				details.patternkey = items.patternkey
				details.failed = True
				details.pending = False
				details.approved = False
				details.created = items.created
				details.save()
			Url = "http://passmecash.com/checkout/payment/!/failed/refcode=!"+str(Rcode)+"/PatternKey=!"+str(pattern)
			return HttpResponseRedirect(Url)

@login_required
def successful(request, Rcode, pattern):
	check = Checkout.objects.filter(patternkey=pattern)
	print(Rcode)
	print(pattern)
	for items in check:
		agent = items.agent
		approved = items.approved
		pending = items.pending
		failed = items.failed

	details = User.objects.filter(username=agent)
	address = Address.objects.filter(user=agent)
	telephone = phn.objects.filter(user=agent)
	print(details)
	context = {
		'rcode':Rcode,
		'pattern':pattern,
		'details':details,
		'address': address,
		'telephone':telephone
	}
	return render(request, 'checkout/successful.html', context)


@login_required
def failed(request, Rcode, pattern):
	print(Rcode)
	print(pattern)
	context = {
		'rcode':Rcode,
		'pattern':pattern
	}
	return render(request, 'checkout/failed.html')


@login_required
def done(request, pattern):
	print(pattern)
	check = Checkout.objects.filter(patternkey=pattern)
	for items in check:
		agent = items.agent
		user = items.user
		Rcode = items.rcode
	bal = fund.objects.filter(user=agent)
	acct = InAcct.objects.filter(user=agent)
	for items in bal:
		remite = items.can_remite
		balance = items.balance
	Lcheck = RD.objects.filter(rcode=Rcode)
	for its in Lcheck:
		amount = its.amount
	for za in acct:
		balz = za.balance

	a = amount.split('0')
	charge = int(a[0])*100
	fix = int(charge) * 0.70
	print(amount)
	newbal = int(balance) - int(amount)
	print(acct)
	print(newbal)
	for item in bal:
		details = fund()
		details.pk = item.pk
		details.user = item.user
		details.can_remite = item.can_remite
		details.balance = newbal
		details.created = item.created
		details.save()
	if str('<QuerySet []>') in str(acct):
		print(details.user)
		detail = InAcct()
		detail.user = details.user
		detail.rcode = Rcode
		detail.pattern = pattern
		detail.balance = int(amount) 
		detail.xtrafund = fix
		detail.created = now
		detail.save()
	else:
		for itemz in acct:
			detail = InAcct()
			detail.pk = itemz.pk
			detail.user = itemz.user
			detail.rcode = itemz.rcode
			detail.pattern = itemz.pattern
			detail.balance = int(amount) + int(itemz.balance) 
			detail.xtrafund = fix + float(itemz.xtrafund)
			detail.created = itemz.created
			detail.save()
	context = {
		'rcode':Rcode,
		'pattern':pattern
	}
	return HttpResponseRedirect("http://passmecash.com/users/request/")