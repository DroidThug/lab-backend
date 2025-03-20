from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction

User = get_user_model()

class Command(BaseCommand):
    help = 'Update user roles based on their designation for existing users'

    def handle(self, *args, **options):
        # Define the mapping from designation to role
        designation_to_role = {
            'Faculty': 'staff',
            'PG': 'postgraduate',
            'Intern': 'intern',
        }
        
        # Initialize counters
        updated_count = 0
        skipped_count = 0
        
        # Get all users with non-empty designations
        users = User.objects.exclude(designation__isnull=True).exclude(designation='')
        total_users = users.count()
        
        self.stdout.write(self.style.SUCCESS(f"Found {total_users} users with designation. Processing..."))
        
        with transaction.atomic():
            for user in users:
                # Get the current designation and normalize it (strip spaces, convert to title case)
                designation = user.designation.strip()
                
                # Skip if designation is not in our mapping
                if designation not in designation_to_role:
                    self.stdout.write(self.style.WARNING(
                        f"Skipping user {user.username} - designation '{designation}' not mapped to any role"
                    ))
                    skipped_count += 1
                    continue
                
                # Get the corresponding role from the mapping
                new_role = designation_to_role[designation]
                
                # Update the user's role if it's different from the current role
                if user.role != new_role:
                    old_role = user.role
                    user.role = new_role
                    user.save(update_fields=['role'])
                    updated_count += 1
                    self.stdout.write(
                        f"Updated user {user.username}: designation '{designation}' → role changed from '{old_role}' to '{new_role}'"
                    )
                else:
                    self.stdout.write(
                        f"User {user.username}: designation '{designation}' → role already set to '{new_role}'"
                    )
                    skipped_count += 1
        
        self.stdout.write(self.style.SUCCESS(
            f"Role update completed: {updated_count} users updated, {skipped_count} users skipped. "
            f"Total processed: {total_users} users."
        ))
