import stripe
from decimal import Decimal
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_stripe_account(user):
    """
    Crée un compte Stripe Express si non existant et le rattache à l'utilisateur.
    """
    if user.stripe_account_id:
        return user.stripe_account_id

    print(user.role)

    account = stripe.Account.create(
        type="express",
        country="FR",
        email=user.email,
        capabilities={
            "transfers": {"requested": True},
            "card_payments": {"requested": True},
        },
        business_type="company" if user.role == "professionnel" else "individual",
    )
    user.stripe_account_id = account.id
    user.save()
    return account.id

def generate_account_link(user):
    account_id = create_stripe_account(user)

    return stripe.AccountLink.create(
        account=account_id,
        refresh_url=settings.STRIPE_ONBOARDING_REFRESH_URL,
        return_url=settings.STRIPE_ONBOARDING_RETURN_URL,
        type="account_onboarding",
    ).url


def create_stripe_customer(user):
    """Create a Stripe customer for the given user if needed."""
    if user.stripe_customer_id:
        return user.stripe_customer_id
    customer = stripe.Customer.create(email=user.email)
    user.stripe_customer_id = customer.id
    user.save()
    return customer.id


def create_setup_intent(user):
    """Return a SetupIntent client secret for saving a payment method."""
    customer_id = create_stripe_customer(user)
    intent = stripe.SetupIntent.create(customer=customer_id)
    return intent.client_secret


def create_subscription(user, price_id):
    """Create a Stripe subscription for the user to the given price."""
    customer_id = create_stripe_customer(user)
    subscription = stripe.Subscription.create(customer=customer_id, items=[{"price": price_id}])
    user.stripe_subscription_id = subscription.id
    user.save()
    return subscription.id


def create_payment_intent(user, amount, currency="eur"):
    """Create a payment intent for an order."""
    customer_id = create_stripe_customer(user)
    intent = stripe.PaymentIntent.create(customer=customer_id, amount=int(amount * 100), currency=currency)
    return intent
