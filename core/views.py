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
    SectoralDistribution, ReliefOperation, Province, Municipality, Barangay
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
    affected_areas = AffectedArea.objects.all()  # You might want to filter this for Mindanao only

    context = {
        'active_disasters_count': active_disasters_count,
        'total_affected_persons': total_affected_persons,
        'evacuation_centers_count': evacuation_centers_count,
        'recent_updates': recent_updates,
        'affected_areas': affected_areas,
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




def report_list(request):
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
    return render(request, 'core/disaster_info.html')


def get_disasters(request):
    disasters = Disaster.objects.all().values('id', 'name', 'description', 'date_occurred')
    return JsonResponse(list(disasters), safe=False)


@csrf_exempt
def create_disaster(request):
    if request.method == 'POST':
        try:
            data = request.POST
            Disaster.objects.create(
                name=data['name'],
                description=data['description'],
                date_occurred=data['date_occurred']
            )
            return JsonResponse({'status': 'success', 'message': 'Disaster created successfully'})
        except Exception as e:
            return JsonResponse({'status': 'error', 'message': str(e)})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method'})
