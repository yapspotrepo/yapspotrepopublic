from django import forms
from django.forms import ModelForm
import datetime
from .utils import COUNTRY_CHOICES, LANGUAGE_CHOICES, TIMEZONE_CHOICES, GENDER_CHOICES, BANNED_WORDS
from django.forms import ModelForm
from .models import Language, Profile, Event, Group, GroupPost, EventPost
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.core.exceptions import ValidationError
import pytz
from allauth.account.forms import SignupForm
import bleach
from captcha.fields import ReCaptchaField
import re


class DateInput(forms.DateInput):
    input_type = 'date'


class DateTimeInput(forms.DateTimeInput):
    input_type = 'datetimelocal'


class CustomSignupForm(SignupForm):
    """ Teacher signup form """
    name = forms.CharField(max_length=50, required=True, strip=True, widget=forms.TextInput(attrs={'placeholder':'Your name'}))
    captcha = ReCaptchaField()
    field_order = ['name', 'email', 'password1', 'password2', 'captcha']

    def save(self, request):
        user = super(CustomSignupForm, self).save(request)
        name = self.cleaned_data.get('name').strip().title()
        user.profile.name = name
        user.profile.save()
        user.save()
        return user


class ProfileForm(ModelForm):
    """
    Model form for profiles.
    """
    class Meta:
        model = Profile
        fields = ['name', 'time_zone', 'language_preferred', 'city', 'region', 'country', 'interests', 'about_me', 'accept_email', 'accept_sms']


class ProfileAvatarForm(ModelForm):
    """
    Model form for profiles.
    """
    class Meta:
        model = Profile
        fields = ['avatar',]


class ContactForm(forms.Form):
    """ Contact form for website. """
    name = forms.CharField(max_length=30)
    email = forms.EmailField(max_length=254)
    message = forms.CharField(
        max_length = 2000,
        widget = forms.Textarea(),
        help_text = 'Write here your message!'
    )
    captcha = ReCaptchaField()

    def clean_name(self):
        return re.sub("[^0-9A-Za-z@\.\s\-]", "", self.cleaned_data['name'].strip())

    def clean_email(self):
        return re.sub("[^0-9A-Za-z@\.\s\-]", "", self.cleaned_data['email'].strip())

    def clean_message(self):
        return re.sub("[^0-9A-Za-z@\.\s\-]", "", self.cleaned_data['message'].strip())


class GroupForm(ModelForm):
    """
    Model form for Group.
    """
    class Meta:
        model = Group
        fields = ['avatar', 'name', 'description', 'activity_category', 'language_primary']

    def clean_activity_category(self):
        activity_category = self.cleaned_data["activity_category"]
        if activity_category == "":
            raise ValidationError('Error:  Please select a category for the activity.')
        return activity_category


class GroupPostForm(ModelForm):
    """
    Model form for GroupPost.
    """
    class Meta:
        model = GroupPost
        fields = ['post_text',]
        widgets = {
          'post_text': forms.Textarea(attrs={'rows':1, 'placeholder':'Type comment here.'}),
        }

    def clean_post_text(self):
        post_text = self.cleaned_data["post_text"]
        if post_text == "":
            raise ValidationError('Error:  Post cannot be blank.')
        return post_text


class GroupFilterForm(ModelForm):
    """
    Model form for group search.
    """
    class Meta:
        model = Group
        fields = ['activity_category', 'language_primary']


class GroupSearchForm(forms.Form):
    """
    For searching for group by a search term.
    """
    search_term = forms.CharField(max_length=30, required=False, strip=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter search term'}))


class EventForm(ModelForm):
    """
    Model form for events.
    """
    class Meta:
        model = Event
        fields = ['avatar', 
                  'name', 
                  'description', 
                  'start_time', 
                  'duration', 
                  'time_zone', 
                  'maximum_attendee_count',
                  'use_jitsi',
                  'event_url'
                  ]

        widgets = {
            'start_time': DateTimeInput(attrs={'placeholder': 'YYYY-MM-DD HH:mm  (Clock is 24 hours "military time")', 'format': 'Y-m-d H:i'}),
            'event_url': forms.TextInput(attrs={'placeholder': 'https://'}),
        }

        help_texts = {
            "avatar": "<strong>Note:</strong> If no image file is selected, the default avatar for the event is the group's avatar.",
            "start_time": "<strong>Note:</strong> Date/Time format is 'YYYY-MM-DD HH:mm'. Clock is 24 hours \"military time\" - for example, 6:00pm would be 18:00.",
            "duration": "<strong>Note:</strong> Length of the event in minutes (e.g. 60).",
            "event_url": "<strong>Note:</strong> Add a link so people know where to go when your event starts.   If you don't have the URL ahead of time, then leave this field blank and return to the event page 15 minutes before the start of the event and you will be able to mass email a message to the attendees",
        }
    field_order = ['name', 'avatar', 'use_jitsi', 'event_url', 'description', 'maximum_attendee_count', 'start_time', 'time_zone', 'duration']
    use_jitsi = forms.TypedChoiceField(label="Select videochat platform",
                                       coerce=lambda x: x =='True', 
                                       choices=((True, 'Use Jitsi Meet (free)'), (False, 'Use other videochat platform (e.g. Zoom, Google Meet, Skype, etc.)')), 
                                       widget=forms.RadioSelect(), 
                                       )


    def clean_start_time(self):
        start_time = self.cleaned_data["start_time"]
        if start_time < timezone.now():
            raise ValidationError('Error:  Cannot create event with startime in the past.')
        return start_time


    def clean_maximum_attendee_count(self):
        maximum_attendee_count = self.cleaned_data["maximum_attendee_count"]
        if maximum_attendee_count < 2:
            raise ValidationError('Error:  Maximum attendee count must be at least 2.')
        return maximum_attendee_count

 
    def clean_duration(self):
        duration = self.cleaned_data["duration"]

        if duration < 5:
            raise ValidationError('Error:  Event must be at least 5 minutes.')

        elif duration > 1440:
            raise ValidationError('Error:  Event may not be greater than 24 hours (1440 minutes).')

        return duration



class EventPostForm(ModelForm):
    """
    Model form for EventPost.
    """
    class Meta:
        model = EventPost
        fields = ['post_text',]
        widgets = {
          'post_text': forms.Textarea(attrs={'rows':1, 'placeholder':'Type comment here.'}),
        }

    def clean_post_text(self):
        post_text = self.cleaned_data["post_text"]
        if post_text == "":
            raise ValidationError('Error:  Post cannot be blank.')
        return post_text


class EventFilterForm(ModelForm):
    """
    Model form for event search.
    """
    class Meta:
        model = Group
        fields = ['activity_category', 'language_primary']


class EventSearchForm(forms.Form):
    """
    For searching for an event by a search term.
    """
    search_term = forms.CharField(max_length=30, required=False, strip=True, label="", widget=forms.TextInput(attrs={'placeholder': 'Enter search term'}))







