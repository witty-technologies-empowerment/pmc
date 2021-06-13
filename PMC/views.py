from django.shortcuts import render
from user.models import GetInTouch
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse
from agents.models import IsAgent as an_agent

def index(request):
	val = False
	if request.user.is_authenticated:
		username = request.user
		check = an_agent.objects.filter(user=username)
		print(check)
		for agent in check:
			val = agent.is_agent
		if val:
			return HttpResponseRedirect(reverse('agents:dashboard'))
		#else:
		else:
			return HttpResponseRedirect(reverse('users:request'))
	if request.method == "POST":
		name = request.POST.get('name')
		email = request.POST.get('email')
		message = request.POST.get('message')
		try:
			details = GetInTouch()
			details.name = name
			details.email = email
			details.message = message
			details.save()
			response = "Your message has been sent successfully"
			error = 'True'
		except:
			response = "Your message did not send due to some error! Try again soon"
			error = 'False'
		data = {
			'message': response,
			'error': error,
		}
		return render(request,'index.html', data)
	return render(request,'index.html')


def coming(request, link):
	if link == str('agents:dashboard'):
		link = 'agent'
	else:
		link = 'user'
	return render(request, 'coming.html', {'link':link})