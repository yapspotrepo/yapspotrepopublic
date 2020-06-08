from django.core.management.base import BaseCommand
import datetime
from django.utils import timezone
from yap.models import Event, Profile
from django.db.models import Q
import requests
from django.core.cache import cache
from random import randint
from time import sleep
from yapspot.settings import DJANGO_ENV
from yap.utils import make_and_send_event_email


class Command(BaseCommand):
    help = 'Send email of event URL 15 min prior.'

    def handle(self, *args, **kwargs):
        print("Crontab -- Send email of event URL 15 min prior")

        ### get ec2 ID number from AWS using this cURL
        if DJANGO_ENV == "PROD":
            this_ec2_id = str(requests.get('http://169.254.169.254/latest/meta-data/instance-id').text)
        else:
            this_ec2_id = "1234567890"
        designated_ec2 = cache.get("designated_ec2_url_emails", None)
        print("Crontab -- Send email of event URL 15 min prior -- This ec2: " + this_ec2_id)


        ### if there is no designated_ec2 then one needs to be set
        # the sleep is to avoid race conditions for autoscaling ec2's.  However the nx=True (set only if None) really probably makes that unecessary.
        if designated_ec2 == None:

            if DJANGO_ENV == "PROD":
                sleep_interval = randint(1,500)/100
                sleep(sleep_interval)
                cache.set("designated_ec2_url_emails", this_ec2_id, timeout=1200, nx=True)
            else:
                cache.set("designated_ec2_url_emails", this_ec2_id, timeout=1200)


        ### check again for the designated ec2. if it is not this ec2 then stop running
        designated_ec2 = cache.get("designated_ec2_url_emails", None)
        print("Crontab -- Send email of event URL 15 min prior -- EC2 designated for this task: " + designated_ec2)
        if this_ec2_id != designated_ec2:
            print("Crontab -- Send email of event URL 15 min prior -- PASS!!! " + this_ec2_id)
            return


        ### if this is th designated ec2, then go through and delete the crap from the waiting room that hasn't short polled in a long time.
        else:
            print("Crontab -- Send email of event URL 15 min prior -- DESIGNATED!!! " + this_ec2_id)
            minutes_in_future_5 = timezone.now() + datetime.timedelta(minutes=5)
            minutes_in_future_25 = timezone.now() + datetime.timedelta(minutes=25)
            minutes_in_future_44 = timezone.now() + datetime.timedelta(minutes=44)
            events_for_emailing_admin = Event.objects.filter(start_time__gte=minutes_in_future_25, start_time__lt=minutes_in_future_44)
            soon_to_start_events = Event.objects.filter(start_time__gte=minutes_in_future_5, start_time__lt=minutes_in_future_25)


            # send the emails to admins with 30 minutes notice.
            for this_event in events_for_emailing_admin:
                # make and send event email to event host
                make_and_send_event_email(this_event.admin, this_event, "YapSpot.com - Your event begins soon -- ", DJANGO_ENV, True)
                sleep(0.3)


            # Go through each event and send email to users.
            for this_event in soon_to_start_events:

                # send emails to attendees
                for attendee in this_event.attendee.all():
                    #make and send email to attendees.  sleep is to not send them to fast as there is a limit with AWS SES.
                    make_and_send_event_email(attendee, this_event, "YapSpot.com event begins soon -- ", DJANGO_ENV)
                    sleep(0.3)




