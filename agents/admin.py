from django.contrib import admin
from .models import (
	IsAgent, 
	Profile, 
	Address, 
	RequestDetail, 
	SentFunc,
	fund,
	visited,
	RCode,
	rating,
	ProfileAvatar,
	ProfilePic,
	IsVerified,
	InAcct,
	)

admin.site.register(IsAgent)
admin.site.register(Profile)
admin.site.register(Address)
admin.site.register(fund)
admin.site.register(RequestDetail)
admin.site.register(SentFunc)
admin.site.register(visited)
admin.site.register(RCode)
admin.site.register(rating)
admin.site.register(ProfileAvatar)
admin.site.register(ProfilePic)
admin.site.register(IsVerified)
admin.site.register(InAcct)
