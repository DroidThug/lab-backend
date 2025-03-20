import csv
from django.core.management.base import BaseCommand
from django.db import connection
from apps.orders.models import LabTest

class Command(BaseCommand):
    help = 'Import LabTests from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='The path to the CSV file to be imported')

    def handle(self, *args, **kwargs):
        csv_file = kwargs['csv_file']
        with open(csv_file, newline='') as file:
            reader = csv.DictReader(file)
            required_columns = {'id', 'name', 'privilege', 'vac_col', 'comp', 'section'}
            if not required_columns.issubset(reader.fieldnames):
                missing_columns = required_columns - set(reader.fieldnames)
                self.stderr.write(self.style.ERROR(f'Missing columns in CSV file: {missing_columns}'))
                return
            for row in reader:
                lab_test, created = LabTest.objects.update_or_create(
                    id=row['id'],
                    defaults={
                        'name': row['name'],
                        'privilege': row['privilege'],
                        'vac_col': row['vac_col'],
                        'section': row['section']
                    }
                )

            file.seek(0)
            next(reader)  # Skip the header row

            for row in reader:
                if row['comp']:
                    try:
                        comp_test = LabTest.objects.get(id=row['comp'])
                        lab_test = LabTest.objects.get(id=row['id'])
                        lab_test.comp = comp_test
                        lab_test.save()
                    except LabTest.DoesNotExist:
                        self.stderr.write(self.style.ERROR(f'LabTest with id {row["comp"]} does not exist.'))
                        return
        self.stdout.write(self.style.SUCCESS('Successfully imported LabTests from CSV'))