# accounts/views/webhook.py

import stripe
import json
import logging
from django.conf import settings
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from accounts.models import User
from rest_framework import status

logger = logging.getLogger(__name__)

@require_POST
@csrf_exempt
def stripe_webhook(request):
    payload = request.body
    sig_header = request.META.get("HTTP_STRIPE_SIGNATURE")
    endpoint_secret = settings.STRIPE_WEBHOOK_SECRET

    logger.info("📥 Webhook reçu de Stripe")
    logger.debug("🔎 Payload brut : %s", request.body.decode())

    try:
        event = stripe.Webhook.construct_event(
            payload=payload,
            sig_header=sig_header,
            secret=endpoint_secret
        )
        logger.info(f"✅ [WEBHOOK] Received Stripe event: {event['type']}")
    except stripe.error.SignatureVerificationError as e:
        logger.error(f"❌ [WEBHOOK] Signature Stripe invalide : {str(e)}")
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(f"❌ [WEBHOOK] Erreur inattendue webhook Stripe : {str(e)}")
        return HttpResponse(status=status.HTTP_400_BAD_REQUEST)

    if event['type'] == 'account.updated':
        account_data = event['data']['object']
        stripe_account_id = account_data['id']
        logger.info(f"[WEBHOOK] account.updated for: {stripe_account_id}")
        logger.debug(json.dumps(account_data, indent=2))

        try:
            user = User.objects.get(stripe_account_id=stripe_account_id)
        except User.DoesNotExist:
            logger.warning(f"[WEBHOOK] No user found with stripe_account_id: {stripe_account_id}")
            return HttpResponse(status=404)

        # ✅ KYC verification
        if account_data.get('charges_enabled') and account_data.get('payouts_enabled'):
            user.is_kyc_verified = True

        # ✅ Update stripe_account_status intelligemment
        if account_data.get('charges_enabled') and account_data.get('details_submitted'):
            user.stripe_account_status = "verified"
        elif not account_data.get('details_submitted'):
            user.stripe_account_status = "incomplete"
        elif not account_data.get('charges_enabled'):
            user.stripe_account_status = "restricted"
        else:
            user.stripe_account_status = "pending"

        user.save()
        logger.info(f"[WEBHOOK] ✅ User {user.username} updated with status '{user.stripe_account_status}'")

    return HttpResponse(status=200)
