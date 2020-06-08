from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext as _
from django.http import HttpResponseRedirect
from .models import Language, Profile, Event, Group, EventPost, GroupPost, EventAttendance
from .forms import ProfileForm, ProfileAvatarForm, GroupForm, GroupPostForm, GroupFilterForm, \
GroupSearchForm, EventForm, EventPostForm, EventFilterForm, EventSearchForm, ContactForm
from .decorators import user_can_edit_group, user_can_edit_event
from ipware import get_client_ip
from django.contrib.gis.geoip2 import GeoIP2
from allauth.account.signals import user_logged_in
import datetime
from django.utils import timezone
from .utils import COUNTRY_CHOICES_DICT
import re
from django.db.models import F, Q
from yapspot.settings import DJANGO_ENV
import pytz
from allauth.account.views import SignupView
from yap.forms import CustomSignupForm
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
import bleach
from django.core.mail import EmailMessage
import json
import collections, numpy
import math
from .utils import bleach_before_database
from django.core.mail import send_mail
from allauth.account.views import PasswordChangeView
from django.contrib.auth import update_session_auth_hash
from allauth.account.adapter import get_adapter
from allauth.account import signals
from allauth.account.admin import EmailAddress
from math import floor
from django.urls import reverse
from six.moves.urllib.parse import urlparse
from bleach.linkifier import Linker
from yap.utils import make_and_send_event_email


MINUTES_PRIOR_TO_EVENT_CAN_EDIT = 30


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ FUNCTIONS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def get_time_zone(request):
    """
    If authenticated try to get time_zone from profile.  otherwise get it from IP address.
    """

    try:
        # if user is authenticated then try to get timezone from their profile
        if request.user.is_authenticated and request.user.profile.time_zone != "":
            local_tz = pytz.timezone(request.user.profile.time_zone)
            return local_tz
        else:
            # if not authenticated, try to get timezone from sessions (may have been stored previously see below)
            session_timezone = request.user.session.get("timezone", "")
            if session_timezone != "":
                local_tz = pytz.timezone(session_timezone)
            return local_tz
    except: pass

    # if made it this far, then timezone was not in profile or session
    # will attempt to estimate timezone based off ip address GeoIP2.
    this_ip_address, is_routable = get_client_ip(request)

    #if DJANGO_ENV == "DEV":
    #    this_ip_address = "24.185.173.103"

    location_time_zone = "America/New_York"
    if this_ip_address != "127.0.0.1":
        try:
            g = GeoIP2()
            location = g.city(this_ip_address)
            location_time_zone = location["time_zone"]

            # if you got a timeozne from GeoIP, then store it in session so you 
            # don't have to do this over and over again.
            request.user.session["time_zone"] = location_time_zone
        except: pass

    local_tz = pytz.timezone(location_time_zone)

    return local_tz


def get_ip_and_geoip(request):
    this_ip_address = "N/A"
    location_city = "N/A"
    location_region = "N/A"
    location_country = "N/A"
    location_country_code = "N/A"
    location_time_zone = None

    this_ip_address, is_routable = get_client_ip(request)

    if DJANGO_ENV == "DEV":
        this_ip_address = "24.185.173.103"

    if this_ip_address != "127.0.0.1":
        try:
            g = GeoIP2()
            location = g.city(this_ip_address)
            location_city = location["city"]
            location_region = location["region"]
            location_country = location["country_name"]
            location_country_code = location["country_code"]
            location_time_zone = location["time_zone"]
        except: pass

    return this_ip_address, location_city, location_region, location_country, location_country_code, location_time_zone


def somebody_logged_in(request, user, **kwargs):
    """
    This is to set timezone and preferred language automatically.
    They can edit it later if they want.
    """
    try:
        if request.user.is_authenticated:
            need_to_save = False

            if request.user.profile.time_zone == "" or request.user.profile.country == "":
                this_ip_address, location_city, location_region, location_country, location_country_code, location_time_zone = get_ip_and_geoip(request)

                if request.user.profile.time_zone == "":
                    request.user.profile.time_zone = location_time_zone
                    need_to_save = True

                if request.user.profile.country == "" and location_country_code in COUNTRY_CHOICES_DICT.keys():
                    request.user.profile.country = location_country_code
                    need_to_save = True

            if request.user.profile.language_preferred == None:
                language_code = request.LANGUAGE_CODE

                this_language = Language.objects.filter(two_letter_code=language_code).first()
                if this_language is not None:
                    request.user.profile.language_preferred = this_language
                    need_to_save = True

            if need_to_save:
                request.user.profile.save()
    except: pass

user_logged_in.connect(somebody_logged_in)


def calculate_time_until_appointment(start_time, end_time):
    """
    Get time until event begins.
    """

    if start_time < timezone.now() < end_time:
        return "Event currently on-going."

    elif timezone.now() > end_time:
        return "Event hast passed."

    time_difference_to_start = (start_time - timezone.now()).total_seconds() / 60

    days = floor(time_difference_to_start / 1440)
    hours = floor((time_difference_to_start - (days * 1440)) / 60)
    minutes = floor(time_difference_to_start - ((days * 1440) + (hours * 60)))

    start_time_countdown_string = "Starts in"
    if days > 0:
        start_time_countdown_string += " " + str(days)
        if days == 1:
            start_time_countdown_string += " day"
        else:
            start_time_countdown_string += " days"
    if hours > 0:
        start_time_countdown_string += " " + str(hours)
        if hours == 1:
            start_time_countdown_string += " hour"
        else:
            start_time_countdown_string += " hours"
    if days < 1 and minutes > 0:
        start_time_countdown_string += " " + str(minutes)
        if minutes == 1:
            start_time_countdown_string += " min"
        else:
            start_time_countdown_string += " min"

    if start_time_countdown_string == "Starts in":
        start_time_countdown_string = "Starts in less than 1 minute."

    return start_time_countdown_string


