# Generated by Django 3.2 on 2023-03-04 10:22

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_rename_quantity_ingredientsinrecipe_amount'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientsinrecipe',
            name='amount',
            field=models.PositiveIntegerField(default=1, verbose_name='Amount'),
        ),
    ]