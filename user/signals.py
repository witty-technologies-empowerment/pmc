from django.dispatch import Signal

user_current_location = Signal(providing_args=['request'])

