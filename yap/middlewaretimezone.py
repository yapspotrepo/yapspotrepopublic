from django.utils import timezone
import pytz
from django.utils.deprecation import MiddlewareMixin
from yap.views import get_time_zone

class TimezoneMiddleware(MiddlewareMixin):
    def process_request(self, request):
        #try:
        if request.user.is_authenticated:
            timezone.activate(pytz.timezone(request.user.profile.time_zone))
        else:
            local_tz = get_time_zone(request)
            timezone.activate(local_tz)

        #except:
        #    timezone.deactivate()