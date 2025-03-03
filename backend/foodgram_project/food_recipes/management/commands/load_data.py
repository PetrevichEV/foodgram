import csv
import os

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from food_recipes.models import Ingredient

DATA_ROOT = os.path.join(settings.BASE_DIR, 'static/data/')


class Command(BaseCommand):
    def handle(self, *args, **options):
        try:
            with open(
                os.path.join(
                    DATA_ROOT, 'ingredients.csv'), 'r', encoding='utf-8'
            ) as csv_file:
                data = csv.reader(csv_file)
                for row in data:
                    try:
                        name, unit = row
                        Ingredient.objects.create(
                            name=name,
                            measurement_unit=unit,
                        )
                    except IntegrityError:
                        pass
                self.stdout.write(self.style.SUCCESS(
                    'Файл загружен успешно'))
        except FileNotFoundError:
            raise CommandError('Файл не найден')
