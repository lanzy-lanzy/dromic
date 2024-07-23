from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import *
import random
from datetime import timedelta

ZAMBOANGA_PENINSULA_DATA = {
    "Zamboanga del Norte": {
        "Dapitan City": ["Aliguay", "Ba-ao", "Bagting", "Banbanan", "Canlucani"],
        "Dipolog City": ["Barra", "Central", "Dicayas", "Diwan", "Estaka"],
        "Katipunan": ["Balok", "Barangay Dos", "Barangay Uno", "Basagan", "Bulawan"],
    },
    "Zamboanga del Sur": {
        "Pagadian City": ["Balangasan", "Balintawak", "Baloyboan", "Banale", "Bogo"],
        "Zamboanga City": ["Ayala", "Baliwasan", "Bolong", "Cabatangan", "Canelar"],
        "Aurora": ["Acad", "Alang-alang", "Bagong Mandaue", "Bagong Oroquieta", "Bayabas"],
    },
    "Zamboanga Sibugay": {
        "Ipil": ["Bacalan", "Bangkerohan", "Buluan", "Caparan", "Domandan"],
        "Buug": ["Ablayan", "Basalem", "Bawang", "Blancia", "Compostela"],
        "Kabasalan": ["Banker", "Bolo", "Cainglet", "Calapan", "Calubihan"],
    }
}

