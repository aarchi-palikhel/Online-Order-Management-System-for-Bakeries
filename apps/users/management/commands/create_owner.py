from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Create an initial Owner/Superuser with interactive prompts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Username for the owner',
        )
        parser.add_argument(
            '--email',
            help='Email for the owner',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Do not prompt for input',
        )
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        # Check if any owner exists
        if User.objects.filter(user_type='owner').exists():
            self.stdout.write(self.style.WARNING('Owner/Superuser already exists'))
            return
        
        username = options.get('username')
        email = options.get('email')
        noinput = options.get('noinput')
        
        if not username and not noinput:
            username = input('Username: ')
        
        if not email and not noinput:
            email = input('Email: ')
        
        # Create owner/superuser
        try:
            owner = User.objects.create_superuser(
                username=username or 'owner',
                email=email or 'owner@livebakery.com',
                password='owner123',  # Default password, should be changed
                user_type='owner'
            )
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created Owner/Superuser: {owner.username}'
            ))
            self.stdout.write(self.style.WARNING(
                f'Default password: owner123 - Please change it immediately!'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating owner: {e}'))