from django.db.models import Q
from rest_framework import viewsets, status, serializers
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Dispute, DisputeMessage
from .serializers import DisputeSerializer, DisputeMessageSerializer


class DisputeViewSet(viewsets.ModelViewSet):
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

    def perform_create(self, serializer):
        order = serializer.validated_data["order"]
        if order.buyer != self.request.user:
            raise serializers.ValidationError("You cannot open a dispute on this order.")
        serializer.save(initiator=self.request.user)

    @action(detail=True, methods=["post"])
    def add_message(self, request, pk=None):
        dispute = self.get_object()
        if request.user not in [dispute.initiator, dispute.moderator]:
            return Response(status=status.HTTP_403_FORBIDDEN)
        serializer = DisputeMessageSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(dispute=dispute, sender=request.user)
            return Response(serializer.data, status=201)
        return Response(serializer.errors, status=400)

    @action(detail=True, methods=["post"])
    def resolve(self, request, pk=None):
        dispute = self.get_object()
        if request.user not in [dispute.initiator, dispute.moderator]:
            return Response(status=status.HTTP_403_FORBIDDEN)
        dispute.status = "resolved"
        dispute.save()
        return Response(self.get_serializer(dispute).data)
