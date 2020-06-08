from django.contrib import admin
from .models import Language, Profile, Group, GroupPost, GroupMembership, Event, EventPost, EventAttendance


admin.site.register(Language)
admin.site.register(Profile)

admin.site.register(Group)
admin.site.register(GroupPost)
admin.site.register(GroupMembership)

admin.site.register(Event)
admin.site.register(EventPost)
admin.site.register(EventAttendance)
