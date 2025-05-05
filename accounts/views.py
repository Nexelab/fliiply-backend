from rest_framework import viewsets, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from .models import User, Address
from .serializers import UserSerializer, AddressSerializer

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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
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

class RegisterView(APIView):
    permission_classes = [AllowAny]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['username', 'email', 'password'],
            properties={
                'username': openapi.Schema(type=openapi.TYPE_STRING, description='Username of the new user'),
                'email': openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_EMAIL, description='Email of the new user'),
                'password': openapi.Schema(type=openapi.TYPE_STRING, description='Password of the new user'),
                'phone_number': openapi.Schema(type=openapi.TYPE_STRING, description='Phone number of the new user (optional)'),
            },
        ),
        responses={
            201: UserSerializer,
            400: "Bad Request"
        },
        operation_description="Register a new user with the specified username, email, password, and optional phone number."
    )
    def post(self, request):
        serializer = UserSerializer(data=request.data)
        if serializer.is_valid():
            user = User.objects.create_user(
                username=serializer.validated_data['username'],
                email=serializer.validated_data['email'],
                password=serializer.validated_data['password'],
                phone_number=serializer.validated_data.get('phone_number'),
                is_buyer=True,
                is_seller=True,
                is_verifier=False
            )
            return Response(UserSerializer(user).data, status=status.HTTP_201_CREATED)
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
            return Response({
                'is_buyer': user.is_buyer,
                'is_seller': user.is_seller,
                'is_verifier': user.is_verifier
            }, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({"error": "User not found"}, status=status.HTTP_404_NOT_FOUND)

class AddressViewSet(viewsets.ModelViewSet):
    queryset = Address.objects.all()
    serializer_class = AddressSerializer

    def get_queryset(self):
        # Vérifie si la requête est pour la génération Swagger
        if getattr(self, 'swagger_fake_view', False):
            return Address.objects.none()  # Retourne un queryset vide pour Swagger
        # Filtre les adresses par utilisateur authentifié
        if self.request.user.is_authenticated:
            return Address.objects.filter(user=self.request.user)
        return Address.objects.none()  # Retourne vide pour les utilisateurs non authentifiés

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsAuthenticated]
        return [permission() for permission in permission_classes]

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