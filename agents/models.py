from django.db import models

# Create your models here.


class IsAgent(models.Model):
    user = models.CharField(max_length=20)
    is_agent = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.user + " is an Agent."

    def date_join_v1(self):
        return self.created.strftime('%B, %Y.')

    def session(self):
        return self.created.strftime('%a %d, %B %Y.')


class Profile(models.Model):
    user = models.CharField(max_length=20)
    qr_code = models.ImageField(upload_to='profile/qrcode', default='default/codes.jpg')

    def __str__(self):
        return 'QRCode for '+self.user


class ProfilePic(models.Model):
    user = models.CharField(max_length=20)
    picture = models.ImageField(upload_to='profile/picture')

    def __str__(self):
        return 'Profile Picture for '+self.user

    #class Meta:
      #db_table = "profile" 


class Address(models.Model):
    user       = models.CharField(max_length=20)
    street     = models.CharField(max_length=50)
    city       = models.CharField(max_length=50)
    state      = models.CharField(max_length=20)
    country    = models.CharField(max_length=8, default='Nigeria')
    ip_address = models.CharField(max_length=20)
    latitude   = models.CharField(max_length=25)
    longitude  = models.CharField(max_length=25)
    added      = models.DateTimeField(auto_now_add=True)
    updated    = models.DateTimeField(auto_now=True)
    verified   = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.user + " at " + self.street + ", " + self.city + ", " + self.state


class fund(models.Model):
    user       = models.CharField(max_length=20)
    can_remite = models.PositiveIntegerField()
    balance    = models.PositiveIntegerField()
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.user + ' can only give '+str(self.can_remite)+' but has '+str(self.balance)+' as balance.'


class RequestDetail(models.Model):
    user      = models.CharField(max_length=20)
    customer  = models.CharField(max_length=20)
    amount  = models.CharField(max_length=20)
    rcode     = models.CharField(max_length=100)
    rtime     = models.CharField(max_length=20, blank=True)
    rdate     = models.CharField(max_length=20, blank=True)
    n         = models.CharField(max_length=20, default=1)
    send      = models.BooleanField(default=False)
    url       = models.URLField(max_length=500, blank=True)
    update    = models.BooleanField(default=False)
    has_accepted = models.BooleanField(default=False)
    has_declined = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.n <= str(1) and self.has_accepted == True and self.update == True:
            return self.user + ' has Accepted this request with ID ' + self.rcode + ' and ' + self.customer + ' has been redirected'
        elif self.n > str(1) and self.has_accepted == True and self.update == True:
            return self.user + ' has Accepted this request with ID ' + self.rcode + ' and ' + self.customer + ' has been redirected'
        elif self.n <= str(1) and self.has_accepted == True:
            return self.user + ' has Accepted this request with ID '+self.rcode
        elif self.n > str(1) and self.has_accepted == True:
            return self.user + ' has Accepted this request with ID ' + self.rcode
        elif self.n <= str(1) and self.has_declined == True:
            return self.user + ' has Declined this request with ID '+self.rcode
        elif self.n > str(1) and self.has_declined == True:
            return self.user + ' has Declined this request with ID '+self.rcode
        elif self.n > str(1) and self.has_accepted == False:
            return self.user + ' did NOT Accepted this request, and the request has Expired - ID ' + self.rcode
        elif self.send:
            return self.user+' has NOT Accepted the request with ID '+self.rcode
        else:
            return self.customer+' Created request for '+self.rcode


class SentFunc(models.Model):
    rcode    = models.CharField(max_length=100)
    sent_sms = models.BooleanField(default=False)
    check    = models.BooleanField(default=False)
    created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.sent_sms and self.check:
            return 'Sms sent '+self.rcode
        elif self.check:
            return 'Sms pending '+self.rcode
        else:
            return 'Sms port created with ID '+self.rcode


class visited(models.Model):
    rcode    = models.CharField(max_length=100)
    visit    = models.CharField(max_length=2, default=0)
    created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.visit != str(0):
            return 'visited '+self.rcode+" page "+self.visit+" time(s)."
        else:
            return 'not visited '+self.rcode+" page "


class RCode(models.Model):
    rcode    = models.CharField(max_length=100)
    used     = models.BooleanField(default=False)
    created  = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.used:
            return self.rcode+" has been used."
        else:
            return self.rcode+" hasn't been used."


class rating(models.Model):
    user  = models.CharField(max_length=20)
    accept = models.CharField(max_length=20)
    declined = models.CharField(max_length=20)
    expired = models.CharField(max_length=20)
    total = models.CharField(max_length=20)
    average_rating = models.CharField(max_length=20)
    average_accept = models.CharField(max_length=20)
    average_declined = models.CharField(max_length=20)
    average_expired = models.CharField(max_length=20)
    updated = models.DateTimeField(auto_now=True)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.user+"'s Average Rating is "+self.average_rating+'%'


class ProfileAvatar(models.Model):
    title = models.CharField(max_length=29)
    image = models.ImageField(upload_to='media/default/')
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

class IsVerified(models.Model):
    user  = models.CharField(max_length=20)
    otp = models.CharField(max_length=6)
    telephone = models.CharField(max_length=13)
    verified = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.verified:
            return self.user+" is verified"
        else:
            return self.user+" is not verified"


class InAcct(models.Model):
    user  = models.CharField(max_length=20)
    rcode = models.CharField(max_length=100)
    pattern = models.CharField(max_length=100)
    balance = models.CharField(max_length=15)
    xtrafund = models.CharField(max_length=15)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.user+" has "+self.balance+" in account"


class Veri(models.Model):
    user = models.CharField(max_length=20)
    rcode = models.CharField(max_length=100)
    count = models.CharField(max_length=2, default=1)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.count == str(1):
            return self.rcode + ' - ' + self.count
        else:
            return self.rcode + ' - ' + self.count
