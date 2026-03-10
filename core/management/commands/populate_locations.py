from django.core.management.base import BaseCommand
from core.models import Province, Municipality, Barangay

# Official PSGC barangays of Dumingag, Zamboanga del Sur
# Source: https://psgc.gitlab.io/api/municipalities/097308000/barangays.json
DUMINGAG_BARANGAYS = [
    {"code": "097308002", "name": "Bag-ong Valencia", "lat": 8.1331, "lng": 123.282},
    {"code": "097308003", "name": "Bucayan", "lat": 8.1365, "lng": 123.3139},
    {"code": "097308004", "name": "Calumanggi", "lat": 8.0977, "lng": 123.2895},
    {"code": "097308005", "name": "Caridad", "lat": 8.1503, "lng": 123.3601},
    {"code": "097308006", "name": "Danlugan", "lat": 8.1458, "lng": 123.2174},
    {"code": "097308007", "name": "Datu Totocan", "lat": 8.1261, "lng": 123.2239},
    {"code": "097308008", "name": "Dilud", "lat": 8.1857, "lng": 123.3335},
    {"code": "097308009", "name": "Ditulan", "lat": 8.1803, "lng": 123.2857},
    {"code": "097308010", "name": "Dulian", "lat": 8.1161, "lng": 123.229},
    {"code": "097308011", "name": "Dulop", "lat": 8.2137, "lng": 123.2318},
    {"code": "097308012", "name": "Guintananan", "lat": 8.1799, "lng": 123.2601},
    {"code": "097308013", "name": "Guitran", "lat": 8.1599, "lng": 123.367},
    {"code": "097308014", "name": "Gumpingan", "lat": 8.1018, "lng": 123.2622},
    {"code": "097308015", "name": "La Fortuna", "lat": 8.1488, "lng": 123.2897},
    {"code": "097308016", "name": "Libertad", "lat": 8.1402, "lng": 123.3544},
    {"code": "097308017", "name": "Licabang", "lat": 8.1986, "lng": 123.2535},
    {"code": "097308018", "name": "Lipawan", "lat": 8.1718, "lng": 123.3453},
    {"code": "097308019", "name": "Lower Landing", "lat": 8.1535, "lng": 123.3313},
    {"code": "097308020", "name": "Lower Timonan", "lat": 8.1155, "lng": 123.361},
    {"code": "097308021", "name": "Macasing", "lat": 8.1361, "lng": 123.2419},
    {"code": "097308022", "name": "Mahayahay", "lat": 8.1621, "lng": 123.3154},
    {"code": "097308023", "name": "Malagalad", "lat": 8.1528, "lng": 123.2394},
    {"code": "097308024", "name": "Manlabay", "lat": 8.127, "lng": 123.3257},
    {"code": "097308025", "name": "Maralag", "lat": 8.1403, "lng": 123.3696},
    {"code": "097308026", "name": "Marangan", "lat": 8.1028, "lng": 123.3395},
    {"code": "097308027", "name": "New Basak", "lat": 8.1357, "lng": 123.3352},
    {"code": "097308030", "name": "Bagong Kauswagan", "lat": 8.1256, "lng": 123.2968},
    {"code": "097308032", "name": "Saad", "lat": 8.2297, "lng": 123.3175},
    {"code": "097308033", "name": "Salvador", "lat": 8.234, "lng": 123.2462},
    {"code": "097308034", "name": "San Pablo (Pob.)", "lat": 8.1544, "lng": 123.3454},
    {"code": "097308035", "name": "San Pedro (Pob.)", "lat": 8.1573, "lng": 123.3427},
    {"code": "097308037", "name": "San Vicente", "lat": 8.1059, "lng": 123.2937},
    {"code": "097308038", "name": "Senote", "lat": 8.1201, "lng": 123.267},
    {"code": "097308039", "name": "Sinonok", "lat": 8.2197, "lng": 123.3},
    {"code": "097308041", "name": "Sunop", "lat": 8.2063, "lng": 123.3704},
    {"code": "097308042", "name": "Tagun", "lat": 8.1448, "lng": 123.2629},
    {"code": "097308043", "name": "Tamurayan", "lat": 8.1378, "lng": 123.2649},
    {"code": "097308045", "name": "Upper Landing", "lat": 8.1637, "lng": 123.334},
    {"code": "097308046", "name": "Upper Timonan", "lat": 8.1228, "lng": 123.3455},
    {"code": "097308047", "name": "Bagong Silang", "lat": 8.1113, "lng": 123.2461},
    {"code": "097308048", "name": "Dapiwak", "lat": 8.199, "lng": 123.2875},
    {"code": "097308049", "name": "Labangon", "lat": 8.1262, "lng": 123.1863},
    {"code": "097308050", "name": "San Juan", "lat": 8.0887, "lng": 123.2977},
    {"code": "097308051", "name": "Canibongan", "lat": 8.1686, "lng": 123.2301}
]

class Command(BaseCommand):
    help = 'Populates the database exclusively with Zamboanga del Sur and Dumingag locations'

    def handle(self, *args, **kwargs):
        self.stdout.write('Creating Province (Zamboanga del Sur)...')
        province, _ = Province.objects.get_or_create(
            code="097300000",
            defaults={
                "name": "Zamboanga Del Sur",
                "longitude": 123.3112,
                "latitude": 7.8357,
            }
        )

        self.stdout.write('Creating Municipality (Dumingag)...')
        municipality, _ = Municipality.objects.get_or_create(
            code="097308000",
            defaults={
                "name": "Dumingag",
                "province": province,
                "longitude": 123.3469,
                "latitude": 7.8458,
            }
        )

        self.stdout.write('Creating Barangays for Dumingag...')
        created_count = 0
        for brgy_data in DUMINGAG_BARANGAYS:
            name_val = "Barangay " + brgy_data["name"] if not brgy_data["name"].startswith("Barangay") else brgy_data["name"]
            
            # Use the provided name for getting or creating to maintain consistency.
            # If the original database had them without "Barangay ", they might be duplicated otherwise.
            # We will use exactly the name from array.
            name_val = brgy_data["name"]

            _, created = Barangay.objects.get_or_create(
                code=brgy_data["code"],
                defaults={
                    "name": name_val,
                    "municipality": municipality,
                    "longitude": brgy_data["lng"],
                    "latitude": brgy_data["lat"],
                }
            )
            if created:
                created_count += 1

        self.stdout.write(self.style.SUCCESS(f'Successfully ensured {len(DUMINGAG_BARANGAYS)} barangays exist for Dumingag! ({created_count} newly created)'))