def set_target_linkify(attrs, new=False):
    """
    for making links in description.
    """
    p = urlparse(attrs[(None, 'href')])
    if p.netloc not in ['my-domain.com', 'other-domain.com']:
        attrs[(None, 'target')] = '_blank'
        attrs[(None, 'class')] = 'external'
    else:
        attrs.pop((None, 'target'), None)
    return attrs


def create_group_json(all_groups, user_request=None):
    """ Make JSON out of data so you can render it with Vue.js """

    if user_request.user.is_authenticated:
        user_is_authenticated = True
        this_profile = user_request.user.profile
    else:
        user_is_authenticated = False
        this_profile = None

    all_groups_json = []
    for group in all_groups:
        try:
            this_group_json = {
                "group_url": reverse('groupview', kwargs={"group_id":group.pk}), 
                "group_avatar_url": group.get_avatar_thumbnail(), 
                "name": bleach_before_database(group.name), 
                "admin_url": reverse('profile', kwargs={"profile_id":group.admin.pk}), 
                "admin_name": bleach_before_database(group.admin.__str__()), 
                "admin_is_user": user_is_authenticated and this_profile == group.admin, 
                "description": group.get_group_description(), 
                "activity_category": bleach_before_database(group.get_activity_category_display()), 
                "member_count": group.member_count,
                "language_primary": group.get_language_name()
            }
            all_groups_json.append(this_group_json)
        except: pass

    return json.dumps(all_groups_json)


def create_event_json(all_events, local_tz, user_request=None):
    """ Make JSON out of data so you can render it with Vue.js """

    if user_request.user.is_authenticated:
        user_is_authenticated = True
        this_profile = user_request.user.profile
    else:
        user_is_authenticated = False
        this_profile = None

    all_events_json = []
    for event in all_events:
        try:
            this_event = {
                "event_pk": event.pk,
                "event_url": reverse('eventview', kwargs={"event_id":event.pk}),
                "event_avatar_url": event.get_avatar_thumbnail(), 
                "name": bleach_before_database(event.name),
                "group_url": reverse('groupview', kwargs={"group_id":event.group.pk}),
                "group_name": bleach_before_database(event.group.__str__()),
                "admin_url": reverse('profile', kwargs={"profile_id":event.admin.pk}),
                "admin_name": bleach_before_database(event.admin.__str__()),
                "admin_is_user": user_is_authenticated and this_profile == event.admin, 
                "start_time": event.start_time.astimezone(local_tz).strftime("%A, %b %-d, %Y at %-I:%M %p %Z"),
                "description": event.get_event_description(),
                #"activity_category": bleach_before_database(event.get_activity_category_display()), 
                "language_primary": event.get_language_name(),
                "attendee_count": event.attendee_count,
                "maximum_attendee_count": event.maximum_attendee_count,
                "time_until_event_start": calculate_time_until_appointment(event.start_time, event.end_time)
            }
            all_events_json.append(this_event)
        except: pass

    return json.dumps(all_events_json)


def create_post_json(all_posts, local_tz):
    all_posts_json = []
    for post in all_posts:
        try:
            this_post = {
                "post_pk":post.pk,
                "poster_url": reverse('profile', kwargs={"profile_id":post.poster.pk}),
                "profile_avatar_micro_url": post.poster.get_avatar_thumbnail_micro(),
                "poster_name": bleach_before_database(post.poster.__str__()),
                "post_text": bleach_before_database(post.post_text),
                "created_at": post.created_at.astimezone(local_tz).strftime("%b %-d, %Y at %-I:%M %p %Z"),
            }
            all_posts_json.append(this_post)
        except: pass

    return json.dumps(all_posts_json)


def create_profile_json(all_profiles, local_tz):
    all_profiles_json = []
    for profile in all_profiles:
        try:
            this_profile = {
                "profile_pk": profile.pk,
                "profile_url": reverse('profile', kwargs={"profile_id":profile.pk}),
                "profile_name": bleach_before_database(profile.name.__str__()),
                "profile_avatar_micro_url": profile.get_avatar_thumbnail_micro(),
            }
            all_profiles_json.append(this_profile)
        except: pass

    return json.dumps(all_profiles_json)


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ UNAUTHENTICATED PAGES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def index(request):
    if request.user.is_authenticated:
        return HttpResponseRedirect(reverse('eventlist'))
    return render(request, 'yap/index/index.html')


def tos(request):
    return render(request, 'yap/index/tos.html')


class CustomSignupView(SignupView):
    """ class-based view for teacher signup """
    template_name = 'account/signup.html'
    form_class = CustomSignupForm
    view_name = 'custom_signup'
    success_url = '/yap/eventlist/'

custom_signup = CustomSignupView.as_view()


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CONTACT PAGE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def process_contact_form(form):
    try:
        message = form.cleaned_data.get('message')
        if form.cleaned_data.get('name') != "":
            message += "\n\n [from " + form.cleaned_data.get('name') + "]"

        ## These 3 lines below are to make a Reply link that has the original message in it.
        message_initial = message
        message += "<br><br><br><a href='mailto:" + form.cleaned_data.get('email') + "?subject=Re: Contact"
        message += "&body=/////" + message_initial + "'>Reply</a>"

        reply_to_email = form.cleaned_data.get('email')
        email_message = EmailMessage("YapSpot Contact", message, 'hello@yapspot.com', ['hello@yapspot.com'],
                                     headers={'Reply-To': reply_to_email})
        email_message.content_subtype = "html"
        email_message.send()
        return True
    except:
        return False


