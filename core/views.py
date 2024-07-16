from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from core.models import Disaster, AffectedArea, EvacuationCenter, DROMICReport,DamagedHouse
from django.shortcuts import render
from .export import generate_report_pdf



def dashboard(request):
    # You can add context data here, e.g., statistics for the dashboard
    context = {
        'total_disasters': 2,
        'affected_areas': 2,
        'evacuation_centers': 5,
        'affected_families': 68,
        'affected_persons': 1149,
        'displaced_population': 460,
    }
    return render(request, 'core/index.html', context)
from django.db.models import Sum
from .models import Disaster, AffectedArea, DisplacedPopulation, DamagedHouse, ReliefOperation, SexAgeDistribution, SectoralDistribution, DROMICReport

def overview(request):
    reports = DROMICReport.objects.all().order_by('-date')
    total_reports = reports.count()
    total_affected_families = sum(report.total_affected_families() for report in reports)
    total_affected_persons = sum(report.total_affected_persons() for report in reports)
    
    total_displaced = DisplacedPopulation.objects.aggregate(
        cum_families=Sum('cum_families'),
        now_families=Sum('now_families'),
        cum_persons=Sum('cum_persons'),
        now_persons=Sum('now_persons')
    )
    
    sex_age_distribution = SexAgeDistribution.objects.values('sex', 'age_group').annotate(
        cum_total=Sum('cum_count'),
        now_total=Sum('now_count')
    )
    
    sectoral_distribution = SectoralDistribution.objects.values('sector').annotate(
        cum_total=Sum('cum_count'),
        now_total=Sum('now_count')
    )
    
    damaged_houses = DamagedHouse.objects.aggregate(
        total_damaged=Sum('partially_damaged') + Sum('totally_damaged'),
        partially_damaged=Sum('partially_damaged'),
        totally_damaged=Sum('totally_damaged')
    )
    
    relief_operations = ReliefOperation.objects.aggregate(
        total_financial_assistance=Sum('financial_assistance'),
        total_food_items=Sum('food_items'),
        total_non_food_items=Sum('non_food_items')
    )
    
    context = {
        'reports': reports,
        'total_reports': total_reports,
        'total_affected_families': total_affected_families,
        'total_affected_persons': total_affected_persons,
        'total_displaced': total_displaced,
        'sex_age_distribution': sex_age_distribution,
        'sectoral_distribution': sectoral_distribution,
        'damaged_houses': damaged_houses,
        'relief_operations': relief_operations,
    }
    return render(request, 'core/overview.html', context)

@login_required
def disaster_info(request):
    return render(request, 'core/disaster_info.html')

@login_required
def affected_areas(request):
    return render(request, 'core/affected_areas.html')

@login_required
def evacuation_centers(request):
    return render(request, 'core/evacuation_centers.html')

# @login_required
# def reports(request):
#     return render(request, 'core/reports.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to your login page

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Disaster, DROMICReport, Province, Municipality, Barangay, DisplacedPopulation, ReliefOperation

