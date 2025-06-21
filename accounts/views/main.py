import uuid
from datetime import timedelta
from random import randint

from django.core.mail import send_mail
from django.utils import timezone
from django.contrib.auth import password_validation
from django.core.exceptions import ValidationError
from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from accounts.models import User, Address, ProfessionalInfo
from accounts.serializers import (
    UserSerializer,
    AddressSerializer,
    UserRegisterSerializer,
    UserProfessionalRegisterSerializer,
    ProfessionalInfoSerializer,
)
from accounts.permissions import IsOwner, IsEmailVerified
from accounts.services import create_stripe_account, generate_account_link
from accounts.services import create_setup_intent, create_subscription

class CustomTokenObtainPairView(TokenObtainPairView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Authenticate user and obtain JWT tokens",
        operation_summary="User Login",
        tags=['Authentication'],
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
                    'refresh_expires_in': openapi.Schema(type=openapi.TYPE_INTEGER, description='Refresh token expiry in seconds'),
                    'access_expires_in': openapi.Schema(type=openapi.TYPE_INTEGER, description='Access token expiry in seconds'),
                }
            ),
            401: "Unauthorized"
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Add expiry information to the response
            response.data['refresh_expires_in'] = 604800  # 7 days in seconds
            response.data['access_expires_in'] = 300      # 5 minutes in seconds
        return response


class CustomTokenRefreshView(TokenRefreshView):
    """Custom JWT token refresh view with proper Swagger documentation."""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        operation_description="Refresh JWT access token using refresh token",
        operation_summary="Refresh Token",
        tags=['Authentication'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['refresh'],
            properties={
                'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='Valid refresh token'),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'refresh': openapi.Schema(type=openapi.TYPE_STRING, description='New refresh token'),
                    'access': openapi.Schema(type=openapi.TYPE_STRING, description='New access token'),
                    'refresh_expires_in': openapi.Schema(type=openapi.TYPE_INTEGER, description='Refresh token expiry in seconds'),
                    'access_expires_in': openapi.Schema(type=openapi.TYPE_INTEGER, description='Access token expiry in seconds'),
                }
            ),
            401: "Invalid or expired refresh token"
        }
    )
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            # Get the refresh token from request
            refresh_token = request.data.get('refresh')
            if refresh_token:
                try:
                    # Create new refresh token
                    from rest_framework_simplejwt.tokens import RefreshToken
                    token = RefreshToken(refresh_token)
                    user = token.payload.get('user_id')
                    if user:
                        # Create fresh tokens
                        new_refresh = RefreshToken.for_user(User.objects.get(id=user))
                        response.data['refresh'] = str(new_refresh)
                        response.data['access'] = str(new_refresh.access_token)
                        response.data['refresh_expires_in'] = 604800  # 7 days
                        response.data['access_expires_in'] = 300      # 5 minutes
                except Exception:
                    # Fallback to original response with just access token
                    response.data['refresh_expires_in'] = 604800
                    response.data['access_expires_in'] = 300
        return response


class UserViewSet(viewsets.ModelViewSet):
    """
    User profile management.
    
    Allows authenticated users to view and update their own profile information.
    Users can only access their own data for privacy and security.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated, IsOwner]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return User.objects.none()
        return User.objects.filter(id=self.request.user.id)

    @swagger_auto_schema(
        operation_description="Retrieve the authenticated user's profile details",
        operation_summary="Get User Profile",
        tags=['User Management'],
        responses={200: UserSerializer}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update the authenticated user's profile information",
        operation_summary="Update User Profile",
        tags=['User Management'],
        request_body=UserSerializer,
        responses={200: UserSerializer, 400: "Bad Request"}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    @swagger_auto_schema(
        operation_description="Get current user's profile information",
        operation_summary="Get My Profile",
        tags=['User Management'],
        responses={200: UserSerializer}
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    @swagger_auto_schema(
        operation_description="Enable seller capabilities for the current user and create Stripe account",
        operation_summary="Become Seller",
        tags=['Seller Onboarding'],
        responses={
            200: openapi.Response(description="User is now a seller"),
            400: openapi.Response(description="Error in seller setup")
        }
    )
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
            required=['username', 'first_name', 'last_name', 'email', 'password', 'confirm_password', 'accept_terms'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the new user'),
                'first_name': openapi.Schema(type=openapi.TYPE_STRING, description='First name of the new user'),
                'last_name': openapi.Schema(type=openapi.TYPE_STRING, description='Last name of the new user'),
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
        operation_description="Register a new user account",
        operation_summary="User Registration",
        tags=['Authentication']
    )
    def post(self, request):
        role = request.data.get('role', User.Role.PARTICULIER)
        serializer_class = (
            UserProfessionalRegisterSerializer
            if role == User.Role.PROFESSIONNEL
            else UserRegisterSerializer
        )
        serializer = serializer_class(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            otp = f"{randint(100000, 999999)}"
            user.email_otp = otp
            user.email_otp_expiry = timezone.now() + timedelta(minutes=10)
            user.save()
            refresh = RefreshToken.for_user(user)

            send_mail(
                subject="Code de vérification de votre email",
                message=(
                    f"Bonjour {user.username},\n\n"
                    f"Votre code de vérification est : {otp}.\n"
                    "Il expire dans 10 minutes."
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
        operation_description="Update user roles and permissions (Admin only)",
        operation_summary="Change User Roles",
        tags=['User Management']
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
        operation_description="List all addresses for the authenticated user",
        operation_summary="List My Addresses",
        tags=['User Management'],
        responses={200: AddressSerializer(many=True), 401: "Unauthorized"}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new address for the authenticated user",
        operation_summary="Add Address",
        tags=['User Management'],
        responses={201: AddressSerializer, 400: "Bad Request", 401: "Unauthorized"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)


class ProfessionalInfoViewSet(viewsets.ModelViewSet):
    """
    Professional information management for business users.
    
    Allows professional users to manage their business information
    including company details, tax information, and business address.
    """
    queryset = ProfessionalInfo.objects.all()
    serializer_class = ProfessionalInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if getattr(self, 'swagger_fake_view', False):
            return ProfessionalInfo.objects.none()
        return ProfessionalInfo.objects.filter(user=self.request.user)

    @swagger_auto_schema(
        operation_description="List professional information for the authenticated user",
        operation_summary="List Professional Info",
        tags=['User Management'],
        responses={200: ProfessionalInfoSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create professional information for the authenticated user",
        operation_summary="Create Professional Info",
        tags=['User Management'],
        responses={201: ProfessionalInfoSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve professional information details",
        operation_summary="Get Professional Info",
        tags=['User Management'],
        responses={200: ProfessionalInfoSerializer, 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update professional information",
        operation_summary="Update Professional Info",
        tags=['User Management'],
        responses={200: ProfessionalInfoSerializer, 400: "Bad Request"}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Partially update professional information",
        operation_summary="Update Professional Info Partially",
        tags=['User Management'],
        responses={200: ProfessionalInfoSerializer, 400: "Bad Request"}
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete professional information",
        operation_summary="Delete Professional Info",
        tags=['User Management'],
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

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
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            ),
            400: "Bad Request"
        },
        operation_description="Request password reset code via email",
        operation_summary="Request Password Reset",
        tags=['Authentication']
    )
    def post(self, request):
        email = request.data.get('email')
        if not email:
            return Response({'error': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User with this email does not exist'}, status=status.HTTP_400_BAD_REQUEST)

        otp = f"{randint(100000, 999999)}"
        user.password_reset_otp = otp
        user.password_reset_otp_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        send_mail(
            subject="Code de réinitialisation de mot de passe",
            message=(
                f"Bonjour {user.username},\n\n"
                f"Votre code de réinitialisation est : {otp}.\n"
                "Il expire dans 10 minutes."
            ),
            from_email='Fliiply <no-reply@fliiply.com>',
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({'message': 'Password reset code sent'}, status=status.HTTP_200_OK)

class PasswordResetVerifyView(APIView):
    """Step 1: Verify OTP and get reset token"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'otp': openapi.Schema(type=openapi.TYPE_STRING, description='6-digit OTP code'),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING),
                    'reset_token': openapi.Schema(type=openapi.TYPE_STRING, description='Temporary reset token for password change')
                }
            ),
            400: "Bad Request",
            403: "Invalid OTP"
        },
        operation_description="Verify OTP and receive reset token for password change",
        operation_summary="Verify Password Reset OTP",
        tags=['Authentication']
    )
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')

        if not all([email, otp]):
            return Response({'error': 'email and otp are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_password_reset_otp_valid(otp):
            # Generate a temporary reset token (valid for 10 minutes)
            reset_token = f"{randint(100000000, 999999999)}"
            user.password_reset_token = reset_token
            user.password_reset_token_expiry = timezone.now() + timedelta(minutes=10)
            user.save()
            
            return Response({
                'message': 'OTP verified successfully. You can now set your new password.',
                'reset_token': reset_token
            }, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_403_FORBIDDEN)


class PasswordResetConfirmView(APIView):
    """Step 2: Set new password using reset token"""
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['reset_token', 'new_password', 'password_confirm'],
            properties={
                'reset_token': openapi.Schema(type=openapi.TYPE_STRING, description='Reset token from OTP verification'),
                'new_password': openapi.Schema(type=openapi.TYPE_STRING, description='New password to set'),
                'password_confirm': openapi.Schema(type=openapi.TYPE_STRING, description='Confirm new password'),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            ),
            400: "Bad Request",
            403: "Invalid or expired reset token"
        },
        operation_description="Set new password using reset token from OTP verification",
        operation_summary="Confirm Password Reset",
        tags=['Authentication']
    )
    def post(self, request):
        reset_token = request.data.get('reset_token')
        new_password = request.data.get('new_password')
        password_confirm = request.data.get('password_confirm')

        if not all([reset_token, new_password, password_confirm]):
            return Response({'error': 'reset_token, new_password, and password_confirm are required'}, status=status.HTTP_400_BAD_REQUEST)

        if new_password != password_confirm:
            return Response({'error': 'Password confirmation does not match'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(
                password_reset_token=reset_token,
                password_reset_token_expiry__gt=timezone.now()
            )
        except User.DoesNotExist:
            return Response({'error': 'Invalid or expired reset token'}, status=status.HTTP_403_FORBIDDEN)

        # Validate password strength
        try:
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            return Response({'error': e.messages}, status=status.HTTP_400_BAD_REQUEST)

        # Set new password and clear reset tokens
        user.set_password(new_password)
        user.password_reset_otp = None
        user.password_reset_otp_expiry = None
        user.password_reset_token = None
        user.password_reset_token_expiry = None
        user.save()
        
        return Response({'message': 'Password reset successfully'}, status=status.HTTP_200_OK)

class VerifyEmailView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email', 'otp'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL),
                'otp': openapi.Schema(type=openapi.TYPE_STRING),
            },
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={'message': openapi.Schema(type=openapi.TYPE_STRING)}
            ),
            400: "Bad Request",
            403: "Invalid or expired OTP",
        },
        operation_description="Verify email address using OTP code",
        operation_summary="Verify Email",
        tags=['Authentication']
    )
    def post(self, request):
        email = request.data.get('email')
        otp = request.data.get('otp')
        if not email or not otp:
            return Response({'error': 'email and otp are required'}, status=status.HTTP_400_BAD_REQUEST)

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'User not found'}, status=status.HTTP_400_BAD_REQUEST)

        if user.is_email_otp_valid(otp):
            user.is_email_verified = True
            user.email_otp = None
            user.email_otp_expiry = None
            user.save()
            return Response({'message': 'Email verified successfully'}, status=status.HTTP_200_OK)
        return Response({'error': 'Invalid or expired OTP'}, status=status.HTTP_403_FORBIDDEN)

