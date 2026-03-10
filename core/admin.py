from django.contrib import admin
from .models import (
    Province, Municipality, Barangay, Disaster, AffectedArea, EvacuationCenter,
    Family, FamilyMember, DisplacedPopulation, SexAgeDistribution,
    SectoralDistribution, DamagedHouse, ReliefOperation, EarlyRecovery,
    DROMICReport
)

@admin.register(Province)
class ProvinceAdmin(admin.ModelAdmin):
    list_display = ('code', 'name')
    search_fields = ('code', 'name')

@admin.register(Municipality)
class MunicipalityAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'province')
    list_filter = ('province',)
    search_fields = ('code', 'name', 'province__name')

@admin.register(Barangay)
class BarangayAdmin(admin.ModelAdmin):
    list_display = ('code', 'name', 'municipality')
    list_filter = ('municipality__province', 'municipality')
    search_fields = ('code', 'name', 'municipality__name', 'municipality__province__name')

@admin.register(Disaster)
class DisasterAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'date_occurred')
    list_filter = ('category', 'date_occurred')
    search_fields = ('name', 'description')

@admin.register(AffectedArea)
class AffectedAreaAdmin(admin.ModelAdmin):
    list_display = ('disaster', 'province', 'municipality', 'barangay', 'affected_families', 'affected_persons')
    list_filter = ('disaster', 'province', 'municipality')
    search_fields = ('disaster__name', 'province__name', 'municipality__name', 'barangay__name')

@admin.register(EvacuationCenter)
class EvacuationCenterAdmin(admin.ModelAdmin):
    list_display = ('name', 'province', 'municipality', 'barangay', 'capacity', 'current_occupancy', 'is_full')
    list_filter = ('province', 'municipality', 'barangay')
    search_fields = ('name', 'province__name', 'municipality__name', 'barangay__name')


@admin.register(Family)
class FamilyAdmin(admin.ModelAdmin):
    list_display = ('head_of_family', 'area', 'number_of_members')
    list_filter = ('area__disaster', 'area__province', 'area__municipality')
    search_fields = ('head_of_family', 'area__barangay__name')

@admin.register(FamilyMember)
class FamilyMemberAdmin(admin.ModelAdmin):
    list_display = ('name', 'family', 'age', 'gender', 'relationship_to_head', 'is_displaced', 'is_in_evacuation_center')
    list_filter = ('gender', 'is_displaced', 'is_in_evacuation_center')
    search_fields = ('name', 'family__head_of_family')

@admin.register(DisplacedPopulation)
class DisplacedPopulationAdmin(admin.ModelAdmin):
    list_display = ('area', 'evacuation_center', 'cum_families', 'now_families', 'cum_persons', 'now_persons')
    list_filter = ('area__disaster', 'area__province', 'area__municipality')
    search_fields = ('area__barangay__name', 'evacuation_center__name')

@admin.register(SexAgeDistribution)
class SexAgeDistributionAdmin(admin.ModelAdmin):
    list_display = ('population', 'sex', 'age_group', 'cum_count', 'now_count')
    list_filter = ('sex', 'age_group')
    search_fields = ('population__area__barangay__name',)

@admin.register(SectoralDistribution)
class SectoralDistributionAdmin(admin.ModelAdmin):
    list_display = ('population', 'sector', 'cum_count', 'now_count')
    list_filter = ('sector',)
    search_fields = ('population__area__barangay__name',)

@admin.register(DamagedHouse)
class DamagedHouseAdmin(admin.ModelAdmin):
    list_display = ('area', 'partially_damaged', 'totally_damaged')
    list_filter = ('area__disaster', 'area__province', 'area__municipality')
    search_fields = ('area__barangay__name',)

@admin.register(ReliefOperation)
class ReliefOperationAdmin(admin.ModelAdmin):
    list_display = ('area', 'date', 'food_items', 'non_food_items', 'financial_assistance')
    list_filter = ('date', 'area__disaster', 'area__province', 'area__municipality')
    search_fields = ('area__barangay__name',)

@admin.register(EarlyRecovery)
class EarlyRecoveryAdmin(admin.ModelAdmin):
    list_display = ('area', 'date_started', 'date_completed')
    list_filter = ('date_started', 'date_completed', 'area__disaster', 'area__province', 'area__municipality')
    search_fields = ('area__barangay__name', 'description')

@admin.register(DROMICReport)
class DROMICReportAdmin(admin.ModelAdmin):
    list_display = ('disaster', 'province', 'municipality', 'barangay', 'date', 'total_affected_families', 'total_affected_persons')
    list_filter = ('disaster', 'province', 'municipality', 'date')
    search_fields = ('disaster__name', 'province__name', 'municipality__name', 'barangay__name')
    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('affected_areas', 'displaced_populations', 'sex_age_distributions', 'sectoral_distributions', 'damaged_houses', 'relief_operations', 'early_recovery', 'families')
