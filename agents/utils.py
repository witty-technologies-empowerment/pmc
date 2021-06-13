import pyqrcode
#from pyqrcode import QRCode
from .models import Profile as ID
from django.dispatch import receiver, Signal
import os
import secrets
from PIL import Image


create_agent_code = Signal(providing_args=['user'])
save_image = Signal(providing_args=['RCode'])

@receiver(create_agent_code)
def code_set(sender, **kwargs):
    data = kwargs
    check = ID.objects.filter(user=data['user'])
    if str(data['user']) in str(check):
        os.path.exists('default/code.png')
        print('Unique Code already exist')
        print('Clearing cache')
        print('Deleted Cache')
    else:
        acct = "This Account belongs to "+str(data['user'])
        details = acct + '  ' +secrets.token_hex(8) + ' and its secured by a 32bit Encoder'
        print('Creating unique code......')
        qr_data = str(details)
        qr_image = pyqrcode.create(qr_data, error='L', version=5, mode='binary')
        qr_image.png('media/default/code.png', scale=6, module_color='#000', background='#eee')
        #qr_image.show()
        print('Saving process begins')
        save_image.send(sender=None, RCode=data['user'])


@receiver(save_image)
def request_saved(sender, RCode, **kwargs):
    data = kwargs
    details = ID()
    details.user = RCode
    details.save()
    print('Just a sec! Placing thing in the right place!!')
    image = ID.objects.filter(user=RCode)
    for item in image:
        details = ID()
        details.pk = item.pk    
        details.user = item.user
        details.qr_code = item.qr_code
        print("Almost done")
        details.save()
        print("Done!... Unique code Saved!")
    if os.path.exists('default/code.png'):
        print('Clearing cache')
        print('Deleted Cache')


ACCESS_KEY = "6cfa73a5345f6a5868450ea5273cb0a"
xkey = 'pk.8524b836411fd8a01511867f8919f3a2'
key = 'pk.d727acbbe82adec8c038afc106470c2b'
PKEY = 'd0eb6df4539614'


#a6cfa73a5345f6a5868450ea5273cb0a #API-KEY-from-ipstack
