from django.urls import path
from . import views

# SET THE NAMESPACE!
app_name = 'accounts'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='user_login'),
    path('recovery/', views.recover, name='recover'),
	path('registration/<path>/verify/new-account/for-<str:username>', views.new_user_login, name='new_user_login'),
    path('profile/<str:username>=!<int:pk>', views.profile, name='profile'),
]