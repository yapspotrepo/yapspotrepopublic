from django.db import models
from django.contrib.auth.models import User
from .utils import COUNTRY_CHOICES, LANGUAGE_CHOICES, TIMEZONE_CHOICES, GENDER_CHOICES, ACTIVITY_CATEGORIES, bleach_before_database
from phonenumber_field.modelfields import PhoneNumberField
from phonenumber_field.phonenumber import PhoneNumber, to_python
from django.dispatch import receiver
from django.db.models.signals import post_save
from .validators import validate_file_extension, validate_image_file_extension
from storage_backends import PrivateMediaStorage
from imagekit.models import ImageSpecField, ProcessedImageField
from imagekit.processors import ResizeToFill, Transpose
import os
import uuid
from django.templatetags.static import static
import bleach
import secrets 
from .utils import ASCII_NUMERIC


def update_filename_profile_avatar(instance, filename):
    """ Make custom name for uploaded profile photos. """
    path = "profile_avatar/"
    file_extension = os.path.splitext(filename)[1]
    randomuuid = str(uuid.uuid4())
    new_file_name = "profile_avatar_" + str(instance.user.pk) + "_" + randomuuid + file_extension
    return os.path.join(path, new_file_name)


class Language(models.Model):
    """
    Model for languages
    """
    two_letter_code = models.CharField(blank=True, default="", max_length=5)
    name = models.CharField(blank=True, default="", max_length=50)

    def __str__(self):
        return self.name


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ PROFILE ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


class Profile(models.Model):
    """
    Model for user profiles.
    """
    user = models.OneToOneField(User, primary_key=True, on_delete=models.CASCADE)
    name = models.CharField(blank=True, default="", max_length=50)

    time_zone = models.CharField(default="", max_length=100, choices=TIMEZONE_CHOICES)
    language_preferred = models.ForeignKey(Language, blank=True, null=True, primary_key=False, on_delete=models.SET_NULL)

    city = models.CharField(blank=True, default="", max_length=50)
    region = models.CharField(blank=True, default="", verbose_name="Region / Province / State", max_length=50)
    country = models.CharField(blank=True, default="", max_length=5, choices=COUNTRY_CHOICES)
    interests = models.TextField(blank=True, default="", max_length=1000)
    about_me = models.TextField(blank=True, default="", max_length=1000)

    accept_email = models.BooleanField(default=True, verbose_name="Accept Email Notifications")
    accept_sms = models.BooleanField(default=True, verbose_name="Accept SMS Notifications")

    avatar = ProcessedImageField(storage=PrivateMediaStorage(), processors=[Transpose()], upload_to=update_filename_profile_avatar, blank=True, validators=[validate_image_file_extension])
    avatar_thumbnail = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(250, 250)], format='JPEG', options={'quality': 60})
    avatar_thumbnail_mini = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(100, 100)], format='JPEG', options={'quality': 60})
    avatar_thumbnail_micro = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(30, 30)], format='JPEG', options={'quality': 60})

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        prof_string = ""
        if self.name != "":
            prof_string = self.name

        if prof_string != "":
        	return prof_string
        else:
            return self.user.username

    def get_avatar_thumbnail(self):
        if bool(self.avatar_thumbnail):
            return self.avatar_thumbnail.url
        else:
            return static("yap/defaultpics/defaultpic250.jpg")

    def get_avatar_thumbnail_mini(self):
        if bool(self.avatar_thumbnail_mini):
            return self.avatar_thumbnail_mini.url
        else:
            return static("yap/defaultpics/defaultpicmini.jpg")

    def get_avatar_thumbnail_micro(self):
        if bool(self.avatar_thumbnail_micro):
            return self.avatar_thumbnail_micro.url
        else:
            return static("yap/defaultpics/defaultpicmicro.jpg")

    def save(self, *args, **kwargs):
        self.name = bleach_before_database(self.name)
        self.city = bleach_before_database(self.city)
        self.region = bleach_before_database(self.region)
        self.country = bleach_before_database(self.country)
        self.interests = bleach_before_database(self.interests)
        self.about_me = bleach_before_database(self.about_me)
        super(Profile, self).save(*args, **kwargs)

    @receiver(post_save, sender=User)
    def create_user_profile(sender, instance, created, **kwargs):
        if created:
            user_profile = Profile.objects.create(user=instance)

    @receiver(post_save, sender=User)
    def save_user_profile(sender, instance, **kwargs):
        instance.profile.save()


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ GROUP ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def update_filename_group_avatar(instance, filename):
    """ Make custom name for uploaded group photos. """
    path = "group_avatar/"
    file_extension = os.path.splitext(filename)[1]
    randomuuid = str(uuid.uuid4())
    new_file_name = "group_avatar_" + str(instance.pk) + "_" + randomuuid + file_extension
    return os.path.join(path, new_file_name)


