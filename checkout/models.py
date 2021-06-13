from django.db import models

# Create your models here.

class Checkout(models.Model):
    user = models.CharField(max_length=20)
    agent = models.CharField(max_length=20)
    rcode = models.CharField(max_length=100)
    patternkey = models.CharField(max_length=100)
    failed = models.BooleanField(default=False)
    pending = models.BooleanField(default=True)
    approved = models.BooleanField(default=False)
    created = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created']

    def __str__(self):
    	if self.pending == True:
    		return 'Transaction '+str(self.rcode)+' is pending'
    	if self.approved:
    		return 'Transaction '+str(self.rcode)+' is approved'
    	elif self.failed:
    		return 'Transaction '+str(self.rcode)+' is failed'
    	else:
    		return 'Transaction '+str(self.rcode)+' undefined'