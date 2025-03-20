import csv
import os
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils.dateparse import parse_date
from django.db import transaction
from django.contrib.auth.hashers import make_password

User = get_user_model()

class Command(BaseCommand):
    help = 'Import users from CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file')

    def handle(self, *args, **options):
        csv_file_path = options['csv_file']
        
        if not os.path.exists(csv_file_path):
            self.stdout.write(self.style.ERROR(f"File not found: {csv_file_path}"))
            return
            
        self.stdout.write(self.style.SUCCESS(f"Importing users from {csv_file_path}"))
        
        # Track statistics
        users_created = 0
        users_skipped = 0
        errors = []
        users_to_create = []
        
        try:
            with open(csv_file_path, mode='r', encoding='utf-8-sig') as file:
                reader = csv.DictReader(file)
                
                for row in reader:
                    try:
                        # Extract data from CSV row
                        reg_no = row.get('Reg_No', '').strip()
                        name = row.get('Name', '').strip()
                        department = row.get('Department', '').strip()
                        designation = row.get('Designation', '').strip()
                        year = row.get('Year', '').strip()
                        location = row.get('Location', '').strip()
                        dob = row.get('DOB', '').strip()
                        phone_number = row.get('Phone No.', '').strip()
                        password = row.get('Password', '').strip()
                        username = row.get('Username', '').strip()
                        
                        # Skip if username is empty
                        if not username:
                            self.stdout.write(self.style.WARNING(f"Skipping row: Missing username"))
                            users_skipped += 1
                            continue
                        
                        # Check if user already exists
                        if User.objects.filter(username=username).exists():
                            self.stdout.write(self.style.WARNING(f"User {username} already exists. Skipping."))
                            users_skipped += 1
                            continue
                        
                        # Process name field - split into first and last name
                        name_parts = name.split()
                        if len(name_parts) > 0:
                            first_name = name_parts[0]
                            last_name = ' '.join(name_parts[1:]) if len(name_parts) > 1 else ''
                        else:
                            first_name = ''
                            last_name = ''
                        
                        # Generate password if not provided
                        if not password and first_name and last_name:
                            # Use firstname.initialoflastname as password
                            last_initial = last_name[0] if last_name else ''
                            password = f"{first_name.lower()}.{last_initial.lower()}" if last_initial else first_name.lower()
                        
                        # Convert year to integer if possible
                        try:
                            year_int = int(year) if year else None
                        except ValueError:
                            year_int = None
                        
                        # Convert date string to date object
                        parsed_dob = None
                        if dob:
                            try:
                                parsed_dob = parse_date(dob)
                            except ValueError:
                                self.stdout.write(self.style.WARNING(f"Invalid date format for {username}: {dob}"))
                        
                        # Create the user with hashed password
                        user = User(
                            username=username,
                            first_name=first_name,
                            last_name=last_name,
                            email='',  # Email not provided in CSV
                            reg_no=reg_no,
                            department=department,
                            designation=designation,
                            year=year_int,
                            location=location,
                            dob=parsed_dob,
                            phone_number=phone_number,
                            role='staff',  # Default role, adjust as needed
                            password=make_password(password)  # Use make_password instead of set_password
                        )
                        
                        users_to_create.append(user)
                        users_created += 1
                        
                    except Exception as e:
                        error_msg = f"Error processing row for {row.get('Username', 'unknown')}: {str(e)}"
                        self.stdout.write(self.style.ERROR(error_msg))
                        errors.append(error_msg)
                        continue
            
            # Use bulk_create to save all users at once
            with transaction.atomic():
                if users_to_create:
                    # Create users in batches of 100 to avoid memory issues with large imports
                    batch_size = 100
                    for i in range(0, len(users_to_create), batch_size):
                        batch = users_to_create[i:i+batch_size]
                        User.objects.bulk_create(batch)
                        self.stdout.write(self.style.SUCCESS(f"Created batch of {len(batch)} users"))
            
            # Print summary
            self.stdout.write(self.style.SUCCESS(f"Import completed. Users created: {users_created}, Users skipped: {users_skipped}, Errors: {len(errors)}"))
            if errors:
                self.stdout.write(self.style.WARNING("Errors encountered:"))
                for error in errors:
                    self.stdout.write(self.style.WARNING(f"- {error}"))
                    
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Failed to process CSV file: {str(e)}"))
