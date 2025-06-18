from rest_framework import serializers
from .models import Dispute, DisputeMessage
from orders.serializers import OrderSerializer
from orders.models import Order
from accounts.serializers import UserSerializer


class DisputeMessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = DisputeMessage
        fields = [
            "id",
            "sender",
            "content",
            "attachment",
            "created_at",
        ]
        read_only_fields = ["id", "sender", "created_at"]


class DisputeSerializer(serializers.ModelSerializer):
    initiator = UserSerializer(read_only=True)
    moderator = UserSerializer(read_only=True)
    order = OrderSerializer(read_only=True)
    order_id = serializers.PrimaryKeyRelatedField(
        queryset=Order.objects.all(),
        source="order",
        write_only=True,
    )
    messages = DisputeMessageSerializer(many=True, read_only=True)

    class Meta:
        model = Dispute
        fields = [
            "id",
            "order",
            "order_id",
            "initiator",
            "status",
            "moderator",
            "created_at",
            "updated_at",
            "messages",
        ]
        read_only_fields = [
            "id",
            "initiator",
            "status",
            "moderator",
            "created_at",
            "updated_at",
            "messages",
        ]
