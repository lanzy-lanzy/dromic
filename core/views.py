from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import logout, login, authenticate
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.db.models import Sum, Count, F, Case, When, Value, CharField
from django.db import models
from django.utils import timezone
from datetime import timedelta
import json
from django.contrib.auth.forms import UserCreationForm
from .models import (
    Disaster, AffectedArea, EvacuationCenter, DROMICReport,
    DamagedHouse, DisplacedPopulation, SexAgeDistribution,
    SectoralDistribution, ReliefOperation, Province, Municipality, Barangay, Family, FamilyMember,
    FamilyDistribution
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
        'displaced_population': {
            'cum_families': 0,
            'now_families': FamilyMember.objects.filter(is_displaced=True).values('family').distinct().count(),
            'cum_persons': 0,
            'now_persons': FamilyMember.objects.filter(is_displaced=True).count()
        },
        'sex_age_distribution': [
             {'sex': m['gender'], 'age_group': m['age_group'], 'now_total': m['now_total']} 
             for m in FamilyMember.objects.values('gender').annotate(
                 age_group=Case(
                     When(age__lt=1, then=Value('Infant')),
                     When(age__gte=1, age__lte=2, then=Value('Toddler')),
                     When(age__gte=3, age__lte=5, then=Value('Preschool')),
                     When(age__gte=6, age__lte=12, then=Value('School Age')),
                     When(age__gte=13, age__lte=17, then=Value('Teenage')),
                     When(age__gte=18, age__lte=59, then=Value('Adult')),
                     default=Value('Senior Citizen'),
                     output_field=models.CharField()
                 )
             ).values('gender', 'age_group').annotate(now_total=Count('id'))
        ],
        'sectoral_distribution': FamilyMember.objects.exclude(sector='').values('sector').annotate(now_total=Count('id')),
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
    from django.db.models import Sum, Count, Case, When, Value

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
    sex_age_distributions = [
             {'sex': m['gender'], 'age_group': m['age_group'], 'now_total': m['now_total']} 
             for m in FamilyMember.objects.values('gender').annotate(
                 age_group=Case(
                     When(age__lt=1, then=Value('Infant')),
                     When(age__gte=1, age__lte=2, then=Value('Toddler')),
                     When(age__gte=3, age__lte=5, then=Value('Preschool')),
                     When(age__gte=6, age__lte=12, then=Value('School Age')),
                     When(age__gte=13, age__lte=17, then=Value('Teenage')),
                     When(age__gte=18, age__lte=59, then=Value('Adult')),
                     default=Value('Senior Citizen'),
                     output_field=models.CharField()
                 )
             ).values('gender', 'age_group').annotate(now_total=Count('id'))
        ]

    # Sectoral distribution
    sectoral_distributions = FamilyMember.objects.exclude(sector='').values('sector').annotate(now_total=Count('id'))

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
        'total_displaced': {
            'cum_families': 0,
            'now_families': FamilyMember.objects.filter(is_displaced=True).values('family').distinct().count(),
            'cum_persons': 0,
            'now_persons': FamilyMember.objects.filter(is_displaced=True).count()
        },
        'sex_age_distribution': [
             {'sex': m['gender'], 'age_group': m['age_group'], 'now_total': m['now_total']} 
             for m in FamilyMember.objects.values('gender').annotate(
                 age_group=Case(
                     When(age__lt=1, then=Value('Infant')),
                     When(age__gte=1, age__lte=2, then=Value('Toddler')),
                     When(age__gte=3, age__lte=5, then=Value('Preschool')),
                     When(age__gte=6, age__lte=12, then=Value('School Age')),
                     When(age__gte=13, age__lte=17, then=Value('Teenage')),
                     When(age__gte=18, age__lte=59, then=Value('Adult')),
                     default=Value('Senior Citizen'),
                     output_field=models.CharField()
                 )
             ).values('gender', 'age_group').annotate(now_total=Count('id'))
        ],
        'sectoral_distribution': FamilyMember.objects.exclude(sector='').values('sector').annotate(now_total=Count('id')),
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


from django.utils.text import slugify
def export_report_pdf(request, report_id):
    report = get_object_or_404(DROMICReport, id=report_id)
    pdf_buffer = generate_report_pdf(report)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    
    safe_location = slugify(f"{report.barangay.name}_{report.municipality.name}")
    filename = f"DROMIC_Report_{safe_location}_{report.date.strftime('%Y%m%d')}.pdf"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response



def disaster_info(request):
    disasters = Disaster.objects.all().order_by('-date_occurred')
    return render(request, 'core/disaster_info.html', {'disasters': disasters})


# ----------------------------------------------------------------------
# Relief Operations Views
# ----------------------------------------------------------------------

def relief_operations_view(request):
    """View to manage Relief Operations."""
    areas = AffectedArea.objects.all().select_related('disaster', 'province', 'municipality', 'barangay')
    return render(request, 'core/relief_operations.html', {'areas': areas})

def get_relief_operations(request):
    """API to fetch all relief operations."""
    ops = ReliefOperation.objects.all().select_related(
        'area__disaster', 'area__province', 'area__municipality', 'area__barangay'
    ).order_by('-date')
    
    data = []
    for op in ops:
        area_str = f"{op.area.barangay.name}, {op.area.municipality.name}, {op.area.province.name}" if op.area.barangay else f"{op.area.municipality.name}, {op.area.province.name}"
        data.append({
            'id': op.id,
            'date': op.date.strftime('%b. %d, %Y'),
            'disaster': op.area.disaster.name,
            'area': area_str,
            'food_items': op.food_items,
            'non_food_items': op.non_food_items,
            'financial_assistance': float(op.financial_assistance)
        })
    return JsonResponse(data, safe=False)

def add_relief_operation(request):
    """API to add a new relief operation."""
    if request.method == 'POST':
        try:
            area_id = request.POST.get('area')
            area = get_object_or_404(AffectedArea, id=area_id)
            
            ReliefOperation.objects.create(
                area=area,
                date=request.POST.get('date'),
                food_items=request.POST.get('food_items', 0) or 0,
                non_food_items=request.POST.get('non_food_items', 0) or 0,
                financial_assistance=request.POST.get('financial_assistance', 0) or 0
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def delete_relief_operation(request, op_id):
    """API to delete a relief operation."""
    if request.method == 'POST':
        try:
            op = get_object_or_404(ReliefOperation, id=op_id)
            op.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def relief_operation_distribution_view(request, op_id):
    """View to manage family distribution for a specific operation."""
    op = get_object_or_404(ReliefOperation, id=op_id)
    return render(request, 'core/relief_distribution.html', {'operation': op})

def get_distribution_families(request, op_id):
    """API to fetch families and their distribution status for a specific operation."""
    op = get_object_or_404(ReliefOperation, id=op_id)
    # Get all families in the affected area of this operation
    families = Family.objects.filter(area=op.area).order_by('head_of_family')
    
    # Get distribution records for these families in this operation
    distributions = {d.family.id: d for d in FamilyDistribution.objects.filter(operation=op)}
    
    data = []
    for f in families:
        dist = distributions.get(f.id)
        is_received = dist.is_received if dist else False
        data.append({
            'id': f.id,
            'head_of_family': f.head_of_family,
            'number_of_members': f.number_of_members,
            'is_received': is_received
        })
    return JsonResponse(data, safe=False)

import json
def toggle_family_distribution(request, op_id):
    """API to toggle the received status for a specific family in an operation."""
    if request.method == 'POST':
        try:
            op = get_object_or_404(ReliefOperation, id=op_id)
            data = json.loads(request.body)
            family_id = data.get('family_id')
            is_received = data.get('is_received', False)
            
            family = get_object_or_404(Family, id=family_id, area=op.area)
            
            # Update or create the distribution record
            dist, created = FamilyDistribution.objects.update_or_create(
                operation=op, family=family,
                defaults={'is_received': is_received}
            )
            return JsonResponse({'status': 'success', 'is_received': dist.is_received})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

from .export import generate_rds_pdf
from django.utils.text import slugify
def export_rds_pdf(request, op_id):
    """View to export the Relief Distribution Sheet (RDS) as PDF."""
    op = get_object_or_404(ReliefOperation, id=op_id)
    pdf_buffer = generate_rds_pdf(op)
    response = HttpResponse(pdf_buffer.getvalue(), content_type='application/pdf')
    
    safe_disaster_name = slugify(op.area.disaster.name)
    filename = f"RDS_{safe_disaster_name}_{op.date.strftime('%Y%m%d')}.pdf"
    
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response

# ----------------------------------------------------------------------
# Early Recovery Views
# ----------------------------------------------------------------------

def early_recovery_view(request):
    """View to manage Early Recovery Activities."""
    areas = AffectedArea.objects.all().select_related('disaster', 'province', 'municipality', 'barangay')
    return render(request, 'core/early_recovery.html', {'areas': areas})

def get_early_recoveries(request):
    """API to fetch all early recovery activities."""
    recoveries = EarlyRecovery.objects.all().select_related(
        'area__disaster', 'area__province', 'area__municipality', 'area__barangay'
    ).order_by('-date_started')
    
    data = []
    for r in recoveries:
        area_str = f"{r.area.barangay.name}, {r.area.municipality.name}, {r.area.province.name}" if r.area.barangay else f"{r.area.municipality.name}, {r.area.province.name}"
        data.append({
            'id': r.id,
            'disaster': r.area.disaster.name,
            'area': area_str,
            'description': r.description,
            'date_started': r.date_started.strftime('%b. %d, %Y'),
            'date_completed': r.date_completed.strftime('%b. %d, %Y') if r.date_completed else None
        })
    return JsonResponse(data, safe=False)

def add_early_recovery(request):
    """API to add a new early recovery activity."""
    if request.method == 'POST':
        try:
            area_id = request.POST.get('area')
            area = get_object_or_404(AffectedArea, id=area_id)
            
            date_completed = request.POST.get('date_completed')
            if not date_completed:
                date_completed = None
                
            EarlyRecovery.objects.create(
                area=area,
                description=request.POST.get('description'),
                date_started=request.POST.get('date_started'),
                date_completed=date_completed
            )
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def delete_early_recovery(request, rec_id):
    """API to delete an early recovery activity."""
    if request.method == 'POST':
        try:
            r = get_object_or_404(EarlyRecovery, id=rec_id)
            r.delete()
            return JsonResponse({'status': 'success'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})


def get_disasters(request):
    disasters = Disaster.objects.all().values('id', 'name', 'description', 'date_occurred')
    return JsonResponse(list(disasters), safe=False)


# Family Member endpoints
def get_family_members(request, family_id):
    family = get_object_or_404(Family, id=family_id)
    members = family.familymember_set.all()
    data = []
    for m in members:
        data.append({
            'id': m.id,
            'name': m.name,
            'age': m.age,
            'gender': m.gender,
            'relationship_to_head': m.relationship_to_head,
            'sector': m.sector,
            'is_pwd': m.is_pwd,
            'is_pregnant_lactating': m.is_pregnant_lactating,
            'is_displaced': m.is_displaced,
            'is_in_evacuation_center': m.is_in_evacuation_center
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def add_family_member(request, family_id):
    try:
        data = json.loads(request.body)
        family = get_object_or_404(Family, id=family_id)
        
        member = FamilyMember.objects.create(
            family=family,
            name=data.get('name'),
            age=int(data.get('age', 0)),
            gender=data.get('gender'),
            relationship_to_head=data.get('relationship'),
            sector=data.get('sector', ''),
            is_pwd=data.get('is_pwd', False),
            is_pregnant_lactating=data.get('is_pregnant_lactating', False),
            is_displaced=data.get('is_displaced', False),
            is_in_evacuation_center=data.get('is_in_evacuation', False)
        )
        return JsonResponse({'status': 'success', 'member_id': member.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
@require_POST
def delete_family_member(request, member_id):
    try:
        member = get_object_or_404(FamilyMember, id=member_id)
        member.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

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

# ----------------------------------------------------------------------
# Family Management Views
# ----------------------------------------------------------------------

def family_list(request):
    """View to manage families belonging to affected areas."""
    areas = AffectedArea.objects.all().select_related('disaster', 'province', 'municipality', 'barangay')
    return render(request, 'core/family_list.html', {'areas': areas})

def get_families(request):
    """API to fetch all families."""
    families = Family.objects.all().select_related('area__barangay', 'area__municipality', 'area__province', 'area__disaster')
    data = []
    for f in families:
        area_str = f"{f.area.barangay.name}, {f.area.municipality.name}, {f.area.province.name}" if hasattr(f.area, 'barangay') and f.area.barangay else f"{f.area.municipality.name}, {f.area.province.name}"
        data.append({
            'id': f.id,
            'head_of_family': f.head_of_family,
            'number_of_members': f.number_of_members,
            'area_id': f.area.id,
            'area_name': area_str,
            'disaster_name': f.area.disaster.name
        })
    return JsonResponse(data, safe=False)

@csrf_exempt
@require_POST
def add_family(request):
    try:
        data = json.loads(request.body)
        area = get_object_or_404(AffectedArea, id=data.get('area_id'))
        
        family = Family.objects.create(
            area=area,
            head_of_family=data.get('head_of_family'),
            number_of_members=int(data.get('number_of_members', 1))
        )
        return JsonResponse({'status': 'success', 'family_id': family.id})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})

@csrf_exempt
@require_POST
def delete_family(request, family_id):
    try:
        family = get_object_or_404(Family, id=family_id)
        family.delete()
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)})
