from django.core.management.base import BaseCommand
from searches.models import SearchHistory


class Command(BaseCommand):
    help = 'Trim search history entries, keeping only the 50 most recent per user.'

    def handle(self, *args, **options):
        user_ids = SearchHistory.objects.values_list('user_id', flat=True).distinct()
        for uid in user_ids:
            histories = SearchHistory.objects.filter(user_id=uid).order_by('-searched_at')
            if histories.count() > 50:
                to_delete = histories[50:]
                count = to_delete.count()
                to_delete.delete()
                self.stdout.write(f"Deleted {count} old entries for user {uid}")
        self.stdout.write(self.style.SUCCESS('Search history cleanup completed.'))
