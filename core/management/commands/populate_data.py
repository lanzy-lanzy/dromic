from django.core.management.base import BaseCommand
from django.utils import timezone
from core.models import (
    Province, Municipality, Barangay, Disaster, AffectedArea,
    EvacuationCenter, Family, FamilyMember, DisplacedPopulation,
    SexAgeDistribution, SectoralDistribution, DamagedHouse,
    ReliefOperation, EarlyRecovery, DROMICReport
)
import random
from datetime import timedelta
from decimal import Decimal


# Official PSGC barangays of Dumingag, Zamboanga del Sur
# Source: https://psgc.gitlab.io/api/municipalities/097308000/barangays.json
DUMINGAG_BARANGAYS = [
    {
        "code": "097308002",
        "name": "Bag-ong Valencia",
        "lat": 8.1331,
        "lng": 123.282
    },
    {
        "code": "097308003",
        "name": "Bucayan",
        "lat": 8.1365,
        "lng": 123.3139
    },
    {
        "code": "097308004",
        "name": "Calumanggi",
        "lat": 8.0977,
        "lng": 123.2895
    },
    {
        "code": "097308005",
        "name": "Caridad",
        "lat": 8.1503,
        "lng": 123.3601
    },
    {
        "code": "097308006",
        "name": "Danlugan",
        "lat": 8.1458,
        "lng": 123.2174
    },
    {
        "code": "097308007",
        "name": "Datu Totocan",
        "lat": 8.1261,
        "lng": 123.2239
    },
    {
        "code": "097308008",
        "name": "Dilud",
        "lat": 8.1857,
        "lng": 123.3335
    },
    {
        "code": "097308009",
        "name": "Ditulan",
        "lat": 8.1803,
        "lng": 123.2857
    },
    {
        "code": "097308010",
        "name": "Dulian",
        "lat": 8.1161,
        "lng": 123.229
    },
    {
        "code": "097308011",
        "name": "Dulop",
        "lat": 8.2137,
        "lng": 123.2318
    },
    {
        "code": "097308012",
        "name": "Guintananan",
        "lat": 8.1799,
        "lng": 123.2601
    },
    {
        "code": "097308013",
        "name": "Guitran",
        "lat": 8.1599,
        "lng": 123.367
    },
    {
        "code": "097308014",
        "name": "Gumpingan",
        "lat": 8.1018,
        "lng": 123.2622
    },
    {
        "code": "097308015",
        "name": "La Fortuna",
        "lat": 8.1488,
        "lng": 123.2897
    },
    {
        "code": "097308016",
        "name": "Libertad",
        "lat": 8.1402,
        "lng": 123.3544
    },
    {
        "code": "097308017",
        "name": "Licabang",
        "lat": 8.1986,
        "lng": 123.2535
    },
    {
        "code": "097308018",
        "name": "Lipawan",
        "lat": 8.1718,
        "lng": 123.3453
    },
    {
        "code": "097308019",
        "name": "Lower Landing",
        "lat": 8.1535,
        "lng": 123.3313
    },
    {
        "code": "097308020",
        "name": "Lower Timonan",
        "lat": 8.1155,
        "lng": 123.361
    },
    {
        "code": "097308021",
        "name": "Macasing",
        "lat": 8.1361,
        "lng": 123.2419
    },
    {
        "code": "097308022",
        "name": "Mahayahay",
        "lat": 8.1621,
        "lng": 123.3154
    },
    {
        "code": "097308023",
        "name": "Malagalad",
        "lat": 8.1528,
        "lng": 123.2394
    },
    {
        "code": "097308024",
        "name": "Manlabay",
        "lat": 8.127,
        "lng": 123.3257
    },
    {
        "code": "097308025",
        "name": "Maralag",
        "lat": 8.1403,
        "lng": 123.3696
    },
    {
        "code": "097308026",
        "name": "Marangan",
        "lat": 8.1028,
        "lng": 123.3395
    },
    {
        "code": "097308027",
        "name": "New Basak",
        "lat": 8.1357,
        "lng": 123.3352
    },
    {
        "code": "097308030",
        "name": "Bagong Kauswagan",
        "lat": 8.1256,
        "lng": 123.2968
    },
    {
        "code": "097308032",
        "name": "Saad",
        "lat": 8.2297,
        "lng": 123.3175
    },
    {
        "code": "097308033",
        "name": "Salvador",
        "lat": 8.234,
        "lng": 123.2462
    },
    {
        "code": "097308034",
        "name": "San Pablo (Pob.)",
        "lat": 8.1544,
        "lng": 123.3454
    },
    {
        "code": "097308035",
        "name": "San Pedro (Pob.)",
        "lat": 8.1573,
        "lng": 123.3427
    },
    {
        "code": "097308037",
        "name": "San Vicente",
        "lat": 8.1059,
        "lng": 123.2937
    },
    {
        "code": "097308038",
        "name": "Senote",
        "lat": 8.1201,
        "lng": 123.267
    },
    {
        "code": "097308039",
        "name": "Sinonok",
        "lat": 8.2197,
        "lng": 123.3
    },
    {
        "code": "097308041",
        "name": "Sunop",
        "lat": 8.2063,
        "lng": 123.3704
    },
    {
        "code": "097308042",
        "name": "Tagun",
        "lat": 8.1448,
        "lng": 123.2629
    },
    {
        "code": "097308043",
        "name": "Tamurayan",
        "lat": 8.1378,
        "lng": 123.2649
    },
    {
        "code": "097308045",
        "name": "Upper Landing",
        "lat": 8.1637,
        "lng": 123.334
    },
    {
        "code": "097308046",
        "name": "Upper Timonan",
        "lat": 8.1228,
        "lng": 123.3455
    },
    {
        "code": "097308047",
        "name": "Bagong Silang",
        "lat": 8.1113,
        "lng": 123.2461
    },
    {
        "code": "097308048",
        "name": "Dapiwak",
        "lat": 8.199,
        "lng": 123.2875
    },
    {
        "code": "097308049",
        "name": "Labangon",
        "lat": 8.1262,
        "lng": 123.1863
    },
    {
        "code": "097308050",
        "name": "San Juan",
        "lat": 8.0887,
        "lng": 123.2977
    },
    {
        "code": "097308051",
        "name": "Canibongan",
        "lat": 8.1686,
        "lng": 123.2301
    }
]


