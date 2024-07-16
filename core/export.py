from io import BytesIO
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.platypus import Table, TableStyle, SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from django.http import HttpResponse
from django.db.models import Sum
from .models import DROMICReport, DisplacedPopulation, SexAgeDistribution, SectoralDistribution, DamagedHouse, ReliefOperation

def generate_report_pdf(report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)

    styles = getSampleStyleSheet()
    elements = []

    # Title
    elements.append(Paragraph(f"DROMIC Report: {report.disaster.name}", styles['Title']))
    elements.append(Spacer(1, 0.5 * inch))

    # Summary Statistics
    elements.append(Paragraph("Summary Statistics", styles['Heading2']))
    data = [
        ["Total Affected Families", str(report.total_affected_families())],
        ["Total Affected Persons", str(report.total_affected_persons())],
    ]
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)]))
    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))

    # Displaced Population
    elements.append(Paragraph("Displaced Population", styles['Heading2']))
    displaced = DisplacedPopulation.objects.filter(area__in=report.affected_areas.all()).aggregate(
        cum_families=Sum('cum_families'),
        now_families=Sum('now_families'),
        cum_persons=Sum('cum_persons'),
        now_persons=Sum('now_persons')
    )
    data = [
        ["", "Cumulative", "Current"],
        ["Families", str(displaced['cum_families']), str(displaced['now_families'])],
        ["Persons", str(displaced['cum_persons']), str(displaced['now_persons'])],
    ]
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)]))
    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))

    # Sex and Age Distribution
    elements.append(Paragraph("Sex and Age Distribution", styles['Heading2']))
    sex_age = SexAgeDistribution.objects.filter(population__area__in=report.affected_areas.all()).values('sex', 'age_group').annotate(
        cum_total=Sum('cum_count'),
        now_total=Sum('now_count')
    )
    data = [["Sex", "Age Group", "Cumulative", "Current"]]
    for item in sex_age:
        data.append([item['sex'], item['age_group'], str(item['cum_total']), str(item['now_total'])])
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)]))
    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))

    # Damaged Houses
    elements.append(Paragraph("Damaged Houses", styles['Heading2']))
    damaged = DamagedHouse.objects.filter(area__in=report.affected_areas.all()).aggregate(
        partially_damaged=Sum('partially_damaged'),
        totally_damaged=Sum('totally_damaged')
    )
    data = [
        ["Partially Damaged", str(damaged['partially_damaged'])],
        ["Totally Damaged", str(damaged['totally_damaged'])],
    ]
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)]))
    elements.append(table)
    elements.append(Spacer(1, 0.25 * inch))

    # Relief Operations
    elements.append(Paragraph("Relief Operations", styles['Heading2']))
    relief = ReliefOperation.objects.filter(area__in=report.affected_areas.all()).aggregate(
        total_financial_assistance=Sum('financial_assistance'),
        total_food_items=Sum('food_items'),
        total_non_food_items=Sum('non_food_items')
    )
    data = [
        ["Financial Assistance", f"${relief['total_financial_assistance']:.2f}"],
        ["Food Items", str(relief['total_food_items'])],
        ["Non-Food Items", str(relief['total_non_food_items'])],
    ]
    table = Table(data)
    table.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, 0), colors.grey),
                               ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke)]))
    elements.append(table)

    doc.build(elements)
    buffer.seek(0)
    return buffer
