from django.db.models import Q
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from .models import Dispute, DisputeMessage
from .serializers import DisputeSerializer, DisputeMessageSerializer


class DisputeViewSet(viewsets.ModelViewSet):
    """
    Dispute management for order issues.
    
    Allows users to create and manage disputes for order problems.
    Buyers can create disputes, moderators can resolve them.
    """
    queryset = Dispute.objects.all()
    serializer_class = DisputeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Return an empty queryset when generating Swagger docs or when the
        # request user isn't authenticated to avoid errors during schema
        # generation.
        if getattr(self, "swagger_fake_view", False) or not self.request.user.is_authenticated:
            return Dispute.objects.none()

        user = self.request.user
        return Dispute.objects.filter(
            Q(initiator=user) | Q(order__buyer=user) | Q(moderator=user)
        ).distinct()

    @swagger_auto_schema(
        operation_description="List all disputes accessible to the current user",
        operation_summary="List Disputes",
        tags=['Disputes'],
        responses={200: DisputeSerializer(many=True)}
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Create a new dispute for an order (buyers only)",
        operation_summary="Create Dispute",
        tags=['Disputes'],
        responses={201: DisputeSerializer, 400: "Bad Request"}
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Retrieve details of a specific dispute",
        operation_summary="Get Dispute",
        tags=['Disputes'],
        responses={200: DisputeSerializer, 404: "Not Found"}
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Update a dispute",
        operation_summary="Update Dispute",
        tags=['Disputes'],
        responses={200: DisputeSerializer, 400: "Bad Request"}
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_description="Delete a dispute",
        operation_summary="Delete Dispute",
        tags=['Disputes'],
        responses={204: "No Content"}
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        if order.buyer != self.request.user:
            raise serializers.ValidationError("You cannot open a dispute on this order.")
        serializer.save(initiator=self.request.user)

    @swagger_auto_schema(
        operation_description="Add a message to a dispute conversation",
        operation_summary="Add Dispute Message",
        tags=['Disputes'],
        request_body=DisputeMessageSerializer,
        responses={201: DisputeMessageSerializer, 400: "Bad Request", 403: "Forbidden"}
    )
    @action(detail=True, methods=["post"], url_path="add_message")
    def add_message(self, request, pk=None):
        dispute = self.get_object()
        if request.user not in [dispute.initiator, dispute.moderator]:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = DisputeMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(dispute=dispute, sender=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @swagger_auto_schema(
        operation_description="Mark a dispute as resolved",
        operation_summary="Resolve Dispute",
        tags=['Disputes'],
        responses={200: DisputeSerializer, 403: "Forbidden"}
    )
    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        dispute = self.get_object()
        if request.user not in [dispute.initiator, dispute.moderator]:
            return Response(status=status.HTTP_403_FORBIDDEN)
        dispute.status = "resolved"
        dispute.save()
        return Response(self.get_serializer(dispute).data)
