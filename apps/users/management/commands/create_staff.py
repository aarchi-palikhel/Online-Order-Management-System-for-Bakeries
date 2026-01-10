from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.core.management import call_command

class Command(BaseCommand):
    help = 'Create a Staff user with interactive prompts'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            help='Username for the staff',
        )
        parser.add_argument(
            '--email',
            help='Email for the staff',
        )
        parser.add_argument(
            '--password',
            help='Password for the staff (if not provided, will generate random)',
        )
        parser.add_argument(
            '--noinput',
            action='store_true',
            help='Do not prompt for input',
        )
    
    def handle(self, *args, **options):
        User = get_user_model()
        
        username = options.get('username')
        email = options.get('email')
        password = options.get('password')
        noinput = options.get('noinput')
        
        # Interactive prompts if not provided
        if not username and not noinput:
            username = input('Username for staff: ').strip()
        
        if not email and not noinput:
            email = input('Email for staff: ').strip()
        
        if not password and not noinput:
            password = input('Password for staff (leave empty to generate): ').strip()
            if not password:
                password = None
        
        # Validate inputs
        if not username:
            self.stdout.write(self.style.ERROR('Username is required'))
            return
        
        if not email:
            self.stdout.write(self.style.ERROR('Email is required'))
            return
        
        # Check if user already exists
        if User.objects.filter(username=username).exists():
            self.stdout.write(self.style.ERROR(f'User with username "{username}" already exists'))
            return
        
        if User.objects.filter(email=email).exists():
            self.stdout.write(self.style.ERROR(f'User with email "{email}" already exists'))
            return
        
        # Generate random password if not provided
        if not password:
            import secrets
            import string
            alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
            password = ''.join(secrets.choice(alphabet) for i in range(12))
        
        # Create staff user
        try:
            staff = User.objects.create_user(
                username=username,
                email=email,
                password=password,
                user_type='staff'
            )
            
            # Ensure staff has correct permissions
            staff.is_staff = True
            staff.is_active = True
            staff.save()
            
            self.stdout.write(self.style.SUCCESS(
                f'Successfully created Staff user: {staff.username}'
            ))
            self.stdout.write(self.style.SUCCESS(
                f'Email: {staff.email}'
            ))
            self.stdout.write(self.style.WARNING(
                f'Password: {password}'
            ))
            self.stdout.write(self.style.NOTICE(
                'Please change the password on first login!'
            ))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'Error creating staff: {e}'))