from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, F
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Disaster, AffectedArea, EvacuationCenter, DROMICReport,
    DamagedHouse, DisplacedPopulation, SexAgeDistribution,
    SectoralDistribution, ReliefOperation, Province, Municipality, Barangay, Family, FamilyMember
)
from .export import generate_report_pdf
from django.db.models.functions import TruncDate

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('dashboard')  # Replace 'home' with your main page URL name
        else:
            # Add an error message
            pass
    return render(request, 'core/login.html')

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('login')
    else:
        form = UserCreationForm()
    return render(request, 'core/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('index')

@login_required
def dashboard(request):
    total_disasters = Disaster.objects.count()
    affected_areas = AffectedArea.objects.count()
    evacuation_centers = EvacuationCenter.objects.count()
    total_reports = DROMICReport.objects.count()

    disaster_types = list(Disaster.objects.values('name').annotate(count=Count('id')))

    affected_data = AffectedArea.objects.annotate(
    date=F('disaster__date_occurred')
    ).values('date').annotate(
        families=Sum('affected_families'),
        persons=Sum('affected_persons')
    ).order_by('date')


    context = {
    'total_disasters': total_disasters,
    'affected_areas': affected_areas,
    'evacuation_centers': evacuation_centers,
    'total_reports': total_reports,
    'disaster_types': json.dumps(list(disaster_types)),
    'affected_data': json.dumps(list(affected_data), default=str),
    }
    return render(request, 'core/dashboard.html', context)


def index(request):
    active_disasters_count = Disaster.objects.filter(date_occurred__gte=timezone.now() - timedelta(days=30)).count()
    total_affected_persons = AffectedArea.objects.aggregate(Sum('affected_persons'))['affected_persons__sum']
    evacuation_centers_count = EvacuationCenter.objects.count()
    recent_updates = DROMICReport.objects.order_by('-date')[:3]
    affected_areas = AffectedArea.objects.all() 
    barangays = Barangay.objects.all()# You might want to filter this for Mindanao only

    context = {
        'active_disasters_count': active_disasters_count,
        'total_affected_persons': total_affected_persons,
        'evacuation_centers_count': evacuation_centers_count,
        'recent_updates': recent_updates,
        'affected_areas': affected_areas,
        'barangays': barangays,
    }
    return render(request, 'core/index.html', context)

@require_POST
def add_evacuation_center(request):
    try:
        name = request.POST.get('name')
        province_id = request.POST.get('province')
        municipality_id = request.POST.get('municipality')
        barangay_id = request.POST.get('barangay')
        capacity = int(request.POST.get('capacity'))
        current_occupancy = int(request.POST.get('current_occupancy'))

        EvacuationCenter.objects.create(
            name=name,
            province_id=province_id,
            municipality_id=municipality_id,
            barangay_id=barangay_id,
            capacity=capacity,
            current_occupancy=current_occupancy
        )

        return JsonResponse({'status': 'success', 'message': 'Evacuation center added successfully.'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


@csrf_exempt
def save_report(request):
    if request.method == 'POST':
        try:
            data = request.POST
            disaster, _ = Disaster.objects.get_or_create(name=data.get('disaster'))
            province, _ = Province.objects.get_or_create(name=data.get('province'))
            municipality, _ = Municipality.objects.get_or_create(name=data.get('municipality'), province=province)
            barangay, _ = Barangay.objects.get_or_create(name=data.get('barangay'), municipality=municipality)

            DROMICReport.objects.create(
                disaster=disaster,
                date=data.get('date'),
                province=province,
                municipality=municipality,
                barangay=barangay
            )
            return JsonResponse({'status': 'success', 'message': 'Report saved successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@login_required
def overview(request):
    reports = DROMICReport.objects.all().order_by('-date')
    context = {
        'total_reports': reports.count(),
        'total_affected_families': sum(report.total_affected_families() for report in reports),
        'total_affected_persons': sum(report.total_affected_persons() for report in reports),
        'displaced_population': DisplacedPopulation.objects.aggregate(
            cum_families=Sum('cum_families'),
            now_families=Sum('now_families'),
            cum_persons=Sum('cum_persons'),
            now_persons=Sum('now_persons')
        ),
        'sex_age_distribution': SexAgeDistribution.objects.values('sex', 'age_group').annotate(
            cum_total=Sum('cum_count'),
            now_total=Sum('now_count')
        ),
        'sectoral_distribution': SectoralDistribution.objects.values('sector').annotate(
            cum_total=Sum('cum_count'),
            now_total=Sum('now_count')
        ),
        'damaged_houses_summary': DamagedHouse.objects.aggregate(
            total_damaged=Sum('partially_damaged') + Sum('totally_damaged'),
            partially_damaged=Sum('partially_damaged'),
            totally_damaged=Sum('totally_damaged')
        ),
        'relief_summary': ReliefOperation.objects.aggregate(
            total_financial_assistance=Sum('financial_assistance'),
            total_food_items=Sum('food_items'),
            total_non_food_items=Sum('non_food_items')
        ),
        'total_disasters': Disaster.objects.count(),
        'total_affected_areas': AffectedArea.objects.count(),
    }
    return render(request, 'core/overview.html', context)


def affected_area_list(request):
    affected_areas = AffectedArea.objects.all()
    disasters = Disaster.objects.all()
    provinces = Province.objects.all()
    context = {
        'affected_areas': affected_areas,
        'disasters': disasters,
        'provinces': provinces,
        'total_affected_areas': affected_areas.count(),
        'total_affected_families': sum(area.affected_families for area in affected_areas),
        'total_affected_persons': sum(area.affected_persons for area in affected_areas),
    }
    return render(request, 'core/affected_area.html', context)

@csrf_exempt
def create_disaster(request):
    if request.method == 'POST':
        try:
            data = request.POST
            disaster = Disaster.objects.create(
                name=data['name'],
                description=data['description'],
                date_occurred=data['date_occurred']
            )
            return JsonResponse({'status': 'success', 'id': disaster.id, 'name': disaster.name})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
@require_POST
def delete_disaster(request, disaster_id):
    try:
        disaster = get_object_or_404(Disaster, id=disaster_id)
        disaster.delete()
        return JsonResponse({'status': 'success', 'message': 'Disaster deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
@require_POST
def bulk_delete_disasters(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        if not ids:
            return JsonResponse({'status': 'error', 'message': 'No disasters selected'})
        deleted_count, _ = Disaster.objects.filter(id__in=ids).delete()
        return JsonResponse({'status': 'success', 'message': f'{deleted_count} disaster(s) deleted successfully', 'deleted_count': deleted_count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
def create_province(request):
    if request.method == 'POST':
        try:
            data = request.POST
            province = Province.objects.create(name=data['name'])
            return JsonResponse({'status': 'success', 'id': province.id, 'name': province.name})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
@csrf_exempt
def create_municipality(request):
    if request.method == 'POST':
        try:
            data = request.POST
            province = Province.objects.get(id=data['province'])
            municipality = Municipality.objects.create(name=data['name'], province=province)
            return JsonResponse({'status': 'success', 'id': municipality.id, 'name': municipality.name})
        except Province.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invalid province selected'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

@csrf_exempt
def create_barangay(request):
    if request.method == 'POST':
        try:
            data = request.POST
            municipality = Municipality.objects.get(id=data['municipality'])
            barangay = Barangay.objects.create(name=data['name'], municipality=municipality)
            return JsonResponse({'status': 'success', 'id': barangay.id, 'name': barangay.name})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

# Update the existing add_affected_area view
@csrf_exempt
@require_POST
def add_affected_area(request):
    try:
        data = request.POST
        disaster = get_or_create_instance(Disaster, data.get('disaster'), data.get('new_disaster'))
        province = get_or_create_instance(Province, data.get('province'), data.get('new_province'))
        municipality = get_or_create_instance(Municipality, data.get('municipality'), data.get('new_municipality'), province=province)
        barangay = get_or_create_instance(Barangay, data.get('barangay'), data.get('new_barangay'), municipality=municipality)
        
        affected_area = AffectedArea.objects.create(
            disaster=disaster,
            province=province,
            municipality=municipality,
            barangay=barangay,
            affected_families=data.get('affected_families'),
            affected_persons=data.get('affected_persons')
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Affected area added successfully',
            'area_id': affected_area.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_affected_areas(request):
    areas = AffectedArea.objects.all().select_related('disaster', 'province', 'municipality', 'barangay')
    data = []
    for a in areas:
        data.append({
            'id': a.id,
            'disaster': a.disaster.name if a.disaster else '',
            'province': a.province.name if a.province else '',
            'municipality': a.municipality.name if a.municipality else '',
            'barangay': a.barangay.name if a.barangay else '',
            'affected_families': a.affected_families,
            'affected_persons': a.affected_persons,
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def delete_affected_area(request, area_id):
    try:
        area = get_object_or_404(AffectedArea, id=area_id)
        area.delete()
        return JsonResponse({'status': 'success', 'message': 'Affected area deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
@require_POST
def bulk_delete_affected_areas(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        if not ids:
            return JsonResponse({'status': 'error', 'message': 'No areas selected'})
        deleted_count, _ = AffectedArea.objects.filter(id__in=ids).delete()
        return JsonResponse({'status': 'success', 'message': f'{deleted_count} area(s) deleted', 'deleted_count': deleted_count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})


def evacuation_center_list(request):
    evacuation_centers = EvacuationCenter.objects.all().select_related('province', 'municipality', 'barangay')
    provinces = Province.objects.all()
    
    context = {
        'evacuation_centers': evacuation_centers,
        'provinces': provinces,
        'total_centers': evacuation_centers.count(),
        'total_capacity': evacuation_centers.aggregate(Sum('capacity'))['capacity__sum'] or 0,
        'total_occupied': evacuation_centers.aggregate(Sum('current_occupancy'))['current_occupancy__sum'] or 0,
    }
    
    return render(request, 'core/evacuation_centers.html', context)

def get_evacuation_centers(request):
    centers = EvacuationCenter.objects.all().select_related('province', 'municipality', 'barangay')
    data = []
    for c in centers:
        data.append({
            'id': c.id,
            'name': c.name,
            'province': c.province.name if c.province else '',
            'municipality': c.municipality.name if c.municipality else '',
            'barangay': c.barangay.name if c.barangay else '',
            'capacity': c.capacity,
            'current_occupancy': c.current_occupancy,
            'available': c.capacity - c.current_occupancy,
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def delete_evacuation_center(request, center_id):
    try:
        center = get_object_or_404(EvacuationCenter, id=center_id)
        center.delete()
        return JsonResponse({'status': 'success', 'message': 'Evacuation center deleted successfully'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
@require_POST
def bulk_delete_evacuation_centers(request):
    try:
        data = json.loads(request.body)
        ids = data.get('ids', [])
        if not ids:
            return JsonResponse({'status': 'error', 'message': 'No centers selected'})
        deleted_count, _ = EvacuationCenter.objects.filter(id__in=ids).delete()
        return JsonResponse({'status': 'success', 'message': f'{deleted_count} center(s) deleted', 'deleted_count': deleted_count})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

def get_municipalities(request):
    province_id = request.GET.get('province_id')
    municipalities = Municipality.objects.filter(province_id=province_id).values('id', 'name')
    return JsonResponse({'municipalities': list(municipalities)})

def get_barangays(request):
    municipality_id = request.GET.get('municipality_id')
    barangays = Barangay.objects.filter(municipality_id=municipality_id).values('id', 'name')
    return JsonResponse({'barangays': list(barangays)})

def get_or_create_instance(model, instance_id, new_name, **kwargs):
    if instance_id == 'new':
        return model.objects.create(name=new_name, **kwargs)
    return model.objects.get(id=instance_id)

def disaster_impact(request):
    """Comprehensive disaster impact page with real data from all models."""
    from django.db.models import Sum, Count

    # Family members
    family_members = FamilyMember.objects.all().select_related('family', 'family__area')
    total_members = family_members.count()
    total_displaced_members = family_members.filter(is_displaced=True).count()
    total_in_evac = family_members.filter(is_in_evacuation_center=True).count()

    # Displaced population
    displaced_all = DisplacedPopulation.objects.all().select_related('area', 'evacuation_center')
    displaced_stats = displaced_all.aggregate(
        cum_families=Sum('cum_families'),
        now_families=Sum('now_families'),
        cum_persons=Sum('cum_persons'),
        now_persons=Sum('now_persons'),
    )
    total_displaced = {
        'cum_families': displaced_stats['cum_families'] or 0,
        'now_families': displaced_stats['now_families'] or 0,
        'cum_persons': displaced_stats['cum_persons'] or 0,
        'now_persons': displaced_stats['now_persons'] or 0,
    }

    # Sex and age distribution
    sex_age_distributions = SexAgeDistribution.objects.all().select_related('population')

    # Sectoral distribution
    sectoral_distributions = SectoralDistribution.objects.all().select_related('population')

    # Damaged houses
    damaged_all = DamagedHouse.objects.all()
    damaged_stats = damaged_all.aggregate(
        total_partially=Sum('partially_damaged'),
        total_totally=Sum('totally_damaged'),
    )
    damaged_houses = {
        'total_partially': damaged_stats['total_partially'] or 0,
        'total_totally': damaged_stats['total_totally'] or 0,
        'total_damaged': (damaged_stats['total_partially'] or 0) + (damaged_stats['total_totally'] or 0),
    }

    # Relief operations
    relief_all = ReliefOperation.objects.all()
    relief_stats = relief_all.aggregate(
        total_food=Sum('food_items'),
        total_non_food=Sum('non_food_items'),
        total_financial=Sum('financial_assistance'),
    )
    relief_operations = {
        'total_food': relief_stats['total_food'] or 0,
        'total_non_food': relief_stats['total_non_food'] or 0,
        'total_financial': float(relief_stats['total_financial'] or 0),
        'total_operations': relief_all.count(),
    }

    # Early recovery
    from .models import EarlyRecovery
    early_recoveries = EarlyRecovery.objects.all().select_related('area')

    # Evacuation centers
    evac_centers = EvacuationCenter.objects.all()
    evac_stats = evac_centers.aggregate(
        total_capacity=Sum('capacity'),
        total_occupied=Sum('current_occupancy'),
    )

    # Affected areas
    affected_areas = AffectedArea.objects.all().select_related('disaster', 'province', 'municipality', 'barangay')
    area_stats = affected_areas.aggregate(
        total_families=Sum('affected_families'),
        total_persons=Sum('affected_persons'),
    )

    # Disasters for context
    disasters = Disaster.objects.all()

    context = {
        'family_members': family_members,
        'total_members': total_members,
        'total_displaced_members': total_displaced_members,
        'total_in_evac': total_in_evac,
        'displaced_populations': displaced_all,
        'total_displaced': total_displaced,
        'sex_age_distributions': sex_age_distributions,
        'sectoral_distributions': sectoral_distributions,
        'damaged_houses_list': damaged_all,
        'damaged_houses': damaged_houses,
        'relief_operations_list': relief_all,
        'relief_operations': relief_operations,
        'early_recoveries': early_recoveries,
        'evac_centers_count': evac_centers.count(),
        'evac_capacity': evac_stats['total_capacity'] or 0,
        'evac_occupied': evac_stats['total_occupied'] or 0,
        'total_affected_areas': affected_areas.count(),
        'total_affected_families': area_stats['total_families'] or 0,
        'total_affected_persons': area_stats['total_persons'] or 0,
        'total_disasters': disasters.count(),
        'disasters': disasters,
        'affected_areas': affected_areas,
    }
    return render(request, 'core/disaster_impact.html', context)


def report_list(request):
    report_create= DROMICReport.objects.all().select_related('province', 'municipality', 'barangay')
    reports = DROMICReport.objects.all().order_by('-date')
    context = {
        'reports': reports,
        'total_reports': reports.count(),
        'total_affected_families': sum(report.total_affected_families() for report in reports),
        'total_affected_persons': sum(report.total_affected_persons() for report in reports),
        'total_displaced': DisplacedPopulation.objects.aggregate(
            cum_families=Sum('cum_families'),
            now_families=Sum('now_families'),
            cum_persons=Sum('cum_persons'),
            now_persons=Sum('now_persons')
        ),
        'sex_age_distribution': SexAgeDistribution.objects.values('sex', 'age_group').annotate(
            cum_total=Sum('cum_count'),
            now_total=Sum('now_count')
        ),
        'sectoral_distribution': SectoralDistribution.objects.values('sector').annotate(
            cum_total=Sum('cum_count'),
            now_total=Sum('now_count')
        ),
        'damaged_houses': DamagedHouse.objects.aggregate(
            total_damaged=Sum('partially_damaged') + Sum('totally_damaged'),
            partially_damaged=Sum('partially_damaged'),
            totally_damaged=Sum('totally_damaged')
        ),
        'relief_operations': ReliefOperation.objects.aggregate(
            total_financial_assistance=Sum('financial_assistance'),
            total_food_items=Sum('food_items'),
            total_non_food_items=Sum('non_food_items')
        ),
    }
    return render(request, 'core/reports.html', context)


def report_detail(request, report_id):
    report = get_object_or_404(DROMICReport, id=report_id)
    context = {
        'report': report,
    }
    return render(request, 'core/report_detail.html', context)


def export_report_pdf(request, report_id):
    report = get_object_or_404(DROMICReport, id=report_id)
    pdf_buffer = generate_report_pdf(report)
    return HttpResponse(pdf_buffer, content_type='application/pdf')



def disaster_info(request):
    disasters = Disaster.objects.all().order_by('-date_occurred')
    return render(request, 'core/disaster_info.html', {'disasters': disasters})


def get_disasters(request):
    disasters = Disaster.objects.all().values('id', 'name', 'description', 'date_occurred')
    return JsonResponse(list(disasters), safe=False)


# Disaster impact
from django.template.loader import render_to_string
def add_family_member(request):
    if request.method == 'POST':
        # Process form data and save to database
        FamilyMember.objects.create(
            name=request.POST.get('name'),
            age=request.POST.get('age'),
            gender=request.POST.get('gender'),
            relationship_to_head=request.POST.get('relationship')
        )
        family_members = FamilyMember.objects.all()
        html_content = render_to_string('core/partials/family_members.html', {'family_members': family_members})
        return JsonResponse({'status': 'success', 'content': html_content})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})

def add_displaced_population(request):
    if request.method == 'POST':
        DisplacedPopulation.objects.create(
            area=request.POST.get('area'),
            evacuation_center=request.POST.get('evacuationCenter'),
            cum_families=request.POST.get('cumFamilies'),
            now_families=request.POST.get('nowFamilies')
        )
        displaced_population = DisplacedPopulation.objects.all()
        html_content = render_to_string('core/partials/displaced_population.html', {'displaced_population': displaced_population})
        return JsonResponse({'status': 'success', 'content': html_content})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})


def report_list(request):
    """Comprehensive reports dashboard with real data from all models."""
    # Affected areas data
    affected_areas = AffectedArea.objects.all().select_related('disaster', 'province', 'municipality', 'barangay')
    total_affected_families = affected_areas.aggregate(total=Sum('affected_families'))['total'] or 0
    total_affected_persons = affected_areas.aggregate(total=Sum('affected_persons'))['total'] or 0

    # Disasters
    disasters = Disaster.objects.all()

    # Evacuation centers
    evacuation_centers = EvacuationCenter.objects.all()
    total_centers = evacuation_centers.count()
    total_capacity = evacuation_centers.aggregate(total=Sum('capacity'))['total'] or 0
    total_occupancy = evacuation_centers.aggregate(total=Sum('current_occupancy'))['total'] or 0

    # Displaced population
    displaced = DisplacedPopulation.objects.all()
    displaced_stats = displaced.aggregate(
        cum_families=Sum('cum_families'),
        now_families=Sum('now_families'),
        cum_persons=Sum('cum_persons'),
        now_persons=Sum('now_persons'),
    )
    total_displaced = {
        'cum_families': displaced_stats['cum_families'] or 0,
        'now_families': displaced_stats['now_families'] or 0,
        'cum_persons': displaced_stats['cum_persons'] or 0,
        'now_persons': displaced_stats['now_persons'] or 0,
    }

    # Sex and age distribution
    sex_age_data = SexAgeDistribution.objects.values('sex', 'age_group').annotate(
        cum_total=Sum('cum_count'),
        now_total=Sum('now_count'),
    ).order_by('sex', 'age_group')

    # Sectoral distribution
    sectoral_data = SectoralDistribution.objects.values('sector').annotate(
        cum_total=Sum('cum_count'),
        now_total=Sum('now_count'),
    ).order_by('sector')

    # Damaged houses
    damaged_stats = DamagedHouse.objects.aggregate(
        total_partially=Sum('partially_damaged'),
        total_totally=Sum('totally_damaged'),
    )
    damaged_houses = {
        'total_partially': damaged_stats['total_partially'] or 0,
        'total_totally': damaged_stats['total_totally'] or 0,
        'total_damaged': (damaged_stats['total_partially'] or 0) + (damaged_stats['total_totally'] or 0),
    }

    # Relief operations
    relief_stats = ReliefOperation.objects.aggregate(
        total_food=Sum('food_items'),
        total_non_food=Sum('non_food_items'),
        total_financial=Sum('financial_assistance'),
    )
    relief_operations = {
        'total_food': relief_stats['total_food'] or 0,
        'total_non_food': relief_stats['total_non_food'] or 0,
        'total_financial': float(relief_stats['total_financial'] or 0),
    }

    # Per-disaster breakdown for charts
    disaster_breakdown = []
    for d in disasters:
        areas = AffectedArea.objects.filter(disaster=d)
        families = areas.aggregate(total=Sum('affected_families'))['total'] or 0
        persons = areas.aggregate(total=Sum('affected_persons'))['total'] or 0
        disaster_breakdown.append({
            'name': d.name,
            'families': families,
            'persons': persons,
        })

    # Reports list
    reports = DROMICReport.objects.all().select_related(
        'disaster', 'province', 'municipality', 'barangay'
    ).order_by('-date')

    # Provinces for the create modal
    provinces = Province.objects.all()

    context = {
        'total_disasters': disasters.count(),
        'total_affected_areas': affected_areas.count(),
        'total_affected_families': total_affected_families,
        'total_affected_persons': total_affected_persons,
        'total_centers': total_centers,
        'total_capacity': total_capacity,
        'total_occupancy': total_occupancy,
        'total_displaced': total_displaced,
        'sex_age_distribution': list(sex_age_data),
        'sectoral_distribution': list(sectoral_data),
        'damaged_houses': damaged_houses,
        'relief_operations': relief_operations,
        'disaster_breakdown': disaster_breakdown,
        'reports': reports,
        'total_reports': reports.count(),
        'disasters': disasters,
        'provinces': provinces,
    }
    return render(request, 'core/reports.html', context)


def report_detail(request, report_id):
    """View a single DROMIC report."""
    report = get_object_or_404(DROMICReport, id=report_id)
    context = {
        'report': report,
        'affected_areas': report.affected_areas.all(),
        'displaced_populations': report.displaced_populations.all(),
        'damaged_houses': report.damaged_houses.all(),
        'relief_operations': report.relief_operations.all(),
    }
    return render(request, 'core/report_detail.html', context)


def export_report_pdf(request, report_id):
    """Export a DROMIC report as a text file (PDF generation placeholder)."""
    report = get_object_or_404(DROMICReport, id=report_id)
    content = f"DROMIC Report\n"
    content += f"Disaster: {report.disaster.name}\n"
    content += f"Location: {report.barangay.name}, {report.municipality.name}, {report.province.name}\n"
    content += f"Date: {report.date}\n\n"

    areas = report.affected_areas.all()
    content += f"Affected Areas: {areas.count()}\n"
    for area in areas:
        content += f"  - {area.barangay.name}: {area.affected_families} families, {area.affected_persons} persons\n"

    response = HttpResponse(content, content_type='text/plain')
    response['Content-Disposition'] = f'attachment; filename="dromic_report_{report_id}.txt"'
    return response


@csrf_exempt
@require_POST
def save_report(request):
    """Create a new DROMIC report."""
    try:
        report = DROMICReport.objects.create(
            disaster_id=request.POST.get('disaster'),
            province_id=request.POST.get('province'),
            municipality_id=request.POST.get('municipality'),
            barangay_id=request.POST.get('barangay'),
            date=request.POST.get('date'),
        )
        return JsonResponse({
            'status': 'success',
            'message': 'Report created successfully',
            'report_id': report.id
        })
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
