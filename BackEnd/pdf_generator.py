# pdf_generator.py
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable
from reportlab.lib.enums import TA_CENTER, TA_LEFT
import re
import os
from datetime import datetime


def generate_itinerary_pdf(itinerary_text, filename="itinerary.pdf"):
    """Convert itinerary text to a beautiful PDF"""

    output_dir = os.path.join(os.getcwd(), "static", "pdfs")
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, filename)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        rightMargin=40,
        leftMargin=40,
        topMargin=40,
        bottomMargin=40
    )

    # ─────────────────────────────────────────
    # Styles
    # ─────────────────────────────────────────
    styles = getSampleStyleSheet()

    title_style = ParagraphStyle(
        'TitleStyle',
        parent=styles['Title'],
        fontSize=24,
        textColor=colors.HexColor('#1a73e8'),
        spaceAfter=10,
        alignment=TA_CENTER,
        fontName='Helvetica-Bold'
    )

    subtitle_style = ParagraphStyle(
        'SubtitleStyle',
        parent=styles['Normal'],
        fontSize=11,
        textColor=colors.HexColor('#555555'),
        spaceAfter=20,
        alignment=TA_CENTER,
        fontName='Helvetica'
    )

    section_header_style = ParagraphStyle(
        'SectionHeader',
        parent=styles['Normal'],
        fontSize=13,
        textColor=colors.white,
        backColor=colors.HexColor('#1a73e8'),
        spaceBefore=15,
        spaceAfter=8,
        leftIndent=10,
        rightIndent=10,
        fontName='Helvetica-Bold'
    )

    day_header_style = ParagraphStyle(
        'DayHeader',
        parent=styles['Normal'],
        fontSize=12,
        textColor=colors.HexColor('#1a73e8'),
        spaceBefore=12,
        spaceAfter=6,
        fontName='Helvetica-Bold',
    )

    label_style = ParagraphStyle(
        'LabelStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#555555'),
        fontName='Helvetica-Bold',
        spaceAfter=2,
    )

    value_style = ParagraphStyle(
        'ValueStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica',
        spaceAfter=4,
        leftIndent=10,
    )

    activity_style = ParagraphStyle(
        'ActivityStyle',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.HexColor('#333333'),
        fontName='Helvetica',
        spaceAfter=3,
        leftIndent=20,
    )

    # ─────────────────────────────────────────
    # Helper
    # ─────────────────────────────────────────
    def extract(text, field):
        match = re.search(rf'{field}:\s*(.+)', text)
        return match.group(1).strip() if match else ''

    # ─────────────────────────────────────────
    # Build content
    # ─────────────────────────────────────────
    content = []

    # Extract main fields
    title       = extract(itinerary_text, "ITINERARY") or "Travel Itinerary"
    destination = extract(itinerary_text, "DESTINATION")
    duration    = extract(itinerary_text, "DURATION")
    budget      = extract(itinerary_text, "BUDGET")
    travelers   = extract(itinerary_text, "TRAVELERS")
    trip_type   = extract(itinerary_text, "TRIP_TYPE")
    summary     = extract(itinerary_text, "SUMMARY")

    # ── Title ──
    content.append(Paragraph(f"✈ {title}", title_style))
    content.append(Paragraph(
        f"Generated on {datetime.now().strftime('%B %d, %Y')}",
        subtitle_style
    ))
    content.append(HRFlowable(
        width="100%", thickness=2,
        color=colors.HexColor('#1a73e8')
    ))
    content.append(Spacer(1, 15))

    # ── Trip Overview ──
    content.append(Paragraph("TRIP OVERVIEW", section_header_style))
    content.append(Spacer(1, 8))

    overview_data = [
        ["Destination", destination or "N/A", "Duration", duration or "N/A"],
        ["Budget",      budget or "N/A",      "Travelers", travelers or "N/A"],
        ["Trip Type",   trip_type or "N/A",   "",          ""],
    ]

    overview_table = Table(
        overview_data,
        colWidths=[1.2*inch, 2*inch, 1.2*inch, 2*inch]
    )
    overview_table.setStyle(TableStyle([
        ('BACKGROUND',  (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
        ('BACKGROUND',  (2, 0), (2, -1), colors.HexColor('#e8f0fe')),
        ('FONTNAME',    (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTNAME',    (2, 0), (2, -1), 'Helvetica-Bold'),
        ('FONTSIZE',    (0, 0), (-1, -1), 10),
        ('PADDING',     (0, 0), (-1, -1), 8),
        ('GRID',        (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
        ('ROWBACKGROUNDS', (0, 0), (-1, -1),
            [colors.HexColor('#f8f9fa'), colors.white]),
    ]))
    content.append(overview_table)
    content.append(Spacer(1, 10))

    # ── Summary ──
    if summary:
        content.append(Paragraph("TRIP SUMMARY", section_header_style))
        content.append(Spacer(1, 5))
        content.append(Paragraph(summary, value_style))
        content.append(Spacer(1, 10))

    # ── Day by Day ──
    content.append(Paragraph("DAY BY DAY ITINERARY", section_header_style))
    content.append(Spacer(1, 8))

    day_blocks = re.split(r'(DAY \d+:)', itinerary_text)

    i = 1
    while i < len(day_blocks):
        if re.match(r'DAY \d+:', day_blocks[i]):
            day_label = day_blocks[i]
            block     = day_blocks[i + 1] if i + 1 < len(day_blocks) else ""
            i += 2

            lines     = block.strip().split('\n')
            day_title = lines[0].strip() if lines else ""

            # Day header
            content.append(Paragraph(
                f"{day_label} {day_title}",
                day_header_style
            ))
            content.append(HRFlowable(
                width="100%", thickness=1,
                color=colors.HexColor('#1a73e8')
            ))
            content.append(Spacer(1, 5))

            # Day fields
            hotel       = extract(block, "HOTEL")
            transport   = extract(block, "TRANSPORT")
            cost        = extract(block, "COST")
            description = extract(block, "DESCRIPTION")

            if description:
                content.append(Paragraph("Description", label_style))
                content.append(Paragraph(description, value_style))

            # Details table
            details_data = []
            if hotel:
                details_data.append(["Hotel", hotel])
            if transport:
                details_data.append(["Transport", transport])
            if cost:
                details_data.append(["Est. Cost", cost])

            if details_data:
                details_table = Table(
                    details_data,
                    colWidths=[1.5*inch, 4.5*inch]
                )
                details_table.setStyle(TableStyle([
                    ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#e8f0fe')),
                    ('FONTNAME',   (0, 0), (0, -1), 'Helvetica-Bold'),
                    ('FONTSIZE',   (0, 0), (-1, -1), 10),
                    ('PADDING',    (0, 0), (-1, -1), 6),
                    ('GRID',       (0, 0), (-1, -1), 0.5, colors.HexColor('#cccccc')),
                ]))
                content.append(details_table)
                content.append(Spacer(1, 5))

            # Activities
            activity_section = re.search(
                r'ACTIVITIES:(.*?)(?=DAY \d+:|$)', block, re.DOTALL
            )
            if activity_section:
                content.append(Paragraph("Activities", label_style))
                for line in activity_section.group(1).strip().split('\n'):
                    line = line.strip().lstrip('- ')
                    if not line:
                        continue
                    parts         = [p.strip() for p in line.split('|')]
                    activity_name = parts[0] if parts else ''
                    location      = parts[1] if len(parts) > 1 else ''
                    time          = parts[2] if len(parts) > 2 else ''
                    act_cost      = parts[3] if len(parts) > 3 else ''
                    notes         = parts[4] if len(parts) > 4 else ''

                    activity_text = f"• <b>{activity_name}</b>"
                    if location: activity_text += f" — {location}"
                    if time:     activity_text += f" | {time}"
                    if act_cost: activity_text += f" | {act_cost}"
                    if notes:    activity_text += f" | {notes}"

                    content.append(Paragraph(activity_text, activity_style))

            content.append(Spacer(1, 10))
        else:
            i += 1

    # ── Footer ──
    content.append(HRFlowable(
        width="100%", thickness=2,
        color=colors.HexColor('#1a73e8')
    ))
    content.append(Spacer(1, 10))
    content.append(Paragraph(
        "Generated by AI Travel Chatbot",
        subtitle_style
    ))

    # Build PDF
    doc.build(content)
    print(f"✅ PDF generated: {output_path}")
    return output_path