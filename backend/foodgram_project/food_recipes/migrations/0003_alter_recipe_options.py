# Generated by Django 3.2.16 on 2025-03-06 05:53

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('food_recipes', '0002_auto_20250304_1617'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='recipe',
            options={'ordering': ['-pk'], 'verbose_name': 'Рецепт', 'verbose_name_plural': 'Рецепты'},
        ),
    ]
