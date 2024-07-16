from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import *
import random

class Command(BaseCommand):
    help = 'Populates the database with sample data'

    def handle(self, *args, **kwargs):
        # Create Provinces, Municipalities, and Barangays
        province = Province.objects.create(name="Sample Province")
        municipality = Municipality.objects.create(province=province, name="Sample Municipality")
        barangay = Barangay.objects.create(municipality=municipality, name="Sample Barangay")

        # Create a Disaster
        disaster = Disaster.objects.create(
            name="Sample Disaster",
            description="A sample disaster for testing",
            date_occurred=timezone.now().date()
        )

        # Create an Affected Area
        affected_area = AffectedArea.objects.create(
            disaster=disaster,
            province=province,
            municipality=municipality,
            barangay=barangay,
            affected_families=100,
            affected_persons=500
        )

        # Create an Evacuation Center
        evac_center = EvacuationCenter.objects.create(
            name="Sample Evacuation Center",
            location="Sample Location",
            capacity=200
        )

        # Create Displaced Population
        displaced_pop = DisplacedPopulation.objects.create(
            area=affected_area,
            evacuation_center=evac_center,
            cum_families=80,
            now_families=75,
            cum_persons=400,
            now_persons=375
        )

        # Create Sex Age Distribution
        age_groups = ['0-5', '6-12', '13-17', '18-59', '60+']
        for sex in ['Male', 'Female']:
            for age_group in age_groups:
                SexAgeDistribution.objects.create(
                    population=displaced_pop,
                    sex=sex,
                    age_group=age_group,
                    cum_count=random.randint(10, 50),
                    now_count=random.randint(5, 45)
                )

        # Create Sectoral Distribution
        sectors = ['Pregnant', 'Lactating', 'PWD', 'Senior Citizen']
        for sector in sectors:
            SectoralDistribution.objects.create(
                population=displaced_pop,
                sector=sector,
                cum_count=random.randint(5, 20),
                now_count=random.randint(3, 18)
            )

        # Create Damaged Houses
        DamagedHouse.objects.create(
            area=affected_area,
            partially_damaged=30,
            totally_damaged=10
        )

        # Create Relief Operation
        ReliefOperation.objects.create(
            area=affected_area,
            date=timezone.now().date(),
            food_items=200,
            non_food_items=150,
            financial_assistance=50000.00
        )

        # Create Early Recovery
        EarlyRecovery.objects.create(
            area=affected_area,
            description="Sample early recovery efforts",
            date_started=timezone.now().date()
        )

        # Create DROMIC Report
        report = DROMICReport.objects.create(
            disaster=disaster,
            province=province,
            municipality=municipality,
            barangay=barangay,
            date=timezone.now().date()
        )
        report.affected_areas.add(affected_area)
        report.displaced_populations.add(displaced_pop)

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with sample data'))
