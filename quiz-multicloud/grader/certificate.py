"""Dynamic PDF generation (certificate when passed, result slip otherwise) with fpdf2."""
import os

from fpdf import FPDF

FONT_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts")


def build_certificate(*, student_name, exam_title, score, max_score, percent, passed, issued_at, cert_id):
    pdf = FPDF(orientation="L", unit="mm", format="A4")
    pdf.set_auto_page_break(False)
    pdf.add_page()
    # Core PDF fonts cannot render Vietnamese, so a bundled Unicode TTF is required.
    pdf.add_font("DejaVu", "", os.path.join(FONT_DIR, "DejaVuSans.ttf"))
    pdf.add_font("DejaVu", "B", os.path.join(FONT_DIR, "DejaVuSans-Bold.ttf"))

    accent = (20, 90, 160) if passed else (120, 120, 120)
    pdf.set_draw_color(*accent)
    pdf.set_line_width(2.5)
    pdf.rect(10, 10, 277, 190)
    pdf.set_line_width(0.6)
    pdf.rect(15, 15, 267, 180)

    pdf.set_text_color(*accent)
    pdf.set_font("DejaVu", "B", 32)
    pdf.set_xy(15, 38)
    title = "CHỨNG NHẬN HOÀN THÀNH" if passed else "PHIẾU KẾT QUẢ BÀI THI"
    pdf.cell(267, 14, title, align="C")

    pdf.set_text_color(60, 60, 60)
    pdf.set_font("DejaVu", "", 15)
    pdf.set_xy(15, 64)
    pdf.cell(267, 10, "Xác nhận thí sinh", align="C")

    pdf.set_text_color(0, 0, 0)
    pdf.set_font("DejaVu", "B", 28)
    pdf.set_xy(15, 78)
    pdf.cell(267, 14, student_name, align="C")

    pdf.set_font("DejaVu", "", 15)
    pdf.set_xy(15, 100)
    verb = "đã hoàn thành xuất sắc bài thi" if passed else "đã tham gia bài thi"
    pdf.cell(267, 10, verb, align="C")

    pdf.set_font("DejaVu", "B", 20)
    pdf.set_xy(25, 113)
    pdf.multi_cell(247, 10, exam_title, align="C")

    pdf.set_font("DejaVu", "", 16)
    pdf.set_xy(15, 140)
    pdf.cell(267, 10, f"Điểm: {score:g}/{max_score:g}  ({percent:g}%)", align="C")

    pdf.set_font("DejaVu", "", 10)
    pdf.set_text_color(90, 90, 90)
    pdf.set_xy(25, 178)
    pdf.cell(120, 6, f"Ngày cấp: {issued_at}")
    pdf.set_xy(152, 178)
    pdf.cell(120, 6, f"Mã chứng nhận: {cert_id}", align="R")

    return bytes(pdf.output())
