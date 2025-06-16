# accounts/views/webhook.py

import stripe
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST

from accounts.models import User

@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
    except ValueError:
        return HttpResponse(status=400)
    except stripe.error.SignatureVerificationError:
        return HttpResponse(status=400)

    if event['type'] == 'account.updated':
        account_data = event['data']['object']
        stripe_account_id = account_data['id']

        if account_data.get('charges_enabled') and account_data.get('payouts_enabled'):
            try:
                user = User.objects.get(stripe_account_id=stripe_account_id)
                user.is_kyc_verified = True
                user.save()
            except User.DoesNotExist:
                pass

    return HttpResponse(status=200)
