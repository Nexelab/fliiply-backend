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
