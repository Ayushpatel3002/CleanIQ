import io
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle


def generate_pdf_report(dataset_name: str, summary: dict, health_score: float, fix_log: list, quality_report: dict) -> bytes:
    """
    Generates a PDF Data Quality & Audit Report using reportlab.
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=36, leftMargin=36, topMargin=36, bottomMargin=36)
    elements = []
    styles = getSampleStyleSheet()

    # Custom Styles
    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=22,
        textColor=colors.HexColor('#1e1b4b'),
        spaceAfter=6
    )
    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontName='Helvetica',
        fontSize=11,
        textColor=colors.HexColor('#64748b'),
        spaceAfter=15
    )
    section_heading = ParagraphStyle(
        'SectionHeading',
        parent=styles['Heading2'],
        fontName='Helvetica-Bold',
        fontSize=14,
        textColor=colors.HexColor('#4338ca'),
        spaceBefore=14,
        spaceAfter=8
    )
    body_style = ParagraphStyle(
        'Body',
        parent=styles['Normal'],
        fontSize=9,
        textColor=colors.HexColor('#334155')
    )

    # Title
    elements.append(Paragraph("CleanIQ — Data Quality & Cleaning Audit Report", title_style))
    elements.append(Paragraph(f"Dataset: <b>{dataset_name}</b> | Health Score: <b>{health_score}/100</b>", subtitle_style))
    elements.append(Spacer(1, 10))

    # Dataset Summary Table
    elements.append(Paragraph("1. Dataset Summary", section_heading))
    summary_data = [
        ["Metric", "Value", "Metric", "Value"],
        ["Total Rows", str(summary.get("Rows", "—")), "Total Columns", str(summary.get("Columns", "—"))],
        ["Missing Values", str(summary.get("Missing Values", "—")), "Missing %", f"{summary.get('Missing %', '0')}%"],
        ["Duplicate Rows", str(summary.get("Duplicate Rows", "—")), "Memory (MB)", str(summary.get("Memory Usage (MB)", "—"))],
        ["Numeric Columns", str(summary.get("Numeric Columns", "—")), "Categorical Columns", str(summary.get("Categorical Columns", "—"))],
    ]
    t_summary = Table(summary_data, colWidths=[130, 130, 130, 130])
    t_summary.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#4f46e5')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
        ('BACKGROUND', (0, 1), (-1, -1), colors.HexColor('#f8fafc')),
        ('ALIGN', (1, 1), (1, -1), 'CENTER'),
        ('ALIGN', (3, 1), (3, -1), 'CENTER'),
    ]))
    elements.append(t_summary)
    elements.append(Spacer(1, 15))

    # Fix History Table
    elements.append(Paragraph("2. Remediation & Cleaning History", section_heading))
    if fix_log:
        fix_rows = [["#", "Target Column", "Issue Remediated", "Action Executed"]]
        for idx, item in enumerate(fix_log[:20], 1):
            fix_rows.append([
                str(idx),
                str(item.get("Column", "—")),
                str(item.get("Issue", "—")),
                str(item.get("Fix Applied", "—"))[:65]
            ])
        t_fix = Table(fix_rows, colWidths=[25, 110, 140, 245])
        t_fix.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#0284c7')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#e2e8f0')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f1f5f9')])
        ]))
        elements.append(t_fix)
    else:
        elements.append(Paragraph("<i>No individual fixes logged yet. Standard pipeline clean was applied.</i>", body_style))
    elements.append(Spacer(1, 15))

    # Quality Checks Remaining
    elements.append(Paragraph("3. Current Quality Assessment Checks", section_heading))
    quality_rows = [["Validation Category", "Column", "Findings", "Status"]]
    for check_name, findings_dict in quality_report.items():
        if isinstance(findings_dict, dict):
            for col, findings in list(findings_dict.items())[:5]:
                status = "OK" if findings == 0 else f"{findings} Issues"
                quality_rows.append([check_name, col, str(findings), status])

    if len(quality_rows) > 1:
        t_qual = Table(quality_rows[:15], colWidths=[150, 130, 140, 100])
        t_qual.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#334155')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('GRID', (0, 0), (-1, -1), 0.5, colors.HexColor('#cbd5e1')),
            ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.HexColor('#f8fafc')])
        ]))
        elements.append(t_qual)
    else:
        elements.append(Paragraph("<i>All quality checks passed with zero anomalies.</i>", body_style))

    # Build PDF
    doc.build(elements)
    buffer.seek(0)
    return buffer.getvalue()