def contact(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            success = process_contact_form(form)
            if success:
                messages.success(request, 'Messages sent successfully.  We will email you back a response promptly.')
            else:
                messages.error(request, 'Error sending message.  Try again later.')
            return HttpResponseRedirect(reverse('index'))
    else:
        form = ContactForm()
    return render(request, 'yap/index/contact.html', {'form': form})


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PROFILE PAGES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


@login_required
def profile(request, profile_id=None):
    """
    view users profile
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('eventlist'))

    if request.user.profile == this_profile:
        user_can_edit_profile = True
        show_email_verification_link = not EmailAddress.objects.filter(user=request.user, verified=True).exists()
    else:
        user_can_edit_profile = False
        show_email_verification_link = False

    # get avatar
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()


    return render(request, 'yap/profile/profile.html', {'this_profile':this_profile, 
                                                        'this_profile_avatar_url':this_profile_avatar_url,
                                                        'user_can_edit_profile':user_can_edit_profile,
                                                        'show_email_verification_link':show_email_verification_link
                                                        })


@login_required
def profileedit(request):
    """
    Edit user profile
    """

    this_profile = request.user.profile

    if request.method == 'POST':
        profile_form = ProfileForm(request.POST, instance=this_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, _('Your information were successfully updated!'))
            return HttpResponseRedirect(reverse('profile'))
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        profile_form = ProfileForm(instance=this_profile)

    return render(request, 'yap/profile/profileedit.html', {'this_profile':this_profile, 'profile_form':profile_form})


@login_required
def profileavataredit(request):
    """
    Edit user profile
    """

    this_profile = request.user.profile

    if request.method == 'POST':
        profile_form = ProfileAvatarForm(request.POST, request.FILES, instance=this_profile)
        if profile_form.is_valid():
            profile_form.save()
            messages.success(request, _('Your profile avatar was successfully updated!'))
            return HttpResponseRedirect(reverse('profile'))
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        profile_form = ProfileAvatarForm(instance=this_profile)

    return render(request, 'yap/profile/profileedit.html', {'this_profile':this_profile, 'profile_form':profile_form})


@login_required
def profilegroups(request, profile_id=None):
    """
    view users groups.
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_groups = Group.objects.select_related("admin").select_related("language_primary").filter(Q(admin=this_profile) | Q(member=this_profile)).order_by("updated_at")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_groups, 10)
    try:
        all_groups = paginator.page(page)
    except PageNotAnInteger:
        all_groups = paginator.page(1)
    except EmptyPage:
        all_groups = paginator.page(paginator.num_pages)
    all_groups_json = create_group_json(all_groups, request)

    # get profile avatar url
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()

    return render(request, 'yap/profile/groups/profilegroups.html', {'this_profile':this_profile, 
                                                                     'this_profile_avatar_url':this_profile_avatar_url,
                                                                     'all_groups':all_groups,
                                                                     'all_groups_json':all_groups_json})

@login_required
def profilegroupsadmin(request, profile_id=None):
    """
    view users groups.
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_groups = Group.objects.select_related("admin").select_related("language_primary").filter(admin=this_profile).order_by("updated_at")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_groups, 10)
    try:
        all_groups = paginator.page(page)
    except PageNotAnInteger:
        all_groups = paginator.page(1)
    except EmptyPage:
        all_groups = paginator.page(paginator.num_pages)
    all_groups_json = create_group_json(all_groups, request)

    # get profile avatar url
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()

    return render(request, 'yap/profile/groups/profilegroupsadmin.html', {'this_profile':this_profile, 
                                                                          'this_profile_avatar_url':this_profile_avatar_url,
                                                                          'all_groups':all_groups,
                                                                          'all_groups_json':all_groups_json})


@login_required
def profilegroupsmember(request, profile_id=None):
    """
    view users groups.
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_groups = Group.objects.select_related("admin").select_related("language_primary").filter(member=this_profile).order_by("updated_at")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_groups, 10)
    try:
        all_groups = paginator.page(page)
    except PageNotAnInteger:
        all_groups = paginator.page(1)
    except EmptyPage:
        all_groups = paginator.page(paginator.num_pages)
    all_groups_json = create_group_json(all_groups, request)

    # get profile avatar url
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()

    return render(request, 'yap/profile/groups/profilegroupsmember.html', {'this_profile':this_profile, 
                                                                           'this_profile_avatar_url':this_profile_avatar_url,
                                                                           'all_groups':all_groups,
                                                                           'all_groups_json':all_groups_json})


@login_required
def profileevents(request):
    """
    view users groups.
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter((Q(admin=this_profile) | Q(attendee=this_profile)) & Q(end_time__gte=timezone.now())).distinct().order_by("start_time")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_events, 10)
    try:
        all_events = paginator.page(page)
    except PageNotAnInteger:
        all_events = paginator.page(1)
    except EmptyPage:
        all_events = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_events_json = create_event_json(all_events, local_tz, request)

    # get profile avatar url
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()

    return render(request, 'yap/profile/events/profileevents.html', {'this_profile':this_profile, 
                                                                     'this_profile_avatar_url':this_profile_avatar_url,
                                                                     'all_events':all_events,
                                                                     'all_events_json':all_events_json})


@login_required
def profileeventspast(request):
    """
    view users groups.
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter((Q(admin=this_profile) | Q(attendee=this_profile)) & Q(end_time__lt=timezone.now())).distinct().order_by("-start_time")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_events, 10)
    try:
        all_events = paginator.page(page)
    except PageNotAnInteger:
        all_events = paginator.page(1)
    except EmptyPage:
        all_events = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_events_json = create_event_json(all_events, local_tz, request)

    # get profile avatar url
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()

    return render(request, 'yap/profile/events/profileeventspast.html', {'this_profile':this_profile, 
                                                                         'this_profile_avatar_url':this_profile_avatar_url,
                                                                         'all_events':all_events,
                                                                         'all_events_json':all_events_json})