# Filipino family names
FILIPINO_SURNAMES = [
    "Dela Cruz", "Santos", "Reyes", "Cruz", "Bautista",
    "Gonzales", "Garcia", "Lopez", "Fernandez", "Torres",
    "Aquino", "Mendoza", "Ramos", "Rivera", "Castro",
    "Villanueva", "Maglangit", "Salcedo", "Pangilinan", "Tan",
    "Espino", "Navarro", "Magallanes", "Corpuz", "Ocampo",
    "Padilla", "Manalo", "Soriano", "Aguilar", "Flores",
    "Dimacali", "Zamora", "Santiago", "Perez", "Hernandez",
]

FILIPINO_FIRST_NAMES_MALE = [
    "Juan", "Jose", "Pedro", "Antonio", "Manuel",
    "Ricardo", "Eduardo", "Fernando", "Roberto", "Carlos",
    "Miguel", "Rafael", "Alejandro", "Danilo", "Ernesto",
    "Reynaldo", "Rolando", "Romeo", "Jaime", "Joel",
    "Mark", "John", "James", "Kevin", "Christian",
]

FILIPINO_FIRST_NAMES_FEMALE = [
    "Maria", "Ana", "Rosa", "Lourdes", "Carmen",
    "Josefina", "Teresa", "Gloria", "Luz", "Elena",
    "Patricia", "Cristina", "Rosario", "Concepcion", "Milagros",
    "Jennifer", "Mary Jane", "Angelica", "Grace", "Joy",
    "Faith", "Princess", "Angel", "Precious", "Lovely",
]

DISASTER_DATA = [
    {
        "name": "Typhoon Aghon (Ewiniar)",
        "description": "Severe tropical storm bringing heavy rainfall and strong winds across Zamboanga Peninsula, causing widespread flooding and landslides in mountainous areas of Zamboanga del Sur.",
        "days_ago": 45,
    },
    {
        "name": "Tropical Storm Butchoy",
        "description": "Tropical storm that triggered flash floods and river overflows in low-lying barangays of Dumingag municipality, displacing hundreds of families.",
        "days_ago": 120,
    },
    {
        "name": "Southwest Monsoon Flooding 2026",
        "description": "Enhanced southwest monsoon (habagat) causing continuous heavy rains for 3 days, resulting in severe flooding across multiple barangays in Dumingag and surrounding municipalities.",
        "days_ago": 15,
    },
]

