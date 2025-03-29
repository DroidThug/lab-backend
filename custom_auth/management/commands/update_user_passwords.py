import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.contrib.auth.hashers import make_password
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Update passwords for existing users from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
            return
            
        self.stdout.write(self.style.SUCCESS(f"Updating user passwords from {csv_file_path}"))
        
        # Track statistics
        users_updated = 0
        users_not_found = 0
        errors = []
        
        try:
            with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                with transaction.atomic():
                    for row in reader:
                        try:
                            username = row.get('Username', '').strip()
                            password = row.get('Password', '').strip()
                            
                            # Skip if username is empty
                            if not username:
                                self.stdout.write(self.style.WARNING("Skipping row: Missing username"))
                                continue
                            
                            # Find the user
                            try:
                                user = User.objects.get(username=username)
                            except User.DoesNotExist:
                                self.stdout.write(self.style.WARNING(f"User {username} not found. Skipping."))
                                users_not_found += 1
                                continue
                            
                            # Generate password if not provided
                            if not password:
                                name_parts = user.get_full_name().split()
                                if name_parts:
                                    first_name = name_parts[0].lower()
                                    last_initial = name_parts[-1][0].lower() if len(name_parts) > 1 else ''
                                    password = f"{first_name}.{last_initial}" if last_initial else first_name
                                else:
                                    password = username  # Fallback to username
                            
                            # Update the password
                            user.password = make_password(password)
                            user.save(update_fields=['password'])
                            
                            users_updated += 1
                            self.stdout.write(self.style.SUCCESS(f"Updated password for user: {username}"))
                            
                        except Exception as e:
                            error_msg = f"Error updating password for {row.get('Username', 'unknown')}: {str(e)}"
                            self.stdout.write(self.style.ERROR(error_msg))
                            errors.append(error_msg)
                            continue
            
            # Print summary
            self.stdout.write(self.style.SUCCESS(f"Password update completed. Users updated: {users_updated}, "
                                               f"Users not found: {users_not_found}, Errors: {len(errors)}"))
            
            if errors:
                self.stdout.write(self.style.WARNING("Errors encountered:"))
                for error in errors:
                    self.stdout.write(self.style.WARNING(f"- {error}"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to process CSV file: {str(e)}"))
