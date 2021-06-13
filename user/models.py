from django.db import models
from django.conf import settings


from .signals import user_current_location
from .utils import get_client_city_data, get_client_ip


class UserSessionManager(models.Manager):
    def create_new(self, user, session_key=None, ip_address=None):
        session_new = self.model()
        session_new.user = user
        session_new.session_key = session_key
        if ip_address is not None:
            session_new.ip_address = ip_address
            city_data = get_client_city_data(ip_address)
            session_new.city_data = city_data
            try:
                city = city_data['city']
            except:
                city = None
            session_new.city = city
            try:
                country = city_data['country_name']
            except:
                country = None
            session_new.country = country
            session_new.save()
            return session_new
        return None


class UserSession(models.Model):
    user = models.CharField(max_length=20)
    latitude = models.CharField(max_length=15)
    longitude = models.CharField(max_length=15)
    #user = models.ForeignKey(settings.AUTH_USER_MODEL)
    session_key = models.CharField(max_length=60, null=True, blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    city_data = models.TextField(null=True, blank=True)
    city = models.CharField(max_length=120, null=True, blank=True)
    country = models.CharField(max_length=120, null=True, blank=True)
    active = models.BooleanField(default=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    objects = UserSessionManager()

    def __str__(self):
        city = self.city
        country = self.country
        if city and country:
            return f"{city}, {country}"
        elif city and not country:
            return f"{city}"
        elif country and not city:
            return f"{country}"
        return self.user.username


def user_current_location_receiver(sender, request, *args, **kwargs):
    user = sender
    # ip_address
    city_data = None
    # ip_address = get_client_ip(request)
    ip_address = get_client_ip(request)
    session_key = request.session.session_key
    UserSession.objects.create_new(
        user=user,
        session_key=session_key,
        ip_address=ip_address
    )
    print("Got it")


class GetInTouch(models.Model):
    name = models.CharField(max_length=20)
    email = models.CharField(max_length=50)
    message = models.CharField(max_length=250)
    sent = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-sent']

    def __str__(self):
        return "New message from " + self.name + " ."


class isNewUser(models.Model):
    user = models.CharField(max_length=20)
    is_new = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.is_new:
            return self.user + " is new"
        else:
            return self.user + " not is new"


class userSocial(models.Model):
    user = models.CharField(max_length=20)
    facebook =  models.CharField(max_length=50)
    twitter =  models.CharField(max_length=50)
    google =  models.CharField(max_length=50)
    about =  models.CharField(max_length=150)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.user + " Social Account"
    







user_current_location.connect(user_current_location_receiver)