from django.urls import path
from . import views

# SET THE NAMESPACE!
app_name = 'users'

#Define the URL
urlpatterns = [
    path('request/', views.home, name='request'),
    path('request/set_location', views.set_location, name='set_location'),
    path('request/all_request', views.reciept, name='reciept'),
    path('request/notificaations', views.noti, name='noti'),
    path('request/activites', views.act, name='act'),
    path('<str:username>/', views.user_profile, name='user_profile'),
    path('<str:username>/edit', views.user_profile_edit, name='user_profile_edit'),
    path('<str:username>/settings', views.setting, name='setting'),
    path('test/', views.test),
    path('request/agents/above/<int:amount>', views.agent_list, name='agent_list'),
    path('request/agents/above/<int:amount>/view_agent/!/<str:agent>', views.view_agent, name='view_agent'),
    path('request/agents/you-have-selected-<str:details>-to-pass-you-<int:amount>/<str:RCode>/<others>/<str:sent>', views.agent_selected, name='agent_selected'),
]