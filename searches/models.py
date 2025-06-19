from django.conf import settings
from django.db import models


class SearchHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='search_histories')
    query = models.CharField(max_length=255)
    searched_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['query']),
            models.Index(fields=['searched_at']),
            models.Index(fields=['user', 'searched_at']),
        ]
        ordering = ['-searched_at']

    def __str__(self):
        return f"{self.user}: {self.query}"
