from io import BytesIO
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.piecharts import Pie
from reportlab.graphics.charts.barcharts import VerticalBarChart
from django.db.models import Sum

def generate_report_pdf(report):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, topMargin=72, bottomMargin=18)

    styles = getSampleStyleSheet()
    if 'Heading1' not in styles:
        styles.add(ParagraphStyle(name='Heading1', fontSize=18, spaceAfter=12))
    if 'Heading2' not in styles:
        styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceAfter=8))


    elements = []
    
    # --- LOGO HEADER ---
    import os
    from django.conf import settings
    
    static_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'img')
    
    def get_safe_image(filename, width, height):
        try:
            path = os.path.join(static_dir, filename)
            if os.path.exists(path):
                img = Image(path, width=width, height=height)
                return img
        except Exception:
            pass
        return ""

    dromic_img = get_safe_image('dromic_logo.png', 3.2*cm, 3.2*cm)
    dswd_img = get_safe_image('dswd_logo.png', 2.5*cm, 2.5*cm)

    header_text = Paragraph(
        "<font size=9>Republic of the Philippines</font><br/>"
        "<font size=9>Department of Social Welfare and Development</font><br/>"
        "<b><font size=11>DISASTER RESPONSE OPERATIONS MONITORING AND INFORMATION CENTER</font></b><br/>"
        "<font size=9>Dumingag, Zamboanga del Sur</font>",
        ParagraphStyle(name='CenterHeader', alignment=1, leading=12)
    )
    
    header_table = Table(
        [[dromic_img, header_text, dswd_img]], 
        colWidths=[3.2*cm, 10.6*cm, 3*cm]
    )
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    # -------------------

    # Title
    elements.append(Paragraph(f"DROMIC Report: {report.disaster.name}", styles['Heading1']))
    elements.append(Paragraph(f"Date: {report.date.strftime('%B %d, %Y')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Location
    elements.append(Paragraph("Location", styles['Heading2']))
    location_data = [
        ["Province", report.province.name],
        ["Municipality", report.municipality.name],
        ["Barangay", report.barangay.name]
    ]
    location_table = Table(location_data, colWidths=[4*cm, 10*cm])
    location_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.lightgrey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('ALIGN', (0,1), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(location_table)
    elements.append(Spacer(1, 0.5*cm))

    # Summary Statistics
    elements.append(Paragraph("Summary Statistics", styles['Heading2']))
    summary_data = [
        ["Total Affected Families", str(report.total_affected_families())],
        ["Total Affected Persons", str(report.total_affected_persons())]
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # Displaced Population
    elements.append(Paragraph("Displaced Population", styles['Heading2']))
    displaced = report.displaced_populations.aggregate(
        cum_families=Sum('cum_families'),
        now_families=Sum('now_families'),
        cum_persons=Sum('cum_persons'),
        now_persons=Sum('now_persons')
    )
    displaced_data = [
        ["", "Cumulative", "Current"],
        ["Families", str(displaced['cum_families']), str(displaced['now_families'])],
        ["Persons", str(displaced['cum_persons']), str(displaced['now_persons'])]
    ]
    displaced_table = Table(displaced_data, colWidths=[4*cm, 5*cm, 5*cm])
    displaced_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(displaced_table)
    elements.append(Spacer(1, 0.5*cm))

    # Damaged Houses
    elements.append(Paragraph("Damaged Houses", styles['Heading2']))
    damaged = report.damaged_houses.aggregate(
        partially_damaged=Sum('partially_damaged'),
        totally_damaged=Sum('totally_damaged')
    )
    damaged_data = [
        ["Partially Damaged", str(damaged['partially_damaged'])],
        ["Totally Damaged", str(damaged['totally_damaged'])]
    ]
    damaged_table = Table(damaged_data, colWidths=[8*cm, 6*cm])
    damaged_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightgreen),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(damaged_table)
    elements.append(Spacer(1, 0.5*cm))

    # Relief Operations
    elements.append(Paragraph("Relief Operations", styles['Heading2']))
    relief_data = [["Date", "Food Items", "Non-Food Items", "Financial Assistance"]]
    for relief in report.relief_operations.all():
        relief_data.append([
            relief.date.strftime('%Y-%m-%d'),
            str(relief.food_items),
            str(relief.non_food_items),
            f"${relief.financial_assistance:.2f}"
        ])
    relief_table = Table(relief_data, colWidths=[4*cm, 4*cm, 4*cm, 4*cm])
    relief_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('ALIGN', (0,1), (-1,-1), 'CENTER'),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 6),
        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(relief_table)

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer

def truncate_with_ellipsis(text, max_length=30):
    """Truncate text and add ellipsis if it exceeds max_length."""
    if len(text) > max_length:
        return text[:max_length-3] + "..."
    return text

def generate_affected_areas_pdf(affected_areas):
    """Generate a PDF report for affected areas."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=18)

    styles = getSampleStyleSheet()
    if 'Heading1' not in styles:
        styles.add(ParagraphStyle(name='Heading1', fontSize=18, spaceAfter=12))
    if 'Heading2' not in styles:
        styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceAfter=8))

    elements = []
    
    # --- LOGO HEADER ---
    import os
    from django.conf import settings
    
    static_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'img')
    
    def get_safe_image(filename, width, height):
        try:
            path = os.path.join(static_dir, filename)
            if os.path.exists(path):
                img = Image(path, width=width, height=height)
                return img
        except Exception:
            pass
        return ""

    dromic_img = get_safe_image('dromic_logo.png', 3.2*cm, 3.2*cm)
    dswd_img = get_safe_image('dswd_logo.png', 2.5*cm, 2.5*cm)

    header_text = Paragraph(
        "<font size=9>Republic of the Philippines</font><br/>"
        "<font size=9>Department of Social Welfare and Development</font><br/>"
        "<b><font size=11>DISASTER RESPONSE OPERATIONS MONITORING AND INFORMATION CENTER</font></b><br/>"
        "<font size=9>Dumingag, Zamboanga del Sur</font>",
        ParagraphStyle(name='CenterHeader', alignment=1, leading=12)
    )
    
    header_table = Table(
        [[dromic_img, header_text, dswd_img]], 
        colWidths=[3.2*cm, 10.6*cm, 3*cm]
    )
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    # -------------------

    # Title
    elements.append(Paragraph("Affected Areas Report", styles['Heading1']))
    from django.utils import timezone
    elements.append(Paragraph(f"Report Generated: {timezone.now().strftime('%B %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Summary Statistics
    total_areas = len(affected_areas)
    total_families = sum(area.affected_families for area in affected_areas)
    total_persons = sum(area.affected_persons for area in affected_areas)

    elements.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ["Total Affected Areas", str(total_areas)],
        ["Total Affected Families", str(total_families)],
        ["Total Affected Persons", str(total_persons)]
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # Affected Areas Table
    elements.append(Paragraph("Affected Areas Details", styles['Heading2']))
    data = [["Disaster", "Date Occurred", "Province", "Municipality", "Barangay", "Families", "Persons"]]
    
    for area in affected_areas:
        barangay_name = area.barangay.name if area.barangay else "-"
        date_occurred = area.disaster.date_occurred.strftime('%b %d, %Y') if area.disaster.date_occurred else "-"
        data.append([
            truncate_with_ellipsis(area.disaster.name, 35),
            date_occurred,
            truncate_with_ellipsis(area.province.name, 20),
            truncate_with_ellipsis(area.municipality.name, 20),
            truncate_with_ellipsis(barangay_name, 20),
            str(area.affected_families),
            str(area.affected_persons)
        ])

    table = Table(data, colWidths=[4.5*cm, 3*cm, 3.5*cm, 3.5*cm, 3.5*cm, 2*cm, 2*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (4,-1), 'CENTER'),
        ('ALIGN', (0,1), (3,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('TOPPADDING', (0,1), (-1,-1), 3),
        ('BOTTOMPADDING', (0,1), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_families_pdf(families):
    """Generate a PDF report for families."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=18)

    styles = getSampleStyleSheet()
    if 'Heading1' not in styles:
        styles.add(ParagraphStyle(name='Heading1', fontSize=18, spaceAfter=12))
    if 'Heading2' not in styles:
        styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceAfter=8))

    elements = []
    
    # --- LOGO HEADER ---
    import os
    from django.conf import settings
    
    static_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'img')
    
    def get_safe_image(filename, width, height):
        try:
            path = os.path.join(static_dir, filename)
            if os.path.exists(path):
                img = Image(path, width=width, height=height)
                return img
        except Exception:
            pass
        return ""

    dromic_img = get_safe_image('dromic_logo.png', 3.2*cm, 3.2*cm)
    dswd_img = get_safe_image('dswd_logo.png', 2.5*cm, 2.5*cm)

    header_text = Paragraph(
        "<font size=9>Republic of the Philippines</font><br/>"
        "<font size=9>Department of Social Welfare and Development</font><br/>"
        "<b><font size=11>DISASTER RESPONSE OPERATIONS MONITORING AND INFORMATION CENTER</font></b><br/>"
        "<font size=9>Dumingag, Zamboanga del Sur</font>",
        ParagraphStyle(name='CenterHeader', alignment=1, leading=12)
    )
    
    header_table = Table(
        [[dromic_img, header_text, dswd_img]], 
        colWidths=[3.2*cm, 10.6*cm, 3*cm]
    )
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    # -------------------

    # Title
    elements.append(Paragraph("Families Report", styles['Heading1']))
    from django.utils import timezone
    elements.append(Paragraph(f"Report Generated: {timezone.now().strftime('%b %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Summary Statistics
    total_families = len(families)
    total_members = sum(f.number_of_members for f in families)
    
    # Count house conditions
    from django.db.models import Q
    totally_damaged = sum(1 for f in families if f.house_condition == 'Totally Damaged')
    partially_damaged = sum(1 for f in families if f.house_condition == 'Partially Damaged')
    not_damaged = sum(1 for f in families if f.house_condition == 'Not Damaged')

    elements.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ["Total Families", str(total_families)],
        ["Total Family Members", str(total_members)],
        ["Totally Damaged Houses", str(totally_damaged)],
        ["Partially Damaged Houses", str(partially_damaged)],
        ["Not Damaged Houses", str(not_damaged)]
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # Families Table
    elements.append(Paragraph("Families Details", styles['Heading2']))
    data = [["Family Head", "Disaster", "Location", "Members", "House Condition"]]
    
    for family in families:
        area_str = f"{family.area.barangay.name if family.area.barangay else ''}, {family.area.municipality.name}, {family.area.province.name}".strip(', ')
        data.append([
            truncate_with_ellipsis(family.head_of_family, 30),
            truncate_with_ellipsis(family.area.disaster.name, 30),
            truncate_with_ellipsis(area_str, 35),
            str(family.number_of_members),
            family.house_condition
        ])

    table = Table(data, colWidths=[4*cm, 4*cm, 5*cm, 2*cm, 3.5*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (2,-1), 'LEFT'),
        ('ALIGN', (3,-1), (4,-1), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('TOPPADDING', (0,1), (-1,-1), 3),
        ('BOTTOMPADDING', (0,1), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_relief_operations_pdf(operations):
    """Generate a PDF report for relief operations."""
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4), rightMargin=50, leftMargin=50, topMargin=60, bottomMargin=18)

    styles = getSampleStyleSheet()
    if 'Heading1' not in styles:
        styles.add(ParagraphStyle(name='Heading1', fontSize=18, spaceAfter=12))
    if 'Heading2' not in styles:
        styles.add(ParagraphStyle(name='Heading2', fontSize=14, spaceAfter=8))

    elements = []
    
    # --- LOGO HEADER ---
    import os
    from django.conf import settings
    
    static_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'img')
    
    def get_safe_image(filename, width, height):
        try:
            path = os.path.join(static_dir, filename)
            if os.path.exists(path):
                img = Image(path, width=width, height=height)
                return img
        except Exception:
            pass
        return ""

    dromic_img = get_safe_image('dromic_logo.png', 3.2*cm, 3.2*cm)
    dswd_img = get_safe_image('dswd_logo.png', 2.5*cm, 2.5*cm)

    header_text = Paragraph(
        "<font size=9>Republic of the Philippines</font><br/>"
        "<font size=9>Department of Social Welfare and Development</font><br/>"
        "<b><font size=11>DISASTER RESPONSE OPERATIONS MONITORING AND INFORMATION CENTER</font></b><br/>"
        "<font size=9>Dumingag, Zamboanga del Sur</font>",
        ParagraphStyle(name='CenterHeader', alignment=1, leading=12)
    )
    
    header_table = Table(
        [[dromic_img, header_text, dswd_img]], 
        colWidths=[3.2*cm, 10.6*cm, 3*cm]
    )
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    # -------------------

    # Title
    elements.append(Paragraph("Relief Operations Report", styles['Heading1']))
    from django.utils import timezone
    elements.append(Paragraph(f"Report Generated: {timezone.now().strftime('%b %d, %Y at %I:%M %p')}", styles['Normal']))
    elements.append(Spacer(1, 0.5*cm))

    # Summary Statistics
    total_operations = len(operations)
    total_food = sum(op.food_items for op in operations)
    total_non_food = sum(op.non_food_items for op in operations)
    total_financial = sum(op.financial_assistance for op in operations)

    elements.append(Paragraph("Summary", styles['Heading2']))
    summary_data = [
        ["Total Operations", str(total_operations)],
        ["Total Food Items", str(total_food)],
        ["Total Non-Food Items", str(total_non_food)],
        ["Total Financial Assistance", f"₱{total_financial:,.2f}"]
    ]
    summary_table = Table(summary_data, colWidths=[8*cm, 6*cm])
    summary_table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,-1), colors.lightblue),
        ('TEXTCOLOR', (0,0), (-1,-1), colors.black),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,-1), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,-1), 10),
        ('TOPPADDING', (0,0), (-1,-1), 6),
        ('BOTTOMPADDING', (0,0), (-1,-1), 6),
        ('GRID', (0,0), (-1,-1), 1, colors.black)
    ]))
    elements.append(summary_table)
    elements.append(Spacer(1, 0.5*cm))

    # Relief Operations Table
    elements.append(Paragraph("Relief Operations Details", styles['Heading2']))
    data = [["Date", "Disaster", "Location", "Food Items", "Non-Food Items", "Financial (₱)"]]
    
    for op in operations:
        area_str = f"{op.area.barangay.name if op.area.barangay else ''}, {op.area.municipality.name}, {op.area.province.name}".strip(', ')
        op_date = op.date.strftime('%b %d, %Y') if op.date else "-"
        data.append([
            op_date,
            truncate_with_ellipsis(op.area.disaster.name, 30),
            truncate_with_ellipsis(area_str, 35),
            str(op.food_items),
            str(op.non_food_items),
            f"{op.financial_assistance:,.2f}"
        ])

    table = Table(data, colWidths=[3*cm, 4*cm, 5*cm, 2*cm, 2.5*cm, 3*cm])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.grey),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (2,-1), 'LEFT'),
        ('ALIGN', (3,-1), (5,-1), 'RIGHT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.beige),
        ('TEXTCOLOR', (0,1), (-1,-1), colors.black),
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 7),
        ('TOPPADDING', (0,1), (-1,-1), 3),
        ('BOTTOMPADDING', (0,1), (-1,-1), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.black),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE')
    ]))
    elements.append(table)

    # Build the PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer


def generate_rds_pdf(operation):
    """Generate a Relief Distribution Sheet (RDS) for a specific Relief Operation."""
    from .models import Family, FamilyDistribution
    
    buffer = BytesIO()
    # RDS typically needs more width for signatures, so landscape could be better, but A4 portrait is standard.
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=36, leftMargin=36, topMargin=54, bottomMargin=36)

    styles = getSampleStyleSheet()
    if 'Heading1' not in styles:
        styles.add(ParagraphStyle(name='Heading1', fontSize=18, spaceAfter=12, alignment=1)) # Center
    if 'Heading2' not in styles:
        styles.add(ParagraphStyle(name='Heading2', fontSize=12, spaceAfter=8))
    
    title_style = ParagraphStyle(name='TitleStyle', fontSize=16, spaceAfter=12, alignment=1, fontName='Helvetica-Bold')
    subtitle_style = ParagraphStyle(name='SubtitleStyle', fontSize=10, spaceAfter=20, alignment=1)

    elements = []

    # --- LOGO HEADER ---
    import os
    from django.conf import settings
    
    static_dir = os.path.join(settings.BASE_DIR, 'core', 'static', 'img')
    
    def get_safe_image(filename, width, height):
        try:
            path = os.path.join(static_dir, filename)
            if os.path.exists(path):
                img = Image(path, width=width, height=height)
                return img
        except Exception:
            pass
        return ""

    dromic_img = get_safe_image('dromic_logo.png', 3.2*cm, 3.2*cm)
    dswd_img = get_safe_image('dswd_logo.png', 2.5*cm, 2.5*cm)

    header_text = Paragraph(
        "<font size=10>Republic of the Philippines</font><br/>"
        "<font size=10>Department of Social Welfare and Development</font><br/>"
        "<b><font size=12>DISASTER RESPONSE OPERATIONS MONITORING AND INFORMATION CENTER</font></b><br/>"
        "<font size=10>Dumingag, Zamboanga del Sur</font>",
        ParagraphStyle(name='CenterHeader', alignment=1, leading=14)
    )
    
    header_table = Table(
        [[dromic_img, header_text, dswd_img]], 
        colWidths=[3.7*cm, 12*cm, 3.5*cm]
    )
    header_table.setStyle(TableStyle([
        ('ALIGN', (0,0), (0,0), 'LEFT'),
        ('ALIGN', (1,0), (1,0), 'CENTER'),
        ('ALIGN', (2,0), (2,0), 'RIGHT'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
    ]))
    
    elements.append(header_table)
    elements.append(Spacer(1, 0.5*cm))
    # -------------------

    # Header
    elements.append(Paragraph("RELIEF DISTRIBUTION SHEET (RDS)", title_style))
    
    area_str = f"{operation.area.barangay.name if operation.area.barangay else ''}, {operation.area.municipality.name}, {operation.area.province.name}".strip(', ')
    metadata = f"<b>Disaster:</b> {operation.area.disaster.name} &nbsp;&nbsp;&nbsp; <b>Location:</b> {area_str} <br/>"
    metadata += f"<b>Date of Distribution:</b> {operation.date.strftime('%B %d, %Y')} &nbsp;&nbsp;&nbsp; "
    metadata += f"<b>Assistance Provided:</b> {operation.food_items} Food, {operation.non_food_items} Non-Food, P{operation.financial_assistance:,.2f}"
    
    elements.append(Paragraph(metadata, subtitle_style))

    # Fetch families and distribution status
    families = Family.objects.filter(area=operation.area).order_by('head_of_family')
    distributions = {d.family_id: d for d in FamilyDistribution.objects.filter(operation=operation)}

    # Table Header
    data = [["No.", "Name of Family Head", "Members", "Status", "Signature / Thumbmark"]]

    for i, f in enumerate(families, 1):
        dist = distributions.get(f.id)
        status_text = "Received" if dist and dist.is_received else ""
        data.append([str(i), f.head_of_family, str(f.number_of_members), status_text, ""])

    # Define column widths: Number, Name, Members, Status, Signature
    col_widths = [1.5*cm, 7*cm, 2*cm, 2.5*cm, 6*cm]
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    # Styling the table
    table_style = TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#EA580C')), # Orange header
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,0), 'CENTER'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 10),
        ('BOTTOMPADDING', (0,0), (-1,0), 8),
        ('TOPPADDING', (0,0), (-1,0), 8),
        
        # Row styling
        ('ALIGN', (0,1), (0,-1), 'CENTER'), # Center numbers
        ('ALIGN', (1,1), (1,-1), 'LEFT'),   # Left align names
        ('ALIGN', (2,1), (3,-1), 'CENTER'), # Center members and status
        ('FONTNAME', (0,1), (-1,-1), 'Helvetica'),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('BOTTOMPADDING', (0,1), (-1,-1), 10),
        ('TOPPADDING', (0,1), (-1,-1), 10),
        
        # Grid
        ('GRID', (0,0), (-1,-1), 0.5, colors.grey),
    ])
    
    # Add alternating row colors
    for i in range(1, len(data)):
        if i % 2 == 0:
            table_style.add('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F8FAFC')) # Very light slate
            
    table.setStyle(table_style)
    elements.append(table)

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer
