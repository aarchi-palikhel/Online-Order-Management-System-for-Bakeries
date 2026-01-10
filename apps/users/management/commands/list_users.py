from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'List all users with details'
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        users = User.objects.all().order_by('date_joined')
        
        self.stdout.write(self.style.SUCCESS(f'Total users: {users.count()}'))
        
        for user in users:
            self.stdout.write(f"""
{'-'*50}
Username: {user.username}
Email: {user.email}
User Type: {user.user_type}
Is Superuser: {user.is_superuser}
Is Staff: {user.is_staff}
Is Active: {user.is_active}
Last Login: {user.last_login}
Date Joined: {user.date_joined}
            """.strip())