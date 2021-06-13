from django.urls import path
from . import views
from accounts import views as view
from django.conf import settings
from django.conf.urls.static import static

# SET THE NAMESPACE!
app_name = 'agents'

urlpatterns=[
    path('register/', views.register, name='register'),
    #path('new_agent_login/', views.new_agent_login, name='new_agent_login'),
    path('new_agent_login/verify/new-account/', views.new_agent_login, name='new_agent_login_2'),
    path('new_<path>_login/verify/new-account/for-<str:username>', view.new_user_login, name='new_agent_login'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/withdraw', views.withdraw, name='withdraw'),
    path('dashboard/top_up', views.topup, name='topup'),
    path('dashboard/set_limit', views.setlimit, name='setlimit'),
    path('create/new_profile/', views.profile_add, name='new_profile'),
    path('request/from/<str:user>/to/pass-<int:amount>/<str:RCode>/<str:RDate>/<str:RTime>', views.userRequest, name='user_reuest'),
    path('request/response/<str:value>ed/<str:RCode>/<int:num>', views.agentResponse, name='response'),
    #path('request/response', views.responsePage, name='responsePage'),
]
# Be careful setting the name to just /login use userlogin instead!
