from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

# SET THE NAMESPACE!
app_name = 'checkout'

urlpatterns=[
    path('payment/!/user=!<str:user>/agent=!<str:agent>/refcode=!<str:Rcode>/PatternKey=!<str:pattern>/', views.checkout, name='checkout'),
    path('payment/!/process/refcode=!<str:Rcode>/PatternKey=!<str:pattern>/successful=!<str:status>', views.process, name='process'),
    path('payment/!/success/refcode=!<str:Rcode>/PatternKey=!<str:pattern>', views.successful, name='success'),
    path('payment/!/failed/refcode=!<str:Rcode>/PatternKey=!<str:pattern>', views.failed, name='failed'),
    path('payment/!/done/<str:pattern>/', views.done, name='done'),
    #path('new_agent_login/', views.new_agent_login, name='new_agent_login'),
    #path('new_agent_login/verify/new-account/', views.new_agent_login, name='new_agent_login_2'),
    #ath('new_agent_login/verify/new-account/for-<str:username>', views.new_agent_login, name='new_agent_login'),
    #path('dashboard/', views.dashboard, name='dashboard'),
    #path('create/new_profile/', views.profile_add, name='new_profile'),
    #path('request/from/<str:user>/to/pass-<int:amount>/<str:RCode>/<str:RDate>/<str:RTime>', views.userRequest, name='user_reuest'),
    #path('request/response/<str:value>ed/<str:RCode>/<int:num>', views.agentResponse, name='response'),
    #path('request/response', views.responsePage, name='responsePage'),
]
