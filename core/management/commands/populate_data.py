from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import *
import random
from datetime import timedelta

class Command(BaseCommand):
    help = 'Populates the database with comprehensive data for Dumingag, Zamboanga del Sur'

    def handle(self, *args, **kwargs):
        # Create Province
        zamboanga_del_sur = Province.objects.create(name="Zamboanga del Sur")

        # Create Municipality
        dumingag = Municipality.objects.create(
            province=zamboanga_del_sur,
            name="Dumingag",
            latitude=8.1667,
            longitude=123.3667
        )

        # Create all 44 Barangays of Dumingag
        barangays_data = [
            ("Bagong Kauswagan", 8.1667, 123.3500), ("Bagong Silang", 8.1833, 123.3667),
            ("Bitoon", 8.1500, 123.3833), ("Bucayan", 8.2000, 123.3500),
            ("Canibongan", 8.1833, 123.3833), ("Caridad", 8.1667, 123.3833),
            ("Datu Totoca", 8.1500, 123.3667), ("Dilud", 8.2000, 123.3667),
            ("Dulian", 8.1833, 123.3500), ("Guintananan", 8.1500, 123.3500),
            ("Gumpingan", 8.1750, 123.3750), ("La Fortuna", 8.1917, 123.3583),
            ("Labangon", 8.1583, 123.3750), ("Licabang", 8.2083, 123.3583),
            ("Lower Landing", 8.1750, 123.3583), ("Lower Timonan", 8.1917, 123.3750),
            ("Macasing", 8.1583, 123.3583), ("Mahayahay", 8.2083, 123.3750),
            ("Malagalad", 8.1750, 123.3917), ("Maralag", 8.1917, 123.3417),
            ("Marangan", 8.1583, 123.3917), ("Matin-ao", 8.2083, 123.3417),
            ("New Basak", 8.1750, 123.3417), ("Nilo", 8.1917, 123.3917),
            ("Ocapan", 8.1583, 123.3417), ("Pag-asa", 8.2083, 123.3917),
            ("Panagaan", 8.1667, 123.3750), ("Panduma", 8.1833, 123.3583),
            ("Poblacion", 8.1500, 123.3750), ("Saad", 8.2000, 123.3583),
            ("San Juan", 8.1667, 123.3583), ("San Pablo", 8.1833, 123.3750),
            ("San Pedro", 8.1500, 123.3583), ("San Vicente", 8.2000, 123.3750),
            ("Santo Niño", 8.1667, 123.3917), ("Senote", 8.1833, 123.3417),
            ("Sinonoc", 8.1500, 123.3917), ("Sunop", 8.2000, 123.3417),
            ("Tagun", 8.1667, 123.3417), ("Tamurayan", 8.1833, 123.3917),
            ("Tigbao", 8.1500, 123.3417), ("Upper Landing", 8.2000, 123.3917),
            ("Upper Timonan", 8.1667, 123.4083), ("Yayang", 8.1833, 123.4083)
        ]

        barangays = []
        for name, lat, lon in barangays_data:
            barangay = Barangay.objects.create(
                municipality=dumingag,
                name=name,
                latitude=lat,
                longitude=lon
            )
            barangays.append(barangay)

        # Create Disasters
        disasters = [
            Disaster.objects.create(
                name="Typhoon Odette",
                description="Strong typhoon affecting Mindanao",
                date_occurred=timezone.now().date() - timedelta(days=30)
            ),
            Disaster.objects.create(
                name="Flash Flood",
                description="Sudden flooding due to heavy rainfall",
                date_occurred=timezone.now().date() - timedelta(days=15)
            ),
            Disaster.objects.create(
                name="Earthquake",
                description="Magnitude 6.2 earthquake",
                date_occurred=timezone.now().date() - timedelta(days=7)
            )
        ]

        # Create Affected Areas
        for disaster in disasters:
            for barangay in random.sample(barangays, 20):  # Randomly affect 20 barangays
                AffectedArea.objects.create(
                    disaster=disaster,
                    province=zamboanga_del_sur,
                    municipality=dumingag,
                    barangay=barangay,
                    affected_families=random.randint(50, 200),
                    affected_persons=random.randint(200, 1000)
                )

        # Create Evacuation Centers
        for i in range(10):
            EvacuationCenter.objects.create(
                name=f"Dumingag Evacuation Center {i+1}",
                location=random.choice(barangays).name,
                capacity=random.randint(100, 500),
                current_occupancy=random.randint(50, 100)
            )

        # Create Families and Family Members
        for area in AffectedArea.objects.all():
            for _ in range(random.randint(10, 30)):
                family = Family.objects.create(
                    area=area,
                    head_of_family=f"Family Head {random.randint(1, 1000)}",
                    number_of_members=random.randint(2, 8)
                )
                for _ in range(family.number_of_members):
                    FamilyMember.objects.create(
                        family=family,
                        name=f"Family Member {random.randint(1, 1000)}",
                        age=random.randint(1, 80),
                        gender=random.choice(['Male', 'Female']),
                        relationship_to_head=random.choice(['Spouse', 'Child', 'Parent', 'Sibling']),
                        is_displaced=random.choice([True, False]),
                        is_in_evacuation_center=random.choice([True, False])
                    )

        # Create DROMIC Reports
        for disaster in disasters:
            report = DROMICReport.objects.create(
                disaster=disaster,
                province=zamboanga_del_sur,
                municipality=dumingag,
                barangay=random.choice(barangays),
                date=disaster.date_occurred + timedelta(days=1)
            )
            affected_areas = AffectedArea.objects.filter(disaster=disaster)
            report.affected_areas.set(affected_areas)

            # Create Displaced Population
            for area in affected_areas:
                displaced_pop = DisplacedPopulation.objects.create(
                    area=area,
                    evacuation_center=EvacuationCenter.objects.order_by('?').first(),
                    cum_families=random.randint(30, 100),
                    now_families=random.randint(20, 80),
                    cum_persons=random.randint(150, 500),
                    now_persons=random.randint(100, 400)
                )
                report.displaced_populations.add(displaced_pop)

                # Create Sex Age Distribution
                for sex in ['Male', 'Female']:
                    for age_group in ['0-5', '6-12', '13-17', '18-59', '60+']:
                        SexAgeDistribution.objects.create(
                            population=displaced_pop,
                            sex=sex,
                            age_group=age_group,
                            cum_count=random.randint(10, 50),
                            now_count=random.randint(5, 45)
                        )

                # Create Sectoral Distribution
                for sector in ['Pregnant', 'Lactating', 'PWD', 'Senior Citizen']:
                    SectoralDistribution.objects.create(
                        population=displaced_pop,
                        sector=sector,
                        cum_count=random.randint(5, 20),
                        now_count=random.randint(3, 18)
                    )

            # Create Damaged Houses
            DamagedHouse.objects.create(
                area=random.choice(affected_areas),
                partially_damaged=random.randint(20, 100),
                totally_damaged=random.randint(5, 50)
            )

            # Create Relief Operation
            ReliefOperation.objects.create(
                area=random.choice(affected_areas),
                date=disaster.date_occurred + timedelta(days=random.randint(1, 5)),
                food_items=random.randint(100, 500),
                non_food_items=random.randint(50, 300),
                financial_assistance=random.uniform(10000, 100000)
            )

            # Create Early Recovery
            EarlyRecovery.objects.create(
                area=random.choice(affected_areas),
                description="Initial recovery efforts underway",
                date_started=disaster.date_occurred + timedelta(days=random.randint(5, 10)),
                date_completed=disaster.date_occurred + timedelta(days=random.randint(15, 30))
            )

        self.stdout.write(self.style.SUCCESS('Successfully populated the database with comprehensive Dumingag, Zamboanga del Sur data'))