class Group(models.Model):
    """
    Model for groups.
    """
    name = models.CharField(blank=True, default="", max_length=100)
    description = models.TextField(blank=True, default="", max_length=3000)
    language_primary = models.ForeignKey(Language, blank=True, null=True, primary_key=False, verbose_name="Primary Language", on_delete=models.SET_NULL)
    activity_category = models.CharField(default="", blank=True, max_length=10, choices=ACTIVITY_CATEGORIES)
    admin = models.ForeignKey(Profile, blank=True, null=True, primary_key=False, on_delete=models.CASCADE)
    member = models.ManyToManyField(Profile, related_name="members", blank=True, through="GroupMembership")
    member_count = models.IntegerField(blank=True, default=1)
    private_group = models.BooleanField(default=False)

    avatar = ProcessedImageField(storage=PrivateMediaStorage(), processors=[Transpose()], upload_to=update_filename_group_avatar, blank=True, validators=[validate_image_file_extension])
    avatar_thumbnail = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(250, 250)], format='JPEG', options={'quality': 60})
    avatar_thumbnail_mini = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(100, 100)], format='JPEG', options={'quality': 60})
    avatar_thumbnail_micro = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(30, 30)], format='JPEG', options={'quality': 60})

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def get_avatar_for_default_event_photo(self):
        if bool(self.avatar):
            return self.avatar
        else:
            return static("yap/defaultpics/group.svg")

    def get_avatar_thumbnail(self):
        if bool(self.avatar_thumbnail):
            return self.avatar_thumbnail.url
        else:
            return static("yap/defaultpics/group.svg")

    def get_avatar_thumbnail_mini(self):
        if bool(self.avatar_thumbnail_mini):
            return self.avatar_thumbnail_mini.url
        else:
            return static("yap/defaultpics/group.png")

    def get_language_name(self):
        if self.language_primary is not None:
            return self.language_primary.__str__()
        else:
            return "No Language Selected"

    def get_group_description(self):
        this_description = bleach.clean(self.description, tags=[], strip=True)
        if len(this_description) < 100:
            return this_description
        else:
            return this_description[:100] + "..."

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.name = bleach_before_database(self.name)
        self.description = bleach_before_database(self.description)
        super(Group, self).save(*args, **kwargs)


