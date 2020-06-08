from django.http import HttpResponseRedirect
from django.urls import reverse
from .models import Group, Event


def user_can_edit_group(function):
    '''
    Make sure this user can edit this group.  Redirects otherwise.
    '''
    def wrap(request, *args, **kwargs):
        group_id = kwargs['group_id']

        try:
            group_id = int(group_id)
        except:
            messages.error(request, _('Error: Cannot find group.'))
            return HttpResponseRedirect(reverse('grouplist'))

        this_group = Group.objects.filter(pk=group_id).first()
        if this_group is None:
            messages.error(request, _('Error: Cannot find group.'))
            return HttpResponseRedirect(reverse('grouplist'))

        if request.user.profile == this_group.admin:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('grouplist'))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap


def user_can_edit_event(function):
    '''
    Make sure this user can edit this event.  Redirects otherwise.
    '''
    def wrap(request, *args, **kwargs):
        event_id = kwargs['event_id']

        try:
            event_id = int(event_id)
        except:
            messages.error(request, _('Error: Cannot find event.'))
            return HttpResponseRedirect(reverse('eventlist'))

        this_event = Event.objects.filter(pk=event_id).first()
        if this_event is None:
            messages.error(request, _('Error: Cannot find event.'))
            return HttpResponseRedirect(reverse('eventlist'))

        if request.user.profile == this_event.admin:
            return function(request, *args, **kwargs)
        else:
            return HttpResponseRedirect(reverse('eventlist'))

    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap
