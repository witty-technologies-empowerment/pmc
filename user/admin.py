from django.contrib import admin
from .models import UserSession, GetInTouch, isNewUser, userSocial

admin.site.register(UserSession)
admin.site.register(GetInTouch)
admin.site.register(isNewUser)
admin.site.register(userSocial)
