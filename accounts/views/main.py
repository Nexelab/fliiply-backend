import uuid
from datetime import timedelta

from django.core.mail import send_mail
from django.utils import timezone
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from django.contrib.auth.forms import PasswordResetForm, SetPasswordForm
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_decode, urlsafe_base64_encode
from django.utils.encoding import force_str, force_bytes
from django.contrib.sites.shortcuts import get_current_site
from accounts.models import User, Address
from accounts.serializers import UserSerializer, AddressSerializer, UserRegisterSerializer
from accounts.permissions import IsOwner, IsEmailVerified
from accounts.services import create_stripe_account, generate_account_link
from accounts.services import create_setup_intent, create_subscription

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the user'),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                }
            ),
            401: "Unauthorized"
        },
        operation_description="Obtain a JWT token pair (access and refresh) by providing username and password."
    )
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return User.objects.filter(id=self.request.user.id)

    @swagger_auto_schema(
        responses={200: UserSerializer},
        operation_description="Retrieve the authenticated user's details, including phone number, billing address, and all addresses."
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "Bad Request"},
        operation_description="Update the authenticated user's details, such as phone number."
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    @swagger_auto_schema(
        responses={200: UserSerializer},
        operation_description="Retrieve the authenticated user's details via /accounts/me/."
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def become_seller(self, request):
        user = request.user

        if user.is_seller:
            return Response({'message': 'Vous êtes déjà vendeur.'}, status=status.HTTP_200_OK)

        # Met à jour les rôles
        user.is_seller = True
        user.save()

        # Crée un compte Stripe s’il n’existe pas
        if not user.stripe_account_id:
            create_stripe_account(user)

        # Génère le lien d’onboarding
        onboarding_url = generate_account_link(user)

        return Response({
            'message': 'Vous êtes maintenant vendeur.',
            'stripe_onboarding_url': onboarding_url
        }, status=status.HTTP_200_OK)

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password', 'confirm_password', 'accept_terms'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the new user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email of the new user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the new user'),
                'confirm_password': openapi.Schema(type=openapi.TYPE_STRING, description='Confirmation of the password'),
                'accept_terms': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the user accepts the terms and conditions'),
                'subscribed_to_newsletter': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the user wants to subscribe to the newsletter'),
                'role': openapi.Schema(
                    type=openapi.TYPE_STRING,
                    enum=['particulier', 'professionnel'],
                    description='Rôle de l’utilisateur (particulier ou professionnel)'
                ),
            },
        ),
        responses={
            201: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Refresh token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='Access token'),
                    'refresh_expires_in': openapi.Schema(type=openapi.TYPE_INTEGER, description='Refresh token expiry in seconds'),
                    'access_expires_in': openapi.Schema(type=openapi.TYPE_INTEGER, description='Access token expiry in seconds'),
                }
            ),
            400: "Bad Request"
        },
        operation_description="Register a new user with the specified details."
    )
    def post(self, request):
        serializer = UserRegisterSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            # Générer le token de vérification et l'expiration
            user.email_verification_token = str(uuid.uuid4())
            user.email_verification_expiry = timezone.now() + timedelta(hours=24)
            user.save()
            # Générer les tokens JWT
            refresh = RefreshToken.for_user(user)
            # Générer l'URL de vérification
            current_site = get_current_site(request)
            verification_url = (
                f"http://localhost:3000/email/confirm"
                f"?uidb64={urlsafe_base64_encode(force_bytes(user.pk))}"
                f"&token={user.email_verification_token}"
            )

            # Envoyer l'email de vérification
            send_mail(
                subject="Vérifiez votre adresse email",
                message=(
                    f"Bonjour {user.username},\n\n"
                    f"Veuillez cliquer sur le lien suivant pour vérifier votre adresse email :\n"
                    f"{verification_url}\n\n"
                    "Ce lien est valide pendant 24 heures. Si vous n'avez pas créé de compte, ignorez cet email."
                ),
                from_email="Fliiply <no-reply@fliiply.com>",
                recipient_list=[user.email],
                fail_silently=False,
            )

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'refresh_expires_in': 604800,  # 7 jours en secondes
                'access_expires_in': 300       # 5 minutes en secondes
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class ChangeRoleView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'is_buyer': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the user can buy'),
                'is_seller': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the user can sell'),
                'is_verifier': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether the user can verify'),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'is_buyer': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'is_seller': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                    'is_verifier': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                }
            ),
            403: "Forbidden",
            404: "Not Found"
        },
        operation_description="Update the roles of a user (admin only)."
    )
    def patch(self, request, user_id):
        try:
            user = User.objects.get(id=user_id)

            is_buyer = request.data.get('is_buyer', user.is_buyer)
            is_seller = request.data.get('is_seller', user.is_seller)
            is_verifier = request.data.get('is_verifier', user.is_verifier)

            user.is_buyer = is_buyer
            user.is_seller = is_seller
            user.is_verifier = is_verifier
            user.save()

            response_data = {
                'is_buyer': user.is_buyer,
                'is_seller': user.is_seller,
                'is_verifier': user.is_verifier
            }

            if user.role == User.Role.PARTICULIER and user.is_seller:
                create_stripe_account(user)
                onboarding_url = generate_account_link(user)
                response_data['onboarding_url'] = onboarding_url

            return Response(response_data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer
    permission_classes = [IsAuthenticated, IsOwner, IsEmailVerified]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()
        if self.request.user.is_authenticated:
            return Address.objects.filter(user=self.request.user)
        return Address.objects.none()

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @swagger_auto_schema(
        operation_description="List all addresses for the authenticated user.",
        responses={200: AddressSerializer(many=True), 401: "Unauthorized"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new address for the authenticated user.",
        responses={201: AddressSerializer, 400: "Bad Request", 401: "Unauthorized"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

class PasswordResetRequestView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email of the user requesting a password reset'),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message'),
                    'uidb64': openapi.Schema(type=openapi.TYPE_STRING, description='Encoded user ID'),
                    'token': openapi.Schema(type=openapi.TYPE_STRING, description='Password reset token'),
                }
            ),
            400: "Bad Request"
        },
        operation_description="Request a password reset email for the specified user email. Returns uidb64 and token."
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        # Générer manuellement uidb64 et token
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = default_token_generator.make_token(user)

        # Envoyer l'e-mail avec uidb64 et token
        form = PasswordResetForm(data={'email': email})
        if form.is_valid():
            form.save(
                domain_override=get_current_site(request).domain,
                subject_template_name='registration/password_reset_email_subject.txt',
                email_template_name='registration/password_reset_email.txt',
                from_email='Fliiply <no-reply@fliiply.com>',
                request=request,
                extra_email_context={'uidb64': uidb64, 'token': token}
            )
            return Response({
                'message': 'Password reset email sent',
                'uidb64': uidb64,
                'token': token
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid email'}, status=status.HTTP_400_BAD_REQUEST)

class PasswordResetConfirmView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['uidb64', 'token', 'new_password'],
            properties={
                'uidb64': openapi.Schema(type=openapi.TYPE_STRING, description='Encoded user ID from reset email'),
                'token': openapi.Schema(type=openapi.TYPE_STRING, description='Token from reset email'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password to set'),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            ),
            400: "Bad Request",
            403: "Invalid token"
        },
        operation_description="Confirm password reset using uidb64 and token, and set a new password."
    )
    def post(self, request):
        uidb64 = request.data.get('uidb64')
        token = request.data.get('token')
        new_password = request.data.get('new_password')

        if not all([uidb64, token, new_password]):
            return Response({'error': 'uidb64, token, and new_password are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and default_token_generator.check_token(user, token):
            form = SetPasswordForm(user, {'new_password1': new_password, 'new_password2': new_password})
            if form.is_valid():
                form.save()
                return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)
            return Response(form.errors, status=status.HTTP_400_BAD_REQUEST)
        return Response({'error': 'Invalid token or user'}, status=status.HTTP_403_FORBIDDEN)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'uidb64',
                openapi.IN_QUERY,
                description="Encoded user ID",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'token',
                openapi.IN_QUERY,
                description="Verification token",
                type=openapi.TYPE_STRING,
                required=True
            ),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            ),
            400: "Bad Request",
            403: "Invalid or expired token"
        },
        operation_description="Verify a user's email using the provided uidb64 and token."
    )
    def get(self, request):
        uidb64 = request.GET.get('uidb64')
        token = request.GET.get('token')

        if not all([uidb64, token]):
            return Response({'error': 'uidb64 and token are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            user = None

        if user is not None and user.email_verification_token == token:
            if user.is_verification_token_valid():
                user.is_email_verified = True
                user.email_verification_token = None
                user.email_verification_expiry = None
                user.save()
                return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
            else:
                return Response({'error': 'Verification token has expired'}, status=status.HTTP_403_FORBIDDEN)
        return Response({'error': 'Invalid token or user'}, status=status.HTTP_403_FORBIDDEN)

class ResendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            ),
            400: "Bad Request",
            403: "Email already verified"
        },
        operation_description="Resend a verification email to the authenticated user if their email is not yet verified."
    )
    def post(self, request):
        user = request.user

        if user.is_email_verified:
            return Response({'error': 'Email is already verified'}, status=status.HTTP_403_FORBIDDEN)

        # Générer un nouveau token et une nouvelle date d'expiration
        user.email_verification_token = str(uuid.uuid4())
        user.email_verification_expiry = timezone.now() + timedelta(hours=24)
        user.save()

        # Générer l'URL de vérification
        uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
        token = user.email_verification_token
        frontend_url = "http://localhost:3000/email/confirm"
        verification_url = f"{frontend_url}?uidb64={uidb64}&token={token}"

        # Envoyer l'email de vérification
        send_mail(
            subject="Vérifiez votre adresse email",
            message=(
                f"Bonjour {user.username},\n\n"
                f"Veuillez cliquer sur le lien suivant pour vérifier votre adresse email :\n"
                f"{verification_url}\n\n"
                "Ce lien est valide pendant 24 heures. Si vous n'avez pas créé de compte, ignorez cet email."
            ),
            from_email="Fliiply <no-reply@fliiply.com>",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({'message': 'Verification email resent successfully'}, status=status.HTTP_200_OK)

class VerifyKYCView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID de l'utilisateur à marquer comme vérifié KYC",
                required=True
            )
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'is_kyc_verified': openapi.Schema(type=openapi.TYPE_BOOLEAN),
                }
            ),
            404: "User Not Found",
            403: "Forbidden"
        },
        operation_description="Marquer un utilisateur comme ayant complété le KYC (admin seulement)."
    )
    def post(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            user.is_kyc_verified = True
            user.save()
            return Response({
                "message": f"Utilisateur {user.username} marqué comme vérifié KYC.",
                "is_kyc_verified": user.is_kyc_verified
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "Utilisateur non trouvé."}, status=status.HTTP_404_NOT_FOUND)


class StripeSetupIntentView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'client_secret': openapi.Schema(type=openapi.TYPE_STRING)},
        )},
        operation_description="Génère un SetupIntent Stripe pour enregistrer une carte."
    )
    def post(self, request):
        client_secret = create_setup_intent(request.user)
        return Response({'client_secret': client_secret})


class StripeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['price_id'],
            properties={'price_id': openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'subscription_id': openapi.Schema(type=openapi.TYPE_STRING)})},
        operation_description="Crée un abonnement Stripe pour les fonctionnalités premium."
    )
    def post(self, request):
        price_id = request.data.get('price_id')
        if not price_id:
            return Response({'error': 'price_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        subscription_id = create_subscription(request.user, price_id)
        return Response({'subscription_id': subscription_id})
