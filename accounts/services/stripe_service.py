import stripe

from decimal import Decimal
from django.conf import settings

stripe.api_key = settings.STRIPE_SECRET_KEY


def should_trigger_kyc(user):
    if user.is_kyc_verified:
        return False
    if user.role == 'professionnel':
        return True
    if user.role == 'particulier' and user.total_sales_amount >= Decimal('5000.00'):
        return True
    return False

def create_stripe_account(user):
    if user.stripe_account_id:
        return user.stripe_account_id

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
        refresh_url="https://xyz.ngrok.io/api/stripe/onboarding/refresh",
        return_url = "https://xyz.ngrok.io/api/stripe/onboarding/complete",
        type="account_onboarding",
    ).url
