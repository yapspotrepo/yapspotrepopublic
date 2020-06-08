from django.urls import path
from django.conf.urls import url, include
from . import views

urlpatterns = [
    path('profile/<int:profile_id>/', views.profile, name='profile'),
    path('profile/', views.profile, name='profile'),
    path('profileedit/', views.profileedit, name='profileedit'),
    path('profileavataredit/', views.profileavataredit, name='profileavataredit'),

    path('profilegroups/<int:profile_id>/', views.profilegroups, name='profilegroups'),
    path('profilegroupsadmin/<int:profile_id>/', views.profilegroupsadmin, name='profilegroupsadmin'),
    path('profilegroupsmember/<int:profile_id>/', views.profilegroupsmember, name='profilegroupsmember'),

    path('profileevents/', views.profileevents, name='profileevents'),
    path('profileeventsadmin/', views.profileeventsadmin, name='profileeventsadmin'),
    path('profileeventsattendee/', views.profileeventsattendee, name='profileeventsattendee'),
    path('profileeventspast/', views.profileeventspast, name='profileeventspast'),

    path('contact/', views.contact, name='contact'),

    path('dashboard/', views.dashboard, name='dashboard'),

    path('grouplist/', views.grouplist, name='grouplist'),
    path('groupcreate/', views.groupcreate, name='groupcreate'),
    path('groupview/<int:group_id>/', views.groupview, name='groupview'),
    path('groupconfirmdelete/<int:group_id>/', views.groupconfirmdelete, name='groupconfirmdelete'),
    path('groupedit/<int:group_id>/', views.groupedit, name='groupedit'),
    path('groupposts/<int:group_id>/', views.groupposts, name='groupposts'),
    path('groupmemberslist/<int:group_id>/', views.groupmemberslist, name='groupmemberslist'),
    path('groupeventslist/<int:group_id>/', views.groupeventslist, name='groupeventslist'),
    path('groupeventslistpast/<int:group_id>/', views.groupeventslistpast, name='groupeventslistpast'),

    path('eventlist/', views.eventlist, name='eventlist'),
    path('eventcreate/<int:group_id>/', views.eventcreate, name='eventcreate'),
    path('eventview/<int:event_id>/', views.eventview, name='eventview'),
    path('eventconfirmdelete/<int:event_id>/', views.eventconfirmdelete, name='eventconfirmdelete'),
    path('eventposts/<int:event_id>/', views.eventposts, name='eventposts'),
    path('eventedit/<int:event_id>/', views.eventedit, name='eventedit'),
    path('eventattendeelist/<int:event_id>/', views.eventattendeelist, name='eventattendeelist'),
]