class Command(BaseCommand):
    help = 'Populates the database with comprehensive sample data for Zamboanga Peninsula'

    def handle(self, *args, **kwargs):
        self.stdout.write("Starting to populate the database...")
        
        provinces = self.create_locations()
        disasters = self.create_disasters()
        
        for disaster in disasters:
            self.create_disaster_data(disaster, provinces)
        
        self.stdout.write(self.style.SUCCESS('Successfully populated the database with comprehensive Zamboanga Peninsula data'))

    def create_locations(self):
        provinces = []
        for province_name, municipalities in ZAMBOANGA_PENINSULA_DATA.items():
            province = Province.objects.create(
                name=province_name,
                code=f"ZP{len(provinces)+1}",
                longitude=random.uniform(121.0, 123.0),
                latitude=random.uniform(7.0, 9.0)
            )
            provinces.append(province)
            
            for municipality_name, barangays in municipalities.items():
                municipality = Municipality.objects.create(
                    name=municipality_name,
                    code=f"ZM{len(Municipality.objects.all())+1}",
                    province=province,
                    longitude=random.uniform(province.longitude-0.5, province.longitude+0.5),
                    latitude=random.uniform(province.latitude-0.5, province.latitude+0.5)
                )
                
                for barangay_name in barangays:
                    Barangay.objects.create(
                        name=barangay_name,
                        code=f"ZB{len(Barangay.objects.all())+1}",
                        municipality=municipality,
                        longitude=random.uniform(municipality.longitude-0.1, municipality.longitude+0.1),
                        latitude=random.uniform(municipality.latitude-0.1, municipality.latitude+0.1)
                    )
        
        return provinces

    def create_disasters(self):
        disaster_types = ["Typhoon", "Flood", "Landslide", "Earthquake", "Storm Surge"]
        disasters = []
        for i in range(3):
            disaster = Disaster.objects.create(
                name=f"{random.choice(disaster_types)} {chr(65+i)}",
                description=f"A severe {disaster_types[i].lower()} that affected Zamboanga Peninsula",
                date_occurred=timezone.now().date() - timedelta(days=random.randint(1, 365))
            )
            disasters.append(disaster)
        return disasters

    def create_disaster_data(self, disaster, provinces):
        for province in provinces:
            municipalities = list(province.municipalities.all())
            for municipality in random.sample(municipalities, random.randint(1, len(municipalities))):
                barangays = list(municipality.barangays.all())
                for barangay in random.sample(barangays, random.randint(1, len(barangays))):
                    affected_area = self.create_affected_area(disaster, province, municipality, barangay)
                    self.create_evacuation_center(province, municipality, barangay)
                    self.create_families(affected_area)
                    self.create_displaced_population(affected_area)
                    self.create_damaged_houses(affected_area)
                    self.create_relief_operation(affected_area)
                    self.create_early_recovery(affected_area)
        
        self.create_dromic_report(disaster)

    def create_affected_area(self, disaster, province, municipality, barangay):
        return AffectedArea.objects.create(
            disaster=disaster,
            province=province,
            municipality=municipality,
            barangay=barangay,
            affected_families=random.randint(50, 500),
            affected_persons=random.randint(200, 2000)
        )

    def create_evacuation_center(self, province, municipality, barangay):
        return EvacuationCenter.objects.create(
            name=f"Evacuation Center in {barangay.name}",
            province=province,
            municipality=municipality,
            barangay=barangay,
            capacity=random.randint(100, 1000),
            current_occupancy=random.randint(50, 500)
        )

    def create_families(self, affected_area):
        for _ in range(random.randint(10, 50)):
            family = Family.objects.create(
                area=affected_area,
                head_of_family=f"Family Head {random.randint(1, 1000)}",
                number_of_members=random.randint(1, 8)
            )
            self.create_family_members(family)

    def create_family_members(self, family):
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

    def create_displaced_population(self, affected_area):
        displaced_population = DisplacedPopulation.objects.create(
            area=affected_area,
            evacuation_center=EvacuationCenter.objects.order_by('?').first(),
            cum_families=random.randint(50, 500),
            now_families=random.randint(25, 250),
            cum_persons=random.randint(200, 2000),
            now_persons=random.randint(100, 1000)
        )
        self.create_sex_age_distribution(displaced_population)
        self.create_sectoral_distribution(displaced_population)

    def create_sex_age_distribution(self, displaced_population):
        for sex in ['Male', 'Female']:
            for age_group in ['0-5', '6-12', '13-17', '18-59', '60+']:
                SexAgeDistribution.objects.create(
                    population=displaced_population,
                    sex=sex,
                    age_group=age_group,
                    cum_count=random.randint(10, 100),
                    now_count=random.randint(5, 50)
                )

    def create_sectoral_distribution(self, displaced_population):
        sectors = ['Agriculture', 'Fishing', 'Industry', 'Services']
        for sector in sectors:
            SectoralDistribution.objects.create(
                population=displaced_population,
                sector=sector,
                cum_count=random.randint(10, 100),
                now_count=random.randint(5, 50)
            )

    def create_damaged_houses(self, affected_area):
        DamagedHouse.objects.create(
            area=affected_area,
            partially_damaged=random.randint(10, 100),
            totally_damaged=random.randint(5, 50)
        )

    def create_relief_operation(self, affected_area):
        ReliefOperation.objects.create(
            area=affected_area,
            date=timezone.now().date() - timedelta(days=random.randint(1, 30)),
            food_items=random.randint(100, 1000),
            non_food_items=random.randint(50, 500),
            financial_assistance=random.uniform(10000, 100000)
        )

    def create_early_recovery(self, affected_area):
        EarlyRecovery.objects.create(
            area=affected_area,
            description="Early recovery efforts including debris clearing and temporary shelter construction",
            date_started=timezone.now().date() - timedelta(days=random.randint(1, 30)),
            date_completed=timezone.now().date() + timedelta(days=random.randint(1, 180))
        )

    def create_dromic_report(self, disaster):
        report = DROMICReport.objects.create(
            disaster=disaster,
            province=Province.objects.order_by('?').first(),
            municipality=Municipality.objects.order_by('?').first(),
            barangay=Barangay.objects.order_by('?').first(),
            date=timezone.now().date()
        )
        report.affected_areas.set(AffectedArea.objects.filter(disaster=disaster))
        report.displaced_populations.set(DisplacedPopulation.objects.filter(area__disaster=disaster))
        report.sex_age_distributions.set(SexAgeDistribution.objects.filter(population__area__disaster=disaster))
        report.sectoral_distributions.set(SectoralDistribution.objects.filter(population__area__disaster=disaster))
        report.damaged_houses.set(DamagedHouse.objects.filter(area__disaster=disaster))
        report.relief_operations.set(ReliefOperation.objects.filter(area__disaster=disaster))
        report.early_recovery.set(EarlyRecovery.objects.filter(area__disaster=disaster))
        report.families.set(Family.objects.filter(area__disaster=disaster))
