import pyqrcode
#from .models import Profile
#from django.dispatch import receiver, Signal


#create_agent_code = Signal(providing_args=['user'])


#@receiver(create_agent_code)
def code_set(sender, **kwargs):
    data = kwargs

    qr_data = 'http://www.sent.com'
    qr_image = pyqrcode.create(qr_data, error='L', version=4, mode='binary')
    qrcode = qr_image.png('code.png', scale=6, module_color=[0, 0, 0, 128], background=[0xff, 0xff, 0xcc])

    details = Profile()
    details.user = 'agent001'
    details.qr_code = qrcode
    details.save()
    print("Saved!")


ACCESS_KEY = "6cfa73a5345f6a5868450ea5273cb0a"
xkey = 'pk.8524b836411fd8a01511867f8919f3a2'
key = 'pk.d727acbbe82adec8c038afc106470c2b'
PKEY = 'd0eb6df4539614'


#a6cfa73a5345f6a5868450ea5273cb0a #API-KEY-from-ipstack
