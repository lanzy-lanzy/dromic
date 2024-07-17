# location/management/commands/populate_locations.py
import requests
from django.core.management.base import BaseCommand
from core.models import Province, Municipality, Barangay

BASE_API_URL = "https://psgc.gitlab.io/api"

# Specific province codes for Zamboanga Peninsula
ZAMBOANGA_PROVINCES = [
    {'code': '097200000', 'name': 'Zamboanga Del Norte'},
    {'code': '097300000', 'name': 'Zamboanga Del Sur'},
    {'code': '098300000', 'name': 'Zamboanga Sibugay'}
]

class Command(BaseCommand):
    help = 'Populates the database with provinces, municipalities, and barangays for Zamboanga Peninsula'

    def fetch_data(self, endpoint):
        url = f"{BASE_API_URL}/{endpoint}/"
        self.stdout.write(f"Fetching data from URL: {url}")
        response = requests.get(url)
        if response.status_code != 200:
            self.stderr.write(self.style.ERROR(f"Failed to fetch {endpoint} data from API, status code: {response.status_code}"))
            return None
        return response.json()

    def handle(self, *args, **kwargs):
        for province_info in ZAMBOANGA_PROVINCES:
            province_code = province_info['code']
            province_name = province_info['name']

            self.stdout.write(f"Processing province: {province_name} (Code: {province_code})")

            province, created = Province.objects.get_or_create(
                code=province_code,
                defaults={'name': province_name}
            )

            # Fetch municipalities for the province
            municipalities = self.fetch_data(f"provinces/{province_code}/municipalities")
            if not municipalities:
                self.stderr.write(self.style.ERROR(f"No municipalities found for province {province_name} (Code: {province_code})"))
                continue

            for municipality_data in municipalities:
                self.stdout.write(f"Processing municipality: {municipality_data['name']} (Code: {municipality_data['code']})")
                municipality, created = Municipality.objects.get_or_create(
                    code=municipality_data['code'],
                    province=province,
                    defaults={'name': municipality_data['name']}
                )

                # Fetch barangays for the municipality
                barangays = self.fetch_data(f"municipalities/{municipality_data['code']}/barangays")
                if not barangays:
                    self.stderr.write(self.style.ERROR(f"No barangays found for municipality {municipality_data['name']} (Code: {municipality_data['code']})"))
                    continue

                for barangay_data in barangays:
                    self.stdout.write(f"Processing barangay: {barangay_data['name']} (Code: {barangay_data['code']})")
                    Barangay.objects.get_or_create(
                        code=barangay_data['code'],
                        municipality=municipality,
                        defaults={'name': barangay_data['name']}
                    )

        self.stdout.write(self.style.SUCCESS('Successfully populated the locations data'))
