"""
TalentSphere Elevate - PDF Generator
Generates beautiful certificates and reports using ReportLab.
"""

import io
from datetime import datetime
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.units import cm
from reportlab.lib.colors import HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

PRIMARY = HexColor("#6C5CE7")
SECONDARY = HexColor("#00CEC9")
DARK = HexColor("#2D3436")
GOLD = HexColor("#FDCB6E")


def generate_certificate(fullname, course_title, cert_code, issued_on=None):
    issued_on = issued_on or datetime.now().strftime("%d %B %Y")
    buf = io.BytesIO()
    W, H = landscape(A4)
    c = canvas.Canvas(buf, pagesize=landscape(A4))

    # Background
    c.setFillColor(HexColor("#F8F7FF"))
    c.rect(0, 0, W, H, fill=1, stroke=0)

    # Border
    c.setStrokeColor(PRIMARY)
    c.setLineWidth(6)
    c.rect(1 * cm, 1 * cm, W - 2 * cm, H - 2 * cm, fill=0, stroke=1)
    c.setStrokeColor(GOLD)
    c.setLineWidth(1.5)
    c.rect(1.3 * cm, 1.3 * cm, W - 2.6 * cm, H - 2.6 * cm, fill=0, stroke=1)

    # Header accent
    c.setFillColor(PRIMARY)
    c.rect(0, H - 2.6 * cm, W, 0.15 * cm, fill=1, stroke=0)

    # Logo / Brand
    c.setFont("Helvetica-Bold", 22)
    c.setFillColor(PRIMARY)
    c.drawCentredString(W / 2, H - 3.3 * cm, "🌐 TalentSphere Elevate")

    c.setFont("Helvetica", 12)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 4.0 * cm, "AI-Powered Career Guidance Platform")

    c.setFont("Helvetica-Bold", 34)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 5.8 * cm, "Certificate of Completion")

    c.setFont("Helvetica", 14)
    c.setFillColor(HexColor("#636E72"))
    c.drawCentredString(W / 2, H - 6.8 * cm, "This certificate is proudly presented to")

    c.setFont("Helvetica-Bold", 30)
    c.setFillColor(SECONDARY)
    c.drawCentredString(W / 2, H - 8.2 * cm, fullname)

    c.setLineWidth(1)
    c.setStrokeColor(PRIMARY)
    c.line(W / 2 - 6 * cm, H - 8.6 * cm, W / 2 + 6 * cm, H - 8.6 * cm)

    c.setFont("Helvetica", 14)
    c.setFillColor(DARK)
    c.drawCentredString(W / 2, H - 9.6 * cm, "for successfully completing")

    c.setFont("Helvetica-Bold", 20)
    c.setFillColor(PRIMARY)
    c.drawCentredString(W / 2, H - 10.6 * cm, course_title)

    # Footer details
    c.setFont("Helvetica", 11)
    c.setFillColor(DARK)
    c.drawString(2.5 * cm, 2.3 * cm, f"Date Issued: {issued_on}")
    c.drawString(2.5 * cm, 1.8 * cm, f"Certificate ID: {cert_code}")

    c.setFont("Helvetica-Oblique", 11)
    c.drawRightString(W - 2.5 * cm, 2.3 * cm, "Authorized by")
    c.setFont("Helvetica-Bold", 13)
    c.drawRightString(W - 2.5 * cm, 1.8 * cm, "TalentSphere Elevate Team")

    # Seal
    c.setFillColor(GOLD)
    c.circle(W - 4.2 * cm, 4.5 * cm, 1.3 * cm, fill=1, stroke=0)
    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 9)
    c.drawCentredString(W - 4.2 * cm, 4.6 * cm, "VERIFIED")
    c.drawCentredString(W - 4.2 * cm, 4.3 * cm, "★ ★ ★")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