class GroupMembership(models.Model):
    """
    Through table between group and profile.
    """
    group = models.ForeignKey(Group, primary_key=False, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, primary_key=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ EVENT ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


def update_filename_event_avatar(instance, filename):
    """ 
    Make custom name for uploaded event photos. 
    """
    path = "event_avatar/"
    file_extension = os.path.splitext(filename)[1]
    randomuuid = str(uuid.uuid4())
    new_file_name = "event_avatar_" + str(instance.pk) + "_" + randomuuid + file_extension
    return os.path.join(path, new_file_name)


class Event(models.Model):
    """
    Model for events.
    """
    name = models.CharField(blank=True, default="", max_length=100, verbose_name="Event Name")
    description = models.TextField(blank=True, default="", max_length=3000)
    language_primary = models.ForeignKey(Language, blank=True, null=True, primary_key=False, verbose_name="Primary Language", on_delete=models.SET_NULL)
    activity_category = models.CharField(default="", max_length=10, choices=ACTIVITY_CATEGORIES)
    start_time = models.DateTimeField(null=True)
    end_time = models.DateTimeField(null=True)
    time_zone = models.CharField(default="", max_length=100, choices=TIMEZONE_CHOICES)
    group = models.ForeignKey(Group, blank=True, null=True, primary_key=False, on_delete=models.CASCADE)
    admin = models.ForeignKey(Profile, blank=True, null=True, primary_key=False, on_delete=models.CASCADE)
    attendee = models.ManyToManyField(Profile, related_name="attendees", blank=True, through="EventAttendance")
    attendee_count = models.IntegerField(blank=True, default=1) # 1 because we don't let the admin leave!!!
    maximum_attendee_count = models.IntegerField(blank=True, default=10)
    duration = models.IntegerField(default=60, verbose_name="Duration (minutes)") # event duration
    event_videochat_room_base_name = models.CharField(default="", max_length=50)
    use_jitsi = models.BooleanField()
    event_url = models.URLField(max_length=200, default="", blank=True, verbose_name="Event URL")
    reminder_email_sent_pre_event = models.BooleanField(default=False)

    #split_attendees_into_multiple_rooms = models.BooleanField(default=False)
    #attendees_per_room = models.IntegerField(blank=True, default=8)

    avatar = ProcessedImageField(storage=PrivateMediaStorage(), processors=[Transpose()], upload_to=update_filename_event_avatar, blank=True, validators=[validate_image_file_extension], verbose_name="Event Avatar")
    avatar_thumbnail = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(250, 250)], format='JPEG', options={'quality': 60})
    avatar_thumbnail_mini = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(100, 100)], format='JPEG', options={'quality': 60})
    avatar_thumbnail_micro = ImageSpecField(source='avatar', processors=[Transpose(),ResizeToFill(30, 30)], format='JPEG', options={'quality': 60})

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


    def create_jitsi_event_videochat_room_name(self):
        """
        For use on jitsi.
        Just capitalize the first letters of the name and remove the spaces.  Max 20 characters.
        Then add a 10 digit number
        """
        random_number_name = ''.join(secrets.choice(ASCII_NUMERIC) for i in range(10)) 
        return "YapSpot" + random_number_name


    def get_video_chat_url(self):
        """
        Get video chat URL.
        """
        if self.use_jitsi:
            if self.event_videochat_room_base_name != "":
                return "https://meet.jit.si/" + self.event_videochat_room_base_name

            else:
                self.event_url = self.create_jitsi_event_videochat_room_name()
                self.save()
                return "https://meet.jit.si/" + self.event_url

        elif self.event_url != "":
            return self.event_url

        else:
            return None


    def determine_if_reminder_email_sent_pre_event(self, this_profile):
        this_event_attendance = EventAttendance.objects.filter(profile=this_profile, event=self).first()
        if this_event_attendance:
            print("\n\n return " + str(this_event_attendance.reminder_email_sent_pre_event))
            return this_event_attendance.reminder_email_sent_pre_event
        else:
            print("\n\n return False")
            return False

    def set_reminder_email_sent_pre_event(self, this_profile):
        this_event_attendance = EventAttendance.objects.filter(profile=this_profile, event=self).first()
        if this_event_attendance:
            this_event_attendance.reminder_email_sent_pre_event = True
            this_event_attendance.save()
        else:
            return False

    def get_avatar_thumbnail(self):
        if bool(self.avatar_thumbnail):
            return self.avatar_thumbnail.url
        else:
            return static("yap/defaultpics/event.png")


    def get_avatar_thumbnail_mini(self):
        if bool(self.avatar_thumbnail_mini):
            return self.avatar_thumbnail_mini.url
        else:
            return static("yap/defaultpics/event.png")


    def get_language_name(self):
        if self.language_primary is not None:
            return self.language_primary.__str__()
        else:
            return "No Language Selected"


    def get_event_description(self):
        this_description = bleach.clean(self.description, tags=[], strip=True)
        if len(this_description) < 100:
            return this_description
        else:
            return this_description[:100] + "..."


    def get_attendees_per_room(self):
        if self.split_attendees_into_multiple_rooms:
            return str(self.attendees_per_room)
        else:
            return "All attendees in one room"


    def __str__(self):
       return self.name


    def save(self, *args, **kwargs):
        self.name = bleach_before_database(self.name)
        self.description = bleach_before_database(self.description)
        super(Event, self).save(*args, **kwargs)


class EventAttendance(models.Model):
    """
    Through table between event and profile.
    """
    event = models.ForeignKey(Event, primary_key=False, on_delete=models.CASCADE)
    profile = models.ForeignKey(Profile, primary_key=False, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    reminder_email_sent_pre_event = models.BooleanField(default=False)

    def __str__(self):
        return self.event.event_videochat_room_base_name + "group" + self.event_videochat_room_name + " -- " + self.profile.user.email


""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ POSTS ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """
""" ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~ """


class GroupPost(models.Model):
    """
    Model for groups.
    """
    group = models.ForeignKey(Group, blank=True, primary_key=False, on_delete=models.CASCADE)
    poster = models.ForeignKey(Profile, blank=True, primary_key=False, on_delete=models.CASCADE)
    post_text = models.TextField(blank=True, default="", verbose_name="", max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.poster + " : " + self.post_text

    def save(self, *args, **kwargs):
        self.post_text = bleach_before_database(self.post_text)
        super(GroupPost, self).save(*args, **kwargs)


class EventPost(models.Model):
    """
    Model for groups.
    """
    event = models.ForeignKey(Event, blank=True, primary_key=False, on_delete=models.CASCADE)
    poster = models.ForeignKey(Profile, blank=True, primary_key=False, on_delete=models.CASCADE)
    post_text = models.TextField(blank=True, default="", verbose_name="", max_length=1000)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.poster + " : " + self.post_text

    def save(self, *args, **kwargs):
        self.post_text = bleach_before_database(self.post_text)
        super(EventPost, self).save(*args, **kwargs)





