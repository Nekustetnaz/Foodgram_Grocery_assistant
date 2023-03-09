import csv

from django.core.management.base import BaseCommand

from recipes.models import Ingredient


class Command(BaseCommand):
    """
    Command 'uploadcsv' uploads data from /data/ingredients.csv to Database.
    """

    help = 'Uploads data from ingredients.csv.'

    def handle(self, *args, **options):
        print('Loading ingredients data')
        with open(r'./data/ingredients.csv', encoding='utf-8') as csv_file:
            temp_data = [
                Ingredient(name=line[0], measurement_unit=line[1])
                for line in csv.reader(csv_file)
            ]
            Ingredient.objects.bulk_create(temp_data)
        print('Data successfully uploaded to database')
