from django.db import models

class Province(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Municipality(models.Model):
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Barangay(models.Model):
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class Disaster(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    date_occurred = models.DateField()

    def __str__(self):
        return self.name

class AffectedArea(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    affected_families = models.IntegerField()
    affected_persons = models.IntegerField()

    def __str__(self):
        return f"{self.barangay.name}, {self.municipality.name}, {self.province.name} - {self.disaster.name}"

class EvacuationCenter(models.Model):
    name = models.CharField(max_length=100)
    location = models.CharField(max_length=255)
    capacity = models.IntegerField()
    current_occupancy = models.IntegerField(default=0)

    def __str__(self):
        return self.name

    @property
    def is_full(self):
        return self.current_occupancy >= self.capacity


class Family(models.Model):
    area = models.ForeignKey(AffectedArea, on_delete=models.CASCADE)
    head_of_family = models.CharField(max_length=100)
    number_of_members = models.IntegerField()

    def __str__(self):
        return f"Family of {self.head_of_family} in {self.area}"

class FamilyMember(models.Model):
    family = models.ForeignKey(Family, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    age = models.IntegerField()
    gender = models.CharField(max_length=10)
    relationship_to_head = models.CharField(max_length=50)
    is_displaced = models.BooleanField(default=False)
    is_in_evacuation_center = models.BooleanField(default=False)

    def __str__(self):
        return self.name

class DisplacedPopulation(models.Model):
    area = models.ForeignKey(AffectedArea, on_delete=models.CASCADE)
    evacuation_center = models.ForeignKey(EvacuationCenter, on_delete=models.CASCADE, null=True, blank=True)
    cum_families = models.IntegerField()
    now_families = models.IntegerField()
    cum_persons = models.IntegerField()
    now_persons = models.IntegerField()
    
    def __str__(self):
        return f"{self.area.barangay.name}, {self.area.municipality.name}, {self.area.province.name} - {self.area.disaster.name}"
class SexAgeDistribution(models.Model):
    population = models.ForeignKey(DisplacedPopulation, on_delete=models.CASCADE)
    sex = models.CharField(max_length=10)
    age_group = models.CharField(max_length=20)
    cum_count = models.IntegerField()
    now_count = models.IntegerField()

class SectoralDistribution(models.Model):
    population = models.ForeignKey(DisplacedPopulation, on_delete=models.CASCADE)
    sector = models.CharField(max_length=50)
    cum_count = models.IntegerField()
    now_count = models.IntegerField()

class DamagedHouse(models.Model):
    area = models.ForeignKey(AffectedArea, on_delete=models.CASCADE)
    partially_damaged = models.IntegerField()
    totally_damaged = models.IntegerField()

class ReliefOperation(models.Model):
    area = models.ForeignKey(AffectedArea, on_delete=models.CASCADE)
    date = models.DateField()
    food_items = models.IntegerField()
    non_food_items = models.IntegerField()
    financial_assistance = models.DecimalField(max_digits=10, decimal_places=2)

class EarlyRecovery(models.Model):
    area = models.ForeignKey(AffectedArea, on_delete=models.CASCADE)
    description = models.TextField()
    date_started = models.DateField()
    date_completed = models.DateField(null=True, blank=True)

class DROMICReport(models.Model):
    disaster = models.ForeignKey(Disaster, on_delete=models.CASCADE)
    province = models.ForeignKey(Province, on_delete=models.CASCADE)
    municipality = models.ForeignKey(Municipality, on_delete=models.CASCADE)
    barangay = models.ForeignKey(Barangay, on_delete=models.CASCADE)
    date = models.DateField()
    affected_areas = models.ManyToManyField(AffectedArea)
    displaced_populations = models.ManyToManyField(DisplacedPopulation)
    sex_age_distributions = models.ManyToManyField(SexAgeDistribution)
    sectoral_distributions = models.ManyToManyField(SectoralDistribution)
    damaged_houses = models.ManyToManyField(DamagedHouse)
    relief_operations = models.ManyToManyField(ReliefOperation)
    early_recovery = models.ManyToManyField(EarlyRecovery)
    families = models.ManyToManyField(Family)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def total_affected_families(self):
        return sum(area.affected_families for area in self.affected_areas.all())

    def total_affected_persons(self):
        return sum(area.affected_persons for area in self.affected_areas.all())
    def __str__(self):
        return f"DROMIC Report for {self.barangay.name}, {self.municipality.name}, {self.province.name} on {self.date}"