@login_required
def profileeventsadmin(request):
    """
    view users groups.
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter(admin=this_profile, end_time__gte=timezone.now()).order_by("start_time")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_events, 10)
    try:
        all_events = paginator.page(page)
    except PageNotAnInteger:
        all_events = paginator.page(1)
    except EmptyPage:
        all_events = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_events_json = create_event_json(all_events, local_tz, request)

    # get profile avatar url
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()

    return render(request, 'yap/profile/events/profileeventsadmin.html', {'this_profile':this_profile, 
                                                                          'this_profile_avatar_url':this_profile_avatar_url,
                                                                          'all_events':all_events,
                                                                          'all_events_json':all_events_json})


@login_required
def profileeventsattendee(request):
    """
    view users groups.
    """

    try:
        profile_id = int(profile_id)
    except:
        profile_id = None

    if profile_id:
        this_profile = Profile.objects.filter(pk=profile_id).first()
    else:
        this_profile = request.user.profile

    if this_profile is None:
        messages.error(request, _('Error: Cannot find user profile.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter(attendee=this_profile, end_time__gte=timezone.now()).order_by("start_time")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_events, 10)
    try:
        all_events = paginator.page(page)
    except PageNotAnInteger:
        all_events = paginator.page(1)
    except EmptyPage:
        all_events = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_events_json = create_event_json(all_events, local_tz, request)

    # get profile avatar url
    this_profile_avatar_url = this_profile.get_avatar_thumbnail()

    return render(request, 'yap/profile/events/profileeventsattendee.html', {'this_profile':this_profile, 
                                                                             'this_profile_avatar_url':this_profile_avatar_url,
                                                                             'all_events':all_events,
                                                                             'all_events_json':all_events_json})


@login_required
def dashboard(request):
    """
    dashboard
    """

    local_tz =  get_time_zone(request)

    # events where user is the admin
    my_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter((Q(admin=request.user.profile) | Q(attendee=request.user.profile)) & Q(end_time__gte=timezone.now())).distinct().order_by("start_time")
    my_events_count = Event.objects.filter((Q(admin=request.user.profile) | Q(attendee=request.user.profile)) & Q(end_time__gte=timezone.now())).count()

    page = request.GET.get('page', 1)
    paginator = Paginator(my_events, 10)
    try:
        my_events = paginator.page(page)
    except PageNotAnInteger:
        my_events = paginator.page(1)
    except EmptyPage:
        my_events = paginator.page(paginator.num_pages)

    my_events_json = create_event_json(my_events, local_tz, request)

    return render(request, 'yap/profile/dashboard.html', {'my_events':my_events,
                                                          'my_events_json':my_events_json,
                                                          'my_events_count':my_events_count,
                                                          })



""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ CUSTOM PASSWORD CHANGE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


class MyPasswordChangeView(PasswordChangeView):
    """ Custom class to override the password change view """
    success_url = "/"

    # Override form valid view to keep user logged i
    def form_valid(self, form):
        form.save()
        # Update session to keep user logged in.
        update_session_auth_hash(self.request, form.user)
        get_adapter().add_message(self.request, messages.SUCCESS, 'account/messages/password_changed.txt')
        signals.password_changed.send(sender=self.request.user.__class__, request=self.request, user=self.request.user)
        return super(PasswordChangeView, self).form_valid(form)


password_change = login_required(MyPasswordChangeView.as_view())


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GROUP PAGES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def grouplist(request):
    """
    list groups.
    """
    selected_category, selected_language = "", None
    all_groups = None

    # get user preferences for group category and language
    if request.method == 'GET' and "search_form" in request.GET:
        group_search_form = GroupSearchForm(request.GET)
        if group_search_form.is_valid():
            search_term = group_search_form.cleaned_data.get('search_term')
            search_term = bleach_before_database(search_term)

            if search_term != "":
                all_groups = Group.objects.select_related("admin").select_related("language_primary").filter(Q(name__icontains=search_term) | Q(description__icontains=search_term)).order_by("-updated_at")
            else:
                all_groups = Group.objects.select_related("admin").select_related("language_primary").all().order_by("-updated_at")

        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        group_search_form = GroupSearchForm()


    # get user preferences for group category and language
    if request.method == 'GET' and "filter_form" in request.GET:
        group_filter_form = GroupFilterForm(request.GET)
        if group_filter_form.is_valid():
            selected_category = group_filter_form.cleaned_data.get('activity_category')
            selected_language = group_filter_form.cleaned_data.get('language_primary')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        group_filter_form = GroupFilterForm()


    if all_groups is None:
        # make search query and retrieve matching groups.
        group_query = Q()

        if selected_category != "":
            group_query &= Q(activity_category=selected_category)

        if selected_language is not None:
            group_query &= Q(language_primary=selected_language)

        if group_query == Q():
            all_groups = Group.objects.select_related("admin").select_related("language_primary").all().order_by("-updated_at")
        else:
            all_groups = Group.objects.select_related("admin").select_related("language_primary").filter(group_query).order_by("-updated_at")


    page = request.GET.get('page', 1)
    paginator = Paginator(all_groups, 10)
    try:
        all_groups = paginator.page(page)
    except PageNotAnInteger:
        all_groups = paginator.page(1)
    except EmptyPage:
        all_groups = paginator.page(paginator.num_pages)

    all_groups_json = create_group_json(all_groups, request)

    return render(request, 'yap/group/grouplist.html', {'all_groups':all_groups, 
                                                        'all_groups_json': all_groups_json,
                                                        'group_filter_form':group_filter_form,
                                                        'group_search_form':group_search_form})


@login_required
def groupcreate(request, group_id=None):
    """
    create a group
    """

    if request.method == 'POST':
        group_form = GroupForm(request.POST, request.FILES)
        if group_form.is_valid():
            saved_group = group_form.save(commit=False)
            saved_group.admin = request.user.profile
            saved_group.save()

            messages.success(request, _('Your group was successfully created!'))
            return HttpResponseRedirect(reverse('groupview', kwargs={'group_id':saved_group.pk}))
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        group_form = GroupForm()

    return render(request, 'yap/group/groupcreate.html', {'group_form':group_form})


def groupview(request, group_id=None):
    """
    view info about a group
    """
    user_can_edit_group, already_in_group = False, False
    group_post_form, all_posts_count, all_posts_json = None, None, None

    try:
        group_id = int(group_id)
    except:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    this_group = Group.objects.filter(pk=group_id).first()
    if this_group is None:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    if request.user.is_authenticated:

        # join the group
        if request.method == 'POST' and "join_group" in request.POST:
            # make sure not already listed under attendees
            if request.user.profile == this_group.admin:
                    messages.success(request, _('You are already the admin of the group.'))

            elif request.user.profile in this_group.member.all():
                messages.success(request, _('You are already a member of the group!'))

            else:
                # make sure the attendee count is less than maximum_attendee_count.
                current_member_count = this_group.member.count() + 1 # plus 1 is to add the admin.
                this_group.member.add(request.user.profile)
                this_group.member_count = current_member_count + 1
                this_group.save()
                messages.success(request, _('Successfully joined the group!'))


        # leave the group
        elif request.method == 'POST' and "leave_group" in request.POST:
            if not request.user.profile in this_group.member.all():
                messages.error(request, _('You are not a member of this group!'))

            else:
                this_group.member.remove(request.user.profile)
                this_group.member_count = this_group.member.count() + 1 # plus 1 is to add the admin.
                this_group.save()
                messages.success(request, _('Successfully left group!'))


        # for posting to group in discussion section.
        if request.method == 'POST' and "create_post" in request.POST:
            group_post_form = GroupPostForm(request.POST)
            if group_post_form.is_valid():
                saved_group_post = group_post_form.save(commit=False)
                saved_group_post.group = this_group
                saved_group_post.poster = request.user.profile
                saved_group_post.created_at = timezone.now()
                saved_group_post.save()
                messages.success(request, _('Your post was successfully created!'))
                group_post_form = GroupPostForm()
            else:
                messages.error(request, _('Please correct the error below.'))
        else:
            group_post_form = GroupPostForm()


        # get list of posts
        all_posts = GroupPost.objects.filter(group=this_group).order_by("-created_at")[:5]
        all_posts_count = GroupPost.objects.filter(group=this_group).count()
        local_tz = get_time_zone(request)
        all_posts_json = create_post_json(all_posts, local_tz)


        # only the admin can edit the group
        if request.user.is_authenticated and request.user.profile == this_group.admin:
            user_can_edit_group = True
        else:
            user_can_edit_group = False

        # check if user is already in group
        if request.user.profile in this_group.member.all():
            already_in_group = True
        else:
            already_in_group = False

    # get upcoming events
    upcoming_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter(group=this_group, end_time__gte=timezone.now()).order_by("start_time")[:3]
    upcoming_events_count = Event.objects.filter(group=this_group, end_time__gte=timezone.now()).count()
    local_tz = get_time_zone(request)
    all_events_json = create_event_json(upcoming_events, local_tz, request)

    # get group avatar url
    this_group_avatar_url = this_group.get_avatar_thumbnail()

    # linkify group description
    linker = Linker(callbacks=[set_target_linkify])
    group_description = linker.linkify(this_group.description)

    return render(request, 'yap/group/groupview.html', {'this_group':this_group, 
                                                        'user_can_edit_group':user_can_edit_group,
                                                        'this_group_avatar_url':this_group_avatar_url,
                                                        'already_in_group':already_in_group,
                                                        'all_events_json':all_events_json,
                                                        'upcoming_events_count':upcoming_events_count,
                                                        'group_description':group_description,
                                                        'group_post_form':group_post_form,
                                                        'all_posts_count':all_posts_count,
                                                        'all_posts_json':all_posts_json})


@login_required
@user_can_edit_group
def groupconfirmdelete(request, group_id=None):
    this_group = Group.objects.get(pk=group_id)

    if request.method == 'POST' and "delete_group" in request.POST:
        this_group.delete()
        messages.success(request, _('Successfully deleted the group!'))
        return HttpResponseRedirect(reverse('profilegroups', kwargs={"profile_id":this_group.admin.pk}))

    this_group_avatar_url = this_group.get_avatar_thumbnail()

    return render(request, 'yap/group/groupconfirmdelete.html', {'this_group':this_group,
                                                                 'this_group_avatar_url':this_group_avatar_url})


@login_required
def groupposts(request, group_id=None):
    """
    Group discussion
    """

    try:
        group_id = int(group_id)
    except:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    this_group = Group.objects.filter(pk=group_id).first()
    if this_group is None:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))


    # for posting to group in discussion section.
    if request.method == 'POST' and "create_post" in request.POST:
        group_post_form = GroupPostForm(request.POST)
        if group_post_form.is_valid():
            saved_group_post = group_post_form.save(commit=False)
            saved_group_post.group = this_group
            saved_group_post.poster = request.user.profile
            saved_group_post.created_at = timezone.now()
            saved_group_post.save()
            messages.success(request, _('Your post was successfully created!'))
            group_post_form = GroupPostForm()
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        group_post_form = GroupPostForm()

    all_posts = GroupPost.objects.filter(group=this_group).order_by("-created_at")
    all_posts_count = GroupPost.objects.filter(group=this_group).count()

    page = request.GET.get('page', 1)
    paginator = Paginator(all_posts, 10)
    try:
        all_posts = paginator.page(page)
    except PageNotAnInteger:
        all_posts = paginator.page(1)
    except EmptyPage:
        all_posts = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_posts_json = create_post_json(all_posts, local_tz)

    return render(request, 'yap/group/groupposts.html', {'this_group':this_group, 
                                                         'group_post_form':group_post_form,
                                                         'all_posts_count':all_posts_count,
                                                         'all_posts':all_posts,
                                                         'all_posts_json':all_posts_json})


@login_required
@user_can_edit_group
def groupedit(request, group_id=None):
    """
    edit a group
    """

    this_group = Group.objects.get(pk=group_id)

    if request.method == 'POST':
        group_form = GroupForm(request.POST, request.FILES, instance=this_group)
        if group_form.is_valid():
            group_form.save()
            messages.success(request, _('Your group was successfully edited!'))
            return HttpResponseRedirect(reverse('groupview', kwargs={'group_id':this_group.pk}))
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        group_form = GroupForm(instance=this_group)

    return render(request, 'yap/group/groupedit.html', {'this_group':this_group, 'group_form':group_form})


def groupmemberslist(request, group_id=None):
    """
    List all members of the group.
    IMPROVEMENT: add pagination
    """
    try:
        group_id = int(group_id)
    except:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    this_group = Group.objects.filter(pk=group_id).first()
    if this_group is None:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    group_members = this_group.member.all()
    member_count = this_group.member_count

    local_tz = get_time_zone(request)
    all_profiles_json = create_profile_json(group_members, local_tz)

    return render(request, 'yap/group/groupmemberslist.html', {'this_group':this_group, 
                                                               'all_profiles_json':all_profiles_json,
                                                               'member_count':member_count})


def groupeventslist(request, group_id=None):
    """
    List all members of the group.
    """
    try:
        group_id = int(group_id)
    except:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    this_group = Group.objects.filter(pk=group_id).first()
    if this_group is None:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter(group=this_group, end_time__gte=timezone.now()).order_by("start_time")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_events, 10)
    try:
        all_events = paginator.page(page)
    except PageNotAnInteger:
        all_events = paginator.page(1)
    except EmptyPage:
        all_events = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_events_json = create_event_json(all_events, local_tz, request)

    return render(request, 'yap/group/groupeventslist.html', {'this_group':this_group, 
                                                              'all_events':all_events,
                                                              'all_events_json':all_events_json})


def groupeventslistpast(request, group_id=None):
    """
    List all members of the group.
    """
    try:
        group_id = int(group_id)
    except:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    this_group = Group.objects.filter(pk=group_id).first()
    if this_group is None:
        messages.error(request, _('Error: Cannot find group.'))
        return HttpResponseRedirect(reverse('grouplist'))

    all_events = Event.objects.select_related("admin").select_related("language_primary").select_related("group").filter(group=this_group, end_time__lt=timezone.now()).order_by("-start_time")

    page = request.GET.get('page', 1)
    paginator = Paginator(all_events, 10)
    try:
        all_events = paginator.page(page)
    except PageNotAnInteger:
        all_events = paginator.page(1)
    except EmptyPage:
        all_events = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_events_json = create_event_json(all_events, local_tz, request)

    return render(request, 'yap/group/groupeventslistpast.html', {'this_group':this_group, 
                                                                  'all_events':all_events,
                                                                  'all_events_json':all_events_json})

""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT PAGES ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def eventlist(request):
    """
    view events list.
    """
    selected_category, selected_language = "", None
    all_events = None


    # get user search term
    if request.method == 'GET' and "search_form" in request.GET:
        event_search_form = EventSearchForm(request.GET)
        if event_search_form.is_valid():
            search_term = event_search_form.cleaned_data.get('search_term')
            search_term = bleach_before_database(search_term)

            if search_term != "":
                all_events = Event.objects.select_related("admin").select_related("language_primary").filter( (Q(name__icontains=search_term) | Q(description__icontains=search_term)) & 
                                                                                                               Q(end_time__gt=timezone.now()) ).order_by("-updated_at")
            else:
                all_events = Event.objects.select_related("admin").select_related("language_primary").filter( Q(end_time__gt=timezone.now()) ).order_by("-updated_at")
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        event_search_form = EventSearchForm()


    # get user preferences for event category and language
    if request.method == 'GET' and "filter_form" in request.GET:
        event_filter_form = EventFilterForm(request.GET, request.FILES)
        if event_filter_form.is_valid():
            selected_category = event_filter_form.cleaned_data.get('activity_category')
            selected_language = event_filter_form.cleaned_data.get('language_primary')
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        event_filter_form = EventFilterForm()


    if request.method == 'GET' and "onlymygroups" in request.GET:
        my_groups = Group.objects.filter( Q(member=request.user.profile) | Q(admin=request.user.profile)).values('pk')
        all_events = Event.objects.filter( Q(pk__in=my_groups) & Q(end_time__gt=timezone.now())).order_by("start_time")


    if all_events is None:
        # make search query and retrieve matching events.
        event_query = Q()

        if selected_category != "":
            event_query &= Q(activity_category=selected_category)

        if selected_language is not None:
            event_query &= Q(language_primary=selected_language)

        if event_query == Q():
            all_events = Event.objects.select_related("admin").select_related("language_primary").filter( Q(attendee_count__lt=F('maximum_attendee_count')) & 
                                                                                                          Q(end_time__gt=timezone.now()) 
                                                                                                          ).order_by("start_time")
        else:
            all_events = Event.objects.select_related("admin").select_related("language_primary").filter( event_query & 
                                                                                                          Q(attendee_count__lt=F('maximum_attendee_count')) & 
                                                                                                          Q(end_time__gt=timezone.now()) 
                                                                                                          ).order_by("start_time")


    page = request.GET.get('page', 1)
    paginator = Paginator(all_events, 10)
    try:
        all_events = paginator.page(page)
    except PageNotAnInteger:
        all_events = paginator.page(1)
    except EmptyPage:
        all_events = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_events_json = create_event_json(all_events, local_tz, request)

    return render(request, 'yap/event/eventlist.html', {'all_events':all_events, 
                                                        'all_events_json':all_events_json,
                                                        'event_filter_form':event_filter_form,
                                                        'event_search_form':event_search_form})


@login_required
@user_can_edit_group
def eventcreate(request, group_id=None):
    """
    create an event.
    """

    this_group = Group.objects.get(pk=group_id)

    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES)
        if event_form.is_valid():
            saved_event = event_form.save(commit=False)
            saved_event.admin = request.user.profile
            saved_event.group = this_group

            # adjust start_time to selected time zone
            local_timezone = pytz.timezone(saved_event.time_zone)
            saved_event.start_time = local_timezone.localize(saved_event.start_time.replace(tzinfo=None))
            saved_event.end_time = saved_event.start_time + datetime.timedelta(minutes=saved_event.duration)

            # make random name for group in case using Jitsi
            saved_event.event_videochat_room_base_name = saved_event.create_jitsi_event_videochat_room_name()

            # no avatar uploaded then default to the avatar for the group.
            try:
                if not bool(saved_event.avatar) and bool(saved_event.group.avatar):
                    saved_event.avatar = saved_event.group.get_avatar_for_default_event_photo()
            except: pass

            # default language and activity category
            saved_event.language_primary = this_group.language_primary
            saved_event.activity_category = this_group.activity_category

            # save.
            saved_event.save()

            # groups are sorted by when they were last updated so 
            # groups that are creating events (most active) show up first.
            this_group.updated_at = timezone.now()
            this_group.save()

            messages.success(request, _('Your event was successfully edited!'))
            return HttpResponseRedirect(reverse('eventview', kwargs={'event_id':saved_event.pk}))
        else:
            messages.error(request, _('Please correct the error below.'))
    else:

        event_initial_values = {}
        try:
            event_initial_values["time_zone"] = request.user.profile.time_zone
        except: pass        
        try:
            local_timezone = pytz.timezone(request.user.profile.time_zone)
            event_initial_values["start_time"] = timezone.now().replace(minute=0, second=0, microsecond=0).astimezone(local_timezone).strftime("%Y-%m-%d %H:%M")
        except: pass        

        
        
        event_form = EventForm(initial=event_initial_values)

    return render(request, 'yap/event/eventcreate.html', {'event_form':event_form,
                                                          'this_group':this_group})


def eventview(request, event_id=None):
    """
    view an event.
    """
    user_can_edit_event, already_rsvped = False, False
    event_post_form, all_posts, all_posts_json, all_posts_count = None, None, None, None

    try:
        event_id = int(event_id)
    except:
        messages.error(request, _('Error: Cannot find event.'))
        return HttpResponseRedirect(reverse('eventlist'))

    this_event = Event.objects.filter(pk=event_id).first()
    if this_event is None:
        messages.error(request, _('Error: Cannot find event.'))
        return HttpResponseRedirect(reverse('eventlist'))

    # make sure event has end_time, otherwise just put 1 hour later.
    if this_event.end_time == None:
        this_event.end_time = this_event.start_time + datetime.timedelta(hours=1)
        this_event.save()

    if request.user.is_authenticated:

        # RSVP for the event
        if request.method == 'POST' and "rsvp_for_event" in request.POST:
            # make sure not already listed under attendees
            if request.user.profile == this_event.admin:
                    messages.success(request, _('You are already the admin of the event.'))

            elif request.user.profile in this_event.attendee.all():
                messages.success(request, _('You are already RSVP\'ed to the event!'))

            elif timezone.now() > this_event.end_time:
                messages.error(request, _('Error: Event has already ended.  Cannot join.'))

            else:
                # make sure the attendee count is less than maximum_attendee_count.
                current_attendee_count = this_event.attendee.count() + 1 # plus 1 is to add the admin.
                if current_attendee_count < this_event.maximum_attendee_count:
                    this_event.attendee.add(request.user.profile)
                    this_event.attendee_count = current_attendee_count + 1
                    this_event.save()
                    messages.success(request, _('Successfully RSVP\'ed to the event!'))

                    try:
                        # send email to user after RSVP
                        email_successful = make_and_send_event_email(request.user.profile, this_event, "YapSpot.com -- Thanks for the RSVP -- ", DJANGO_ENV)
                    except: 
                        messages.error(request, _('Error: Could not send RSVP email.'))
                        email_successful = True

                    # if user has not confirmed email address, then give them this error message.
                    if not email_successful:
                        messages.error(request, _('Please confirm your email address in order to receive event email reminders!  Another confirmation email can be requested from your profile page.'))


        # cancel RSVP for event
        elif request.method == 'POST' and "cancel_rsvp" in request.POST:
            if not request.user.profile in this_event.attendee.all():
                messages.error(request, _('You are not RSVP\'ed to this event!'))

            elif timezone.now() > this_event.end_time:
                messages.error(request, _('Error: Event has already ended.  Cannot join.'))

            else:
                this_event.attendee.remove(request.user.profile)
                this_event.attendee_count = this_event.attendee.count() + 1 # plus 1 is to add the admin.
                this_event.save()
                messages.success(request, _('Successfully canceled RSVP!'))


        # for posting to event in discussion section.
        if request.method == 'POST' and "create_post" in request.POST:
            event_post_form = EventPostForm(request.POST)
            if event_post_form.is_valid():
                saved_event_post = event_post_form.save(commit=False)
                saved_event_post.event = this_event
                saved_event_post.poster = request.user.profile
                saved_event_post.created_at = timezone.now()
                saved_event_post.save()
                messages.success(request, _('Your post was successfully created!'))
                event_post_form = EventPostForm()
            else:
                messages.error(request, _('Please correct the error below.'))
        else:
            event_post_form = EventPostForm()


        # get all posts to display on the page
        all_posts = EventPost.objects.filter(event=this_event).order_by("-created_at")[:5]
        all_posts_count = EventPost.objects.filter(event=this_event).count()
        local_tz = get_time_zone(request)
        all_posts_json = create_post_json(all_posts, local_tz)

        # only the admin can edit the event.
        if request.user.is_authenticated and request.user.profile == this_event.admin:
            user_can_edit_event = True
        else:
            user_can_edit_event = False

        # check if user is already rsvp'ed
        if request.user.profile in this_event.attendee.all():
            already_rsvped = True
        else:
            already_rsvped = False


    # get list of all event attendees
    event_attendees = this_event.attendee.all()

    # get event avatar url
    this_event_avatar_url = this_event.get_avatar_thumbnail()

    # get event videochat URL
    this_event_videochat_url = this_event.get_video_chat_url()

    # time until start of event
    time_until_event_start = calculate_time_until_appointment(this_event.start_time, this_event.end_time)

    # can only enter event around the time of event starting.
    if (timezone.now() < (this_event.start_time - datetime.timedelta(minutes=MINUTES_PRIOR_TO_EVENT_CAN_EDIT))) and (user_can_edit_event or already_rsvped):
        can_enter_videochat_now = "early"
    elif (timezone.now() > this_event.end_time) and (user_can_edit_event or already_rsvped):
        can_enter_videochat_now = "passed"
    elif user_can_edit_event or already_rsvped:
        can_enter_videochat_now = "current"
    else:
        can_enter_videochat_now = "cant"

    # linkify event description
    linker = Linker(callbacks=[set_target_linkify])
    event_description = linker.linkify(this_event.description)

    return render(request, 'yap/event/eventview.html', {'this_event':this_event, 
                                                        'user_can_edit_event':user_can_edit_event,
                                                        'can_enter_videochat_now':can_enter_videochat_now,
                                                        'this_event_avatar_url':this_event_avatar_url,
                                                        'this_event_videochat_url':this_event_videochat_url,
                                                        'event_description':event_description,
                                                        'time_until_event_start':time_until_event_start,
                                                        'already_rsvped':already_rsvped,
                                                        'event_attendees':event_attendees,
                                                        'event_post_form':event_post_form, 
                                                        'all_posts':all_posts,
                                                        'all_posts_json':all_posts_json,
                                                        'all_posts_count':all_posts_count,
                                                        })


@login_required
@user_can_edit_event
def eventconfirmdelete(request, event_id=None):
    this_event = Event.objects.get(pk=event_id)

    if this_event.start_time < ( timezone.now()  + datetime.timedelta(minutes=MINUTES_PRIOR_TO_EVENT_CAN_EDIT) ):
        messages.error(request, _('Error: The event has already started.  You can no longer delete the event.'))
        return HttpResponseRedirect(reverse('eventview', kwargs={'event_id':this_event.pk}))

    if request.method == 'POST' and "delete_event" in request.POST:
        this_event.delete()
        messages.success(request, _('Successfully deleted the event!'))
        return HttpResponseRedirect(reverse('groupview', kwargs={"group_id":this_event.group.pk}))

    # get event avatar url
    this_event_avatar_url = this_event.get_avatar_thumbnail()

    return render(request, 'yap/event/eventconfirmdelete.html', {'this_event':this_event,
                                                                 'this_event_avatar_url':this_event_avatar_url})


@login_required
def eventposts(request, event_id=None):
    """
    Event discussion
    """

    try:
        event_id = int(event_id)
    except:
        messages.error(request, _('Error: Cannot find event.'))
        return HttpResponseRedirect(reverse('eventlist'))

    this_event = Event.objects.filter(pk=event_id).first()
    if this_event is None:
        messages.error(request, _('Error: Cannot find event.'))
        return HttpResponseRedirect(reverse('eventlist'))


    # for posting to event in discussion section.
    if request.method == 'POST' and "create_post" in request.POST:
        event_post_form = EventPostForm(request.POST)
        if event_post_form.is_valid():
            saved_event_post = event_post_form.save(commit=False)
            saved_event_post.event = this_event
            saved_event_post.poster = request.user.profile
            saved_event_post.created_at = timezone.now()
            saved_event_post.save()
            messages.success(request, _('Your post was successfully created!'))
            event_post_form = EventPostForm()
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        event_post_form = EventPostForm()

    all_posts = EventPost.objects.filter(event=this_event).order_by("-created_at")
    all_posts_count = EventPost.objects.filter(event=this_event).count()

    page = request.GET.get('page', 1)
    paginator = Paginator(all_posts, 10)
    try:
        all_posts = paginator.page(page)
    except PageNotAnInteger:
        all_posts = paginator.page(1)
    except EmptyPage:
        all_posts = paginator.page(paginator.num_pages)

    local_tz = get_time_zone(request)
    all_posts_json = create_post_json(all_posts, local_tz)

    return render(request, 'yap/event/eventposts.html', {'this_event':this_event, 
                                                         'event_post_form':event_post_form,
                                                         'all_posts':all_posts,
                                                         'all_posts_count':all_posts_count,
                                                         'all_posts_json':all_posts_json})


@login_required
@user_can_edit_event
def eventedit(request, event_id=None):
    """
    edit an event.
    """
    this_event = Event.objects.get(pk=event_id)

    if timezone.now() > this_event.end_time:
        messages.error(request, _('Error: The event has already ended.  You can no longer edit the event.'))
        return HttpResponseRedirect(reverse('eventview', kwargs={'event_id':this_event.pk}))

    if request.method == 'POST':
        event_form = EventForm(request.POST, request.FILES, instance=this_event)
        if event_form.is_valid():
            saved_event = event_form.save(commit=False)

            # adjust start_time to selected time zone
            local_timezone = pytz.timezone(saved_event.time_zone)
            saved_event.start_time = local_timezone.localize(saved_event.start_time.replace(tzinfo=None))
            saved_event.end_time = saved_event.start_time + datetime.timedelta(minutes=saved_event.duration)

            # default language and activity category
            saved_event.language_primary = saved_event.group.language_primary
            saved_event.activity_category = saved_event.group.activity_category

            saved_event.save()
            messages.success(request, _('Your event was successfully edited!'))
            return HttpResponseRedirect(reverse('eventview', kwargs={'event_id':this_event.pk}))
        else:
            messages.error(request, _('Please correct the error below.'))
    else:
        event_form = EventForm(instance=this_event)

    return render(request, 'yap/event/eventedit.html', {'event_form':event_form,
                                                        'this_event':this_event})



def eventattendeelist(request, event_id=None):
    """
    view attendees an event.
    IMPROVEMENT: add pagination
    """

    try:
        event_id = int(event_id)
    except:
        messages.error(request, _('Error: Cannot find event.'))
        return HttpResponseRedirect(reverse('eventlist'))

    this_event = Event.objects.filter(pk=event_id).first()
    if this_event is None:
        messages.error(request, _('Error: Cannot find event.'))
        return HttpResponseRedirect(reverse('eventlist'))

    event_attendees = this_event.attendee.all()
    local_tz = get_time_zone(request)
    all_profiles_json = create_profile_json(event_attendees, local_tz)

    return render(request, 'yap/event/eventattendeelist.html', {'this_event':this_event,
                                                               'all_profiles_json':all_profiles_json})



