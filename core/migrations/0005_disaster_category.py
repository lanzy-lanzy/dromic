# Generated migration for disaster category field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_family_house_condition'),
    ]

    operations = [
        migrations.AddField(
            model_name='disaster',
            name='category',
            field=models.CharField(
                choices=[
                    ('typhoon', 'Typhoon'),
                    ('earthquake', 'Earthquake'),
                    ('flood', 'Flood'),
                    ('landslide', 'Landslide'),
                    ('landslip', 'Landslip'),
                    ('volcanic_eruption', 'Volcanic Eruption'),
                    ('drought', 'Drought'),
                    ('tsunami', 'Tsunami'),
                    ('wildfire', 'Wildfire'),
                    ('fire', 'Fire'),
                    ('storm_surge', 'Storm Surge'),
                    ('strong_wind', 'Strong Wind'),
                    ('heavy_rain', 'Heavy Rain'),
                    ('thunderstorm', 'Thunderstorm'),
                    ('fallen_trees', 'Fallen Trees'),
                    ('disease_outbreak', 'Disease Outbreak'),
                    ('other', 'Other'),
                ],
                default='other',
                max_length=50
            ),
        ),
    ]
