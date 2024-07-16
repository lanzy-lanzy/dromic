from django.shortcuts import render, redirect
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required
from core.models import Disaster, AffectedArea, EvacuationCenter, DROMICReport

def overview(request):
    context = {
        'active_disasters_count': Disaster.objects.count(),
        'total_affected_persons': sum(area.affected_persons for area in AffectedArea.objects.all()),
        'evacuation_centers_count': EvacuationCenter.objects.count(),
        'total_damaged_houses': sum(area.affected_families for area in AffectedArea.objects.all()),
        'recent_reports': DROMICReport.objects.order_by('-date')[:5],
    }
    return render(request, 'core/dashboard.html', context)

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

# @login_required
# def overview(request):
#     return render(request, 'core/overview.html')

@login_required
def disaster_info(request):
    return render(request, 'core/disaster_info.html')

@login_required
def affected_areas(request):
    return render(request, 'core/affected_areas.html')

@login_required
def evacuation_centers(request):
    return render(request, 'core/evacuation_centers.html')

@login_required
def reports(request):
    return render(request, 'core/reports.html')

def logout_view(request):
    logout(request)
    return redirect('login')  # Redirect to your login page