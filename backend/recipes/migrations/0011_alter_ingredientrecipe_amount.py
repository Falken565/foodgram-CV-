# Generated by Django 3.2.9 on 2021-12-22 15:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0010_auto_20211220_0159'),
    ]

    operations = [
        migrations.AlterField(
            model_name='ingredientrecipe',
            name='amount',
            field=models.IntegerField(verbose_name='Количество'),
        ),
    ]