EVAC_CENTER_NAMES = [
    "{brgy} Elementary School", "{brgy} Covered Court",
    "{brgy} Multi-Purpose Hall", "{brgy} Day Care Center",
    "{brgy} Community Center", "{brgy} Barangay Hall",
    "{brgy} Chapel", "Dumingag National High School",
    "Dumingag Central Elementary School",
    "Dumingag Sports Complex",
]

EARLY_RECOVERY_DESCRIPTIONS = [
    "Debris clearing and road rehabilitation in affected barangays",
    "Temporary shelter construction for totally displaced families",
    "Water system repair and restoration of potable water supply",
    "Rehabilitation of damaged school buildings and learning facilities",
    "Agricultural livelihood recovery program - distribution of seeds and farming tools",
    "Bridge and drainage repair to prevent future flooding",
    "Psychosocial support program for affected children and families",
    "Cash-for-work program for debris clearing and community cleanup",
    "Distribution of construction materials for house repair",
    "Restoration of electrical power lines in remote barangays",
]

SECTORS = [
    "Farmers/Fisherfolk", "Women", "Children",
    "Senior Citizens", "Indigenous Peoples",
    "Persons with Disabilities", "Solo Parents",
    "Out-of-School Youth", "Pregnant/Lactating Women",
]


class Command(BaseCommand):
    help = 'Resets the database and populates with realistic Zamboanga del Sur (Dumingag) sample data'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.WARNING('Flushing all existing data...'))
        self._flush_all()

        self.stdout.write('Creating locations (Zamboanga del Sur → Dumingag → Barangays)...')
        province, municipality, barangays = self._create_locations()

        self.stdout.write('Creating disasters...')
        disasters = self._create_disasters()

        self.stdout.write('Creating evacuation centers...')
        evac_centers = self._create_evacuation_centers(province, municipality, barangays)

        for disaster in disasters:
            self.stdout.write(f'  Populating data for: {disaster.name}')
            self._create_disaster_data(disaster, province, municipality, barangays, evac_centers)

        self.stdout.write('Creating DROMIC reports...')
        self._create_dromic_reports(disasters, province, municipality, barangays)

        # Print summary
        self.stdout.write('')
        self.stdout.write(self.style.SUCCESS('═' * 60))
        self.stdout.write(self.style.SUCCESS('Database populated successfully!'))
        self.stdout.write(self.style.SUCCESS('═' * 60))
        self.stdout.write(f'  Provinces:              {Province.objects.count()}')
        self.stdout.write(f'  Municipalities:         {Municipality.objects.count()}')
        self.stdout.write(f'  Barangays:              {Barangay.objects.count()}')
        self.stdout.write(f'  Disasters:              {Disaster.objects.count()}')
        self.stdout.write(f'  Affected Areas:         {AffectedArea.objects.count()}')
        self.stdout.write(f'  Evacuation Centers:     {EvacuationCenter.objects.count()}')
        self.stdout.write(f'  Families:               {Family.objects.count()}')
        self.stdout.write(f'  Family Members:         {FamilyMember.objects.count()}')
        self.stdout.write(f'  Displaced Populations:  {DisplacedPopulation.objects.count()}')
        self.stdout.write(f'  Sex/Age Distributions:  {SexAgeDistribution.objects.count()}')
        self.stdout.write(f'  Sectoral Distributions: {SectoralDistribution.objects.count()}')
        self.stdout.write(f'  Damaged Houses:         {DamagedHouse.objects.count()}')
        self.stdout.write(f'  Relief Operations:      {ReliefOperation.objects.count()}')
        self.stdout.write(f'  Early Recovery:         {EarlyRecovery.objects.count()}')
        self.stdout.write(f'  DROMIC Reports:         {DROMICReport.objects.count()}')

    def _flush_all(self):
        """Delete all data from all tables in correct order."""
        DROMICReport.objects.all().delete()
        SexAgeDistribution.objects.all().delete()
        SectoralDistribution.objects.all().delete()
        DisplacedPopulation.objects.all().delete()
        EarlyRecovery.objects.all().delete()
        ReliefOperation.objects.all().delete()
        DamagedHouse.objects.all().delete()
        FamilyMember.objects.all().delete()
        Family.objects.all().delete()
        EvacuationCenter.objects.all().delete()
        AffectedArea.objects.all().delete()
        Disaster.objects.all().delete()
        Barangay.objects.all().delete()
        Municipality.objects.all().delete()
        Province.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('  All tables flushed.'))

    def _create_locations(self):
        """Create Zamboanga del Sur → Dumingag → Barangays (PSGC codes)."""
        province = Province.objects.create(
            name="Zamboanga Del Sur",
            code="097300000",
            longitude=123.3112,
            latitude=7.8357,
        )

        municipality = Municipality.objects.create(
            name="Dumingag",
            code="097308000",
            province=province,
            longitude=123.3469,
            latitude=7.8458,
        )

        barangays = []
        for brgy_data in DUMINGAG_BARANGAYS:
            brgy = Barangay.objects.create(
                name=brgy_data["name"],
                code=brgy_data["code"],
                municipality=municipality,
                longitude=brgy_data["lng"],
                latitude=brgy_data["lat"],
            )
            barangays.append(brgy)

        return province, municipality, barangays

    def _create_disasters(self):
        """Create realistic disaster events."""
        disasters = []
        for d in DISASTER_DATA:
            disaster = Disaster.objects.create(
                name=d["name"],
                description=d["description"],
                date_occurred=timezone.now().date() - timedelta(days=d["days_ago"]),
            )
            disasters.append(disaster)
        return disasters

    def _create_evacuation_centers(self, province, municipality, barangays):
        """Create evacuation centers in various barangays."""
        centers = []
        used_names = set()
        # Create 15-20 evacuation centers
        center_barangays = random.sample(barangays, min(18, len(barangays)))
        for brgy in center_barangays:
            template = random.choice(EVAC_CENTER_NAMES)
            name = template.format(brgy=brgy.name)
            if name in used_names:
                name += " Annex"
            used_names.add(name)

            capacity = random.choice([100, 150, 200, 250, 300, 400, 500])
            occupancy = random.randint(int(capacity * 0.3), int(capacity * 0.9))

            center = EvacuationCenter.objects.create(
                name=name,
                province=province,
                municipality=municipality,
                barangay=brgy,
                capacity=capacity,
                current_occupancy=occupancy,
            )
            centers.append(center)
        return centers

    def _create_disaster_data(self, disaster, province, municipality, barangays, evac_centers):
        """Create all impact data for a disaster."""
        # Each disaster affects a subset of barangays
        affected_count = random.randint(8, min(20, len(barangays)))
        affected_brgys = random.sample(barangays, affected_count)

        for brgy in affected_brgys:
            families_count = random.randint(30, 350)
            persons_count = families_count * random.randint(3, 6)

            area = AffectedArea.objects.create(
                disaster=disaster,
                province=province,
                municipality=municipality,
                barangay=brgy,
                affected_families=families_count,
                affected_persons=persons_count,
            )

            # Families & members
            self._create_families(area, random.randint(5, 15))

            # Displaced population
            self._create_displaced_population(area, evac_centers)

            # Damaged houses
            DamagedHouse.objects.create(
                area=area,
                partially_damaged=random.randint(5, 80),
                totally_damaged=random.randint(2, 30),
            )

            # Relief operations
            ReliefOperation.objects.create(
                area=area,
                date=disaster.date_occurred + timedelta(days=random.randint(1, 14)),
                food_items=random.randint(50, 800),
                non_food_items=random.randint(20, 400),
                financial_assistance=Decimal(str(random.randint(5000, 150000))),
            )

            # Early recovery (not for all areas)
            if random.random() > 0.4:
                started = disaster.date_occurred + timedelta(days=random.randint(5, 30))
                completed = None
                if random.random() > 0.4:
                    completed = started + timedelta(days=random.randint(15, 90))
                EarlyRecovery.objects.create(
                    area=area,
                    description=random.choice(EARLY_RECOVERY_DESCRIPTIONS),
                    date_started=started,
                    date_completed=completed,
                )

    def _create_families(self, area, count):
        """Create families with Filipino names."""
        for _ in range(count):
            surname = random.choice(FILIPINO_SURNAMES)
            gender = random.choice(["Male", "Female"])
            if gender == "Male":
                first_name = random.choice(FILIPINO_FIRST_NAMES_MALE)
            else:
                first_name = random.choice(FILIPINO_FIRST_NAMES_FEMALE)

            num_members = random.randint(2, 7)
            family = Family.objects.create(
                area=area,
                head_of_family=f"{first_name} {surname}",
                number_of_members=num_members,
            )

            # Head of family
            FamilyMember.objects.create(
                family=family,
                name=f"{first_name} {surname}",
                age=random.randint(25, 60),
                gender=gender,
                relationship_to_head="Head",
                is_displaced=random.random() > 0.3,
                is_in_evacuation_center=random.random() > 0.5,
            )

            # Spouse
            if num_members >= 2:
                spouse_gender = "Female" if gender == "Male" else "Male"
                if spouse_gender == "Male":
                    spouse_name = random.choice(FILIPINO_FIRST_NAMES_MALE)
                else:
                    spouse_name = random.choice(FILIPINO_FIRST_NAMES_FEMALE)
                is_disp = random.random() > 0.3
                FamilyMember.objects.create(
                    family=family,
                    name=f"{spouse_name} {surname}",
                    age=random.randint(22, 58),
                    gender=spouse_gender,
                    relationship_to_head="Spouse",
                    is_displaced=is_disp,
                    is_in_evacuation_center=is_disp and random.random() > 0.4,
                )

            # Children and other members
            for j in range(num_members - 2):
                child_gender = random.choice(["Male", "Female"])
                if child_gender == "Male":
                    child_name = random.choice(FILIPINO_FIRST_NAMES_MALE)
                else:
                    child_name = random.choice(FILIPINO_FIRST_NAMES_FEMALE)
                relationship = random.choice(["Child", "Child", "Child", "Parent", "Sibling"])
                age = random.randint(1, 17) if relationship == "Child" else random.randint(55, 85)
                is_disp = random.random() > 0.3
                FamilyMember.objects.create(
                    family=family,
                    name=f"{child_name} {surname}",
                    age=age,
                    gender=child_gender,
                    relationship_to_head=relationship,
                    is_displaced=is_disp,
                    is_in_evacuation_center=is_disp and random.random() > 0.4,
                )

    def _create_displaced_population(self, area, evac_centers):
        """Create displaced population with sex/age and sectoral distributions."""
        evac = random.choice(evac_centers) if evac_centers else None
        cum_fam = random.randint(30, 250)
        now_fam = random.randint(int(cum_fam * 0.3), cum_fam)
        cum_per = cum_fam * random.randint(3, 5)
        now_per = now_fam * random.randint(3, 5)

        dp = DisplacedPopulation.objects.create(
            area=area,
            evacuation_center=evac,
            cum_families=cum_fam,
            now_families=now_fam,
            cum_persons=cum_per,
            now_persons=now_per,
        )

        # Sex/Age distribution
        for sex in ['Male', 'Female']:
            for age_group in ['0-5', '6-12', '13-17', '18-59', '60+']:
                cum = random.randint(5, 80)
                now = random.randint(int(cum * 0.3), cum)
                SexAgeDistribution.objects.create(
                    population=dp, sex=sex, age_group=age_group,
                    cum_count=cum, now_count=now,
                )

        # Sectoral distribution
        for sector in SECTORS:
            cum = random.randint(3, 60)
            now = random.randint(int(cum * 0.3), cum)
            SectoralDistribution.objects.create(
                population=dp, sector=sector,
                cum_count=cum, now_count=now,
            )

    def _create_dromic_reports(self, disasters, province, municipality, barangays):
        """Create DROMIC reports for each disaster."""
        for disaster in disasters:
            # Pick 2-3 barangays for each report
            report_brgys = random.sample(barangays, min(3, len(barangays)))
            for brgy in report_brgys:
                report = DROMICReport.objects.create(
                    disaster=disaster,
                    province=province,
                    municipality=municipality,
                    barangay=brgy,
                    date=disaster.date_occurred + timedelta(days=random.randint(1, 7)),
                )
                # Link related data
                areas = AffectedArea.objects.filter(disaster=disaster, barangay=brgy)
                report.affected_areas.set(areas)
                report.displaced_populations.set(
                    DisplacedPopulation.objects.filter(area__in=areas)
                )
                report.sex_age_distributions.set(
                    SexAgeDistribution.objects.filter(population__area__in=areas)
                )
                report.sectoral_distributions.set(
                    SectoralDistribution.objects.filter(population__area__in=areas)
                )
                report.damaged_houses.set(
                    DamagedHouse.objects.filter(area__in=areas)
                )
                report.relief_operations.set(
                    ReliefOperation.objects.filter(area__in=areas)
                )
                report.early_recovery.set(
                    EarlyRecovery.objects.filter(area__in=areas)
                )
                report.families.set(
                    Family.objects.filter(area__in=areas)
                )