class ResendVerificationEmailView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Resend verification email to the authenticated user",
        operation_summary="Resend Verification Email",
        tags=['Authentication'],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'message': openapi.Schema(type=openapi.TYPE_STRING, description='Success message')
                }
            ),
            400: "Bad Request",
            403: "Email already verified"
        }
    )
    def post(self, request):
        user = request.user

        if user.is_email_verified:
            return Response({'error': 'Email is already verified'}, status=status.HTTP_403_FORBIDDEN)

        otp = f"{randint(100000, 999999)}"
        user.email_otp = otp
        user.email_otp_expiry = timezone.now() + timedelta(minutes=10)
        user.save()

        send_mail(
            subject="Code de vérification de votre email",
            message=(
                f"Bonjour {user.username},\n\n"
                f"Votre nouveau code de vérification est : {otp}.\n"
                "Il expire dans 10 minutes."
            ),
            from_email="Fliiply <no-reply@fliiply.com>",
            recipient_list=[user.email],
            fail_silently=False,
        )

        return Response({'message': 'Verification email resent successfully'}, status=status.HTTP_200_OK)

class VerifyKYCView(APIView):
    permission_classes = [IsAdminUser]

    @swagger_auto_schema(
        operation_description="Mark a user as KYC verified (admin only)",
        operation_summary="Verify User KYC",
        tags=['User Management'],
        manual_parameters=[
            openapi.Parameter(
                'user_id',
                openapi.IN_PATH,
                type=openapi.TYPE_INTEGER,
                description="ID of the user to mark as KYC verified",
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
        }
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
        operation_description="Create Stripe SetupIntent for saving payment methods",
        operation_summary="Create Payment Setup Intent",
        tags=['Payment & Billing'],
        responses={200: openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'client_secret': openapi.Schema(type=openapi.TYPE_STRING)},
        )}
    )
    def post(self, request):
        client_secret = create_setup_intent(request.user)
        return Response({'client_secret': client_secret})


class StripeSubscriptionView(APIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        operation_description="Create a Stripe subscription for premium features",
        operation_summary="Create Subscription",
        tags=['Payment & Billing'],
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['price_id'],
            properties={'price_id': openapi.Schema(type=openapi.TYPE_STRING)},
        ),
        responses={200: openapi.Schema(type=openapi.TYPE_OBJECT, properties={'subscription_id': openapi.Schema(type=openapi.TYPE_STRING)})}
    )
    def post(self, request):
        price_id = request.data.get('price_id')
        if not price_id:
            return Response({'error': 'price_id is required'}, status=status.HTTP_400_BAD_REQUEST)
        subscription_id = create_subscription(request.user, price_id)
        return Response({'subscription_id': subscription_id})