@csrf_exempt
def save_report(request):
    if request.method == 'POST':
        try:
            disaster_name = request.POST.get('disaster')
            date = request.POST.get('date')
            province_name = request.POST.get('province')
            municipality_name = request.POST.get('municipality')
            barangay_name = request.POST.get('barangay')

            disaster, _ = Disaster.objects.get_or_create(name=disaster_name)
            province, _ = Province.objects.get_or_create(name=province_name)
            municipality, _ = Municipality.objects.get_or_create(name=municipality_name, province=province)
            barangay, _ = Barangay.objects.get_or_create(name=barangay_name, municipality=municipality)

            report = DROMICReport.objects.create(
                disaster=disaster,
                date=date,
                province=province,
                municipality=municipality,
                barangay=barangay
            )

            return JsonResponse({'status': 'success', 'message': 'Report saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def overview(request):
    disasters = Disaster.objects.all()
    affected_areas = AffectedArea.objects.all()
    displaced_populations = DisplacedPopulation.objects.all()
    damaged_houses = DamagedHouse.objects.all()
    relief_operations = ReliefOperation.objects.all()

    context = {
        'disasters': disasters,
        'affected_areas': affected_areas,
        'displaced_populations': displaced_populations,
        'damaged_houses': damaged_houses,
        'relief_operations': relief_operations,
    }
    return render(request, 'core/overview.html', context)

def disaster_list(request):
    disasters = Disaster.objects.all().prefetch_related(
        'affectedarea_set__displacedpopulation_set',
        'affectedarea_set__damagedhouse_set',
        'affectedarea_set__reliefoperation_set',
        'affectedarea_set__earlyrecovery_set'
    )
    return render(request, 'core/disaster.html', {'disasters': disasters})


def add_affected_area(request):
    if request.method == 'POST':
        disaster_id = request.POST.get('disaster')
        province_id = request.POST.get('province')
        municipality_id = request.POST.get('municipality')
        barangay_id = request.POST.get('barangay')
        affected_families = request.POST.get('affected_families')
        affected_persons = request.POST.get('affected_persons')

        disaster = Disaster.objects.get(id=disaster_id)
        province = Province.objects.get(id=province_id)
        municipality = Municipality.objects.get(id=municipality_id)
        barangay = Barangay.objects.get(id=barangay_id)

        AffectedArea.objects.create(
            disaster=disaster,
            province=province,
            municipality=municipality,
            barangay=barangay,
            affected_families=affected_families,
            affected_persons=affected_persons
        )

        return redirect('core:disaster_list')

    # If it's a GET request, return JSON data for dropdowns
    provinces = Province.objects.all()
    municipalities = Municipality.objects.all()
    barangays = Barangay.objects.all()

    return JsonResponse({
        'provinces': list(provinces.values('id', 'name')),
        'municipalities': list(municipalities.values('id', 'name', 'province_id')),
        'barangays': list(barangays.values('id', 'name', 'municipality_id')),
    })



from django.shortcuts import render, redirect
from django.http import JsonResponse
from .models import AffectedArea, Province, Municipality, Barangay, Disaster
from django.views.decorators.http import require_POST

def affected_area_list(request):
    affected_areas = AffectedArea.objects.all()
    total_affected_areas = affected_areas.count()
    total_affected_families = sum(area.affected_families for area in affected_areas)
    total_affected_persons = sum(area.affected_persons for area in affected_areas)
    
    context = {
        'affected_areas': affected_areas,
        'total_affected_areas': total_affected_areas,
        'total_affected_families': total_affected_families,
        'total_affected_persons': total_affected_persons,
    }
    return render(request, 'core/affected_area.html', context)



def evacuation_center_list(request):
    evacuation_centers = EvacuationCenter.objects.all()
    total_centers = evacuation_centers.count()
    total_capacity = sum(center.capacity for center in evacuation_centers)
    total_occupancy = sum(center.current_occupancy for center in evacuation_centers)
    
    context = {
        'evacuation_centers': evacuation_centers,
        'total_centers': total_centers,
        'total_capacity': total_capacity,
        'total_occupancy': total_occupancy,
    }
    return render(request, 'core/evacuation.html', context)


from django.shortcuts import render
from .models import DROMICReport

from django.db.models import Sum
from .models import DROMICReport, DisplacedPopulation, SexAgeDistribution, SectoralDistribution, DamagedHouse, ReliefOperation

def report_list(request):
    reports = DROMICReport.objects.all().order_by('-date')
    total_reports = reports.count()
    total_affected_families = sum(report.total_affected_families() for report in reports)
    total_affected_persons = sum(report.total_affected_persons() for report in reports)
    
    total_displaced = DisplacedPopulation.objects.aggregate(
        cum_families=Sum('cum_families'),
        now_families=Sum('now_families'),
        cum_persons=Sum('cum_persons'),
        now_persons=Sum('now_persons')
    )
    
    sex_age_distribution = SexAgeDistribution.objects.values('sex', 'age_group').annotate(
        cum_total=Sum('cum_count'),
        now_total=Sum('now_count')
    )
    
    sectoral_distribution = SectoralDistribution.objects.values('sector').annotate(
        cum_total=Sum('cum_count'),
        now_total=Sum('now_count')
    )
    
    damaged_houses = DamagedHouse.objects.aggregate(
        total_damaged=Sum('partially_damaged') + Sum('totally_damaged'),
        partially_damaged=Sum('partially_damaged'),
        totally_damaged=Sum('totally_damaged')
    )
    
    relief_operations = ReliefOperation.objects.aggregate(
        total_financial_assistance=Sum('financial_assistance'),
        total_food_items=Sum('food_items'),
        total_non_food_items=Sum('non_food_items')
    )

    
    context = {
        'reports': reports,
        'total_reports': total_reports,
        'total_affected_families': total_affected_families,
        'total_affected_persons': total_affected_persons,
        'total_displaced': total_displaced,
        'sex_age_distribution': sex_age_distribution,
        'sectoral_distribution': sectoral_distribution,
        'damaged_houses': damaged_houses,
        'relief_operations': relief_operations,
    }
    return render(request, 'core/reports.html', context)

def report_detail(request, report_id):
    report = DROMICReport.objects.get(id=report_id)
    context = {
        'report': report,
    }
    return render(request, 'core/report_detail.html', context)

from django.http import HttpResponse





def export_report_pdf(request, report_id):
    report = DROMICReport.objects.get(id=report_id)
    pdf_buffer = generate_report_pdf(report)
    return HttpResponse(pdf_buffer, content_type='application/pdf')
