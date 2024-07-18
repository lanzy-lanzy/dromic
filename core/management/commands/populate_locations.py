# location/management/commands/populate_locations.py
import requests
from django.core.management.base import BaseCommand
from django.conf import settings
from core.models import Province, Municipality, Barangay
import time

BASE_API_URL = "https://psgc.gitlab.io/api"

# Specific province codes for Zamboanga Peninsula
ZAMBOANGA_PROVINCES = [
    # {'code': '097200000', 'name': 'Zamboanga Del Norte'},
    # {'code': '097300000', 'name': 'Zamboanga Del Sur'},
    {'code': '098300000', 'name': 'Zamboanga Sibugay'}
]

MAX_RETRIES = 2

RETRY_DELAY = 1  # seconds

class Command(BaseCommand):
    help = 'Populates the database with provinces, municipalities, and barangays for Zamboanga Peninsula'

    def fetch_data_with_retry(self, endpoint):
        url = f"{BASE_API_URL}/{endpoint}/"
        for attempt in range(MAX_RETRIES):
            try:
                self.stdout.write(f"Fetching data from URL: {url} (Attempt {attempt + 1})")
                response = requests.get(url)
                response.raise_for_status()
                return response.json()
            except requests.RequestException as e:
                self.stderr.write(self.style.WARNING(f"Attempt {attempt + 1} failed: {str(e)}"))
                if attempt < MAX_RETRIES - 1:
                    self.stdout.write(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    self.stderr.write(self.style.ERROR(f"Failed to fetch {endpoint} data after {MAX_RETRIES} attempts"))
                    return None

    def fetch_geolocation_with_retry(self, name):
        for attempt in range(MAX_RETRIES):
            try:
                response = requests.get(
                    'https://maps.googleapis.com/maps/api/geocode/json',
                    params={'address': name, 'key': settings.GOOGLE_MAPS_API_KEY}
                )
                response.raise_for_status()
                response_data = response.json()
                if response_data['status'] == 'OK':
                    location = response_data['results'][0]['geometry']['location']
                    return location['lat'], location['lng']
                else:
                    raise requests.RequestException(f"Geolocation API returned status: {response_data['status']}")
            except requests.RequestException as e:
                self.stderr.write(self.style.WARNING(f"Attempt {attempt + 1} failed to fetch geolocation for {name}: {str(e)}"))
                if attempt < MAX_RETRIES - 1:
                    self.stdout.write(f"Retrying in {RETRY_DELAY} seconds...")
                    time.sleep(RETRY_DELAY)
                else:
                    self.stderr.write(self.style.ERROR(f"Failed to fetch geolocation for {name} after {MAX_RETRIES} attempts"))
                    return None, None

    def handle(self, *args, **kwargs):
        for province_info in ZAMBOANGA_PROVINCES:
            province_code = province_info['code']
            province_name = province_info['name']

            self.stdout.write(f"Processing province: {province_name} (Code: {province_code})")

            lat, lng = self.fetch_geolocation_with_retry(province_name)
            province, created = Province.objects.get_or_create(
                code=province_code,
                defaults={'name': province_name, 'latitude': lat, 'longitude': lng}
            )

            # Fetch municipalities for the province
            municipalities = self.fetch_data_with_retry(f"provinces/{province_code}/municipalities")
            if not municipalities:
                self.stderr.write(self.style.ERROR(f"No municipalities found for province {province_name} (Code: {province_code})"))
                continue

            for municipality_data in municipalities:
                self.stdout.write(f"Processing municipality: {municipality_data['name']} (Code: {municipality_data['code']})")
                lat, lng = self.fetch_geolocation_with_retry(municipality_data['name'])
                municipality, created = Municipality.objects.get_or_create(
                    code=municipality_data['code'],
                    province=province,
                    defaults={'name': municipality_data['name'], 'latitude': lat, 'longitude': lng}
                )

                # Fetch barangays for the municipality
                barangays = self.fetch_data_with_retry(f"municipalities/{municipality_data['code']}/barangays")
                if not barangays:
                    self.stderr.write(self.style.ERROR(f"No barangays found for municipality {municipality_data['name']} (Code: {municipality_data['code']})"))
                    continue

                for barangay_data in barangays:
                    self.stdout.write(f"Processing barangay: {barangay_data['name']} (Code: {barangay_data['code']})")
                    lat, lng = self.fetch_geolocation_with_retry(barangay_data['name'])
                    Barangay.objects.get_or_create(
                        code=barangay_data['code'],
                        municipality=municipality,
                        defaults={'name': barangay_data['name'], 'latitude': lat, 'longitude': lng}
                    )

        self.stdout.write(self.style.SUCCESS('Successfully populated the locations data'))
        