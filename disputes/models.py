from django.db import models
from django.conf import settings


class Dispute(models.Model):
    STATUS_CHOICES = [
        ("open", "Open"),
        ("resolved", "Resolved"),
        ("closed", "Closed"),
    ]

    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE, related_name="disputes")
    initiator = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="initiated_disputes")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="open")
    moderator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="moderated_disputes",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['order']),
            models.Index(fields=['initiator']),
            models.Index(fields=['status']),
            models.Index(fields=['moderator']),
            models.Index(fields=['created_at']),
            models.Index(fields=['status', 'created_at']),
            models.Index(fields=['moderator', 'status']),
        ]

    def __str__(self):
        return f"Dispute {self.id} on order {self.order_id}"


class DisputeMessage(models.Model):
    dispute = models.ForeignKey(Dispute, on_delete=models.CASCADE, related_name="messages")
    sender = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="dispute_messages")
    content = models.TextField(blank=True)
    attachment = models.FileField(upload_to="dispute_attachments/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['dispute']),
            models.Index(fields=['sender']),
            models.Index(fields=['created_at']),
            models.Index(fields=['dispute', 'created_at']),
        ]

    def __str__(self):
        return f"Message by {self.sender} in dispute {self.dispute_id}"
