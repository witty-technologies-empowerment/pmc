from django.db import models

# Create your models here.
class History(models.Model):
    user = models.CharField(max_length=20)
    trans_id = models.CharField(max_length=250)
    amount = models.CharField(max_length=250)
    agent = models.CharField(max_length=250)
    status = models.BooleanField(default=False)
    time = models.CharField(max_length=250)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.status:
            return 'Transaction history with ID ' +self.trans_id + " was successful."
        else:
            return 'Transaction history with ID ' +self.trans_id + " was not successful."


class Activity(models.Model):
    user = models.CharField(max_length=20)
    details = models.CharField(max_length=1500)
    opened = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.opened:
            return 'Alert for ' +self.user + " (READ)"
        else:
            return 'New alert for ' +self.user + " (UNREAD)"

    
class design(models.Model):
    user = models.CharField(max_length=20)
    background = models.BooleanField(default=False)
    color = models.CharField(max_length=50)
    img = models.CharField(max_length=20)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        if self.background:
            return self.user + " - Background setting is (background-image = ON - color = "+self.color+" - image = "+self.img+")."
        else:
            return self.user + " - Background setting is (background-image = OFF - color = "+self.color+" - image = "+self.img+")."