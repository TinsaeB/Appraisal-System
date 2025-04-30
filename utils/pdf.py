"""
Utility for generating PDF reports from appraisals.
"""
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from io import BytesIO
from models.appraisal import Appraisal

from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet

def generate_appraisal_pdf(appraisals):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()
    elements = []
    elements.append(Paragraph("<b>Employee Appraisal Report</b>", styles['Title']))
    elements.append(Spacer(1, 18))
    data = [["Period", "Self Review", "Manager Review", "Status"]]
    for a in appraisals:
        data.append([
            a.period,
            (a.self_review or "")[:100],
            (a.manager_review or "")[:100],
            a.status
        ])
    table = Table(data, colWidths=[80, 180, 180, 60])
    table.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#dbeafe')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.HexColor('#1e293b')),
        ('ALIGN', (0,0), (-1,-1), 'LEFT'),
        ('FONTNAME', (0,0), (-1,0), 'Helvetica-Bold'),
        ('FONTSIZE', (0,0), (-1,0), 12),
        ('BOTTOMPADDING', (0,0), (-1,0), 12),
        ('BACKGROUND', (0,1), (-1,-1), colors.white),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#93c5fd')),
        ('ROWBACKGROUNDS', (0,1), (-1,-1), [colors.white, colors.HexColor('#f1f5f9')]),
    ]))
    elements.append(table)
    doc.build(elements)
    buffer.seek(0)
    return buffer.read()