def generate_report_pdf(title, fullname, sections: dict):
    """sections: dict of {heading: content_text or list}"""
    buf = io.BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)
    y = H - 2.5 * cm

    c.setFillColor(PRIMARY)
    c.rect(0, H - 2 * cm, W, 2 * cm, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1.5 * cm, H - 1.3 * cm, "🌐 TalentSphere Elevate")

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2 * cm, y, title)
    y -= 0.7 * cm
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#636E72"))
    c.drawString(2 * cm, y, f"Prepared for: {fullname}  |  Generated on: {datetime.now().strftime('%d %B %Y')}")
    y -= 1.0 * cm

    for heading, content in sections.items():
        if y < 3 * cm:
            c.showPage()
            y = H - 2.5 * cm
        c.setFillColor(SECONDARY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2 * cm, y, heading)
        y -= 0.55 * cm
        c.setFillColor(DARK)
        c.setFont("Helvetica", 10.5)

        if isinstance(content, (list, tuple)):
            for item in content:
                if y < 2.5 * cm:
                    c.showPage()
                    y = H - 2.5 * cm
                c.drawString(2.3 * cm, y, f"•  {item}")
                y -= 0.48 * cm
        else:
            text = str(content)
            for line in _wrap_text(text, 95):
                if y < 2.5 * cm:
                    c.showPage()
                    y = H - 2.5 * cm
                c.drawString(2.3 * cm, y, line)
                y -= 0.48 * cm
        y -= 0.4 * cm

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()


def _wrap_text(text, width):
    words = text.split()
    lines, cur = [], ""
    for w in words:
        if len(cur) + len(w) + 1 <= width:
            cur = (cur + " " + w).strip()
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def generate_verification_report(user, profile_extra, sections: dict, verification_code):
    """
    Builds a comprehensive, future-verifiable PDF report combining a user's
    profile snapshot, assessment history, and AI recommendations.
    Includes a verification code + generation timestamp for authenticity checks.
    """
    buf = io.BytesIO()
    W, H = A4
    c = canvas.Canvas(buf, pagesize=A4)
    y = H - 2.6 * cm

    def new_page():
        nonlocal y
        c.showPage()
        y = H - 2.5 * cm

    # Header band
    c.setFillColor(PRIMARY)
    c.rect(0, H - 2.2 * cm, W, 2.2 * cm, fill=1, stroke=0)
    c.setFillColor(HexColor("#FFFFFF"))
    c.setFont("Helvetica-Bold", 17)
    c.drawString(1.5 * cm, H - 1.4 * cm, "🌐 TalentSphere Elevate — Profile Verification Report")

    c.setFillColor(DARK)
    c.setFont("Helvetica-Bold", 20)
    c.drawString(2 * cm, y, user.get("fullname", ""))
    y -= 0.6 * cm
    c.setFont("Helvetica", 11)
    c.setFillColor(HexColor("#636E72"))
    c.drawString(2 * cm, y, f"{user.get('category','')}  |  {user.get('email','')}  |  {user.get('mobile','')}")
    y -= 0.5 * cm
    c.drawString(2 * cm, y, f"Generated on: {datetime.now().strftime('%d %B %Y, %I:%M %p')}   |   Verification Code: {verification_code}")
    y -= 0.9 * cm

    # Profile snapshot section
    if profile_extra:
        c.setFillColor(SECONDARY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2 * cm, y, "Profile Snapshot")
        y -= 0.55 * cm
        c.setFillColor(DARK)
        c.setFont("Helvetica", 10.5)
        for k, v in profile_extra.items():
            if not v:
                continue
            if y < 3 * cm:
                new_page()
            label = k.replace("_", " ").title()
            c.drawString(2.3 * cm, y, f"•  {label}: {v}")
            y -= 0.45 * cm
        y -= 0.4 * cm

    for heading, content in sections.items():
        if y < 3 * cm:
            new_page()
        c.setFillColor(SECONDARY)
        c.setFont("Helvetica-Bold", 13)
        c.drawString(2 * cm, y, heading)
        y -= 0.55 * cm
        c.setFillColor(DARK)
        c.setFont("Helvetica", 10.5)

        if isinstance(content, (list, tuple)):
            for item in content:
                if y < 2.5 * cm:
                    new_page()
                wrapped = _wrap_text(str(item), 95)
                for i, line in enumerate(wrapped):
                    prefix = "•  " if i == 0 else "   "
                    if y < 2.5 * cm:
                        new_page()
                    c.drawString(2.3 * cm, y, f"{prefix}{line}")
                    y -= 0.45 * cm
        else:
            for line in _wrap_text(str(content), 95):
                if y < 2.5 * cm:
                    new_page()
                c.drawString(2.3 * cm, y, line)
                y -= 0.45 * cm
        y -= 0.4 * cm

    # Footer verification strip on last page
    c.setFillColor(HexColor("#636E72"))
    c.setFont("Helvetica-Oblique", 8.5)
    c.drawString(2 * cm, 1.3 * cm, f"This report was generated by TalentSphere Elevate and can be re-verified using code {verification_code}.")

    c.showPage()
    c.save()
    buf.seek(0)
    return buf.getvalue()
