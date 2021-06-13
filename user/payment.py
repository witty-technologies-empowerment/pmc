# Set your secret key: remember to change this to your live secret key in production
# See your keys here: https://dashboard.stripe.com/account/apikeys
pub_key = pk_test_N7TUIbhLOjPPhB5sYkckQz4C00lLFq4Lzm
stripe.api_key = 'sk_test_ZXujBdDDHhEBvGLAek5eJvc300JoWqrPVY'

session = stripe.checkout.Session.create(
  payment_method_types=['card'],
  line_items=[{
    'name': 'T-shirt',
    'description': 'Comfortable cotton t-shirt',
    'images': ['https://example.com/t-shirt.png'],
    'amount': 500,
    'currency': 'usd',
    'quantity': 1,
  }],
  success_url='https://example.com/success?session_id={CHECKOUT_SESSION_ID}',
  cancel_url='https://example.com/cancel',
)
