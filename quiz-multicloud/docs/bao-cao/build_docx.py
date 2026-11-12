"""Build the report draft as .docx: Times New Roman 12, A4, bordered tables.

Usage: python build_docx.py   (needs: pip install python-docx pypandoc-binary)
"""
import os

import pypandoc
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt, RGBColor

HERE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(HERE, "phan-ly-thuyet.md")
OUT = os.path.join(HERE, "BaoCao-PhanLyThuyet.docx")
REF = os.path.join(HERE, "_reference.docx")
FONT = "Times New Roman"
HEADING_SIZES = {"Title": 16, "Heading 1": 14, "Heading 2": 13, "Heading 3": 12}


def set_font(style_or_run, size=None, bold=None):
    f = style_or_run.font
    f.name = FONT
    f.color.rgb = RGBColor(0, 0, 0)
    if size:
        f.size = Pt(size)
    if bold is not None:
        f.bold = bold
    rpr = style_or_run.element.get_or_add_rPr()
    fonts = rpr.find(qn("w:rFonts"))
    if fonts is None:
        fonts = OxmlElement("w:rFonts")
        rpr.append(fonts)
    # Theme fonts would otherwise override the explicit font for Vietnamese text.
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        fonts.set(qn(attr), FONT)
    for attr in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        fonts.attrib.pop(qn(attr), None)


def build_reference():
    # A pandoc-generated docx carries every style pandoc uses; restyle it and reuse it as the reference.
    pypandoc.convert_text("x", "docx", format="md", outputfile=REF)
    doc = Document(REF)
    for style in doc.styles:
        if style.type != 1:  # paragraph styles only
            continue
        name = style.name
        if name in HEADING_SIZES:
            set_font(style, HEADING_SIZES[name], True)
            style.font.italic = False
        elif name in ("Normal", "Body Text", "First Paragraph", "Compact", "Block Text"):
            set_font(style, 12)
            pf = style.paragraph_format
            pf.line_spacing = 1.3
            pf.space_after = Pt(6)
            if name != "Compact":
                pf.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    doc.save(REF)


def border_tables(doc):
    for table in doc.tables:
        tbl_pr = table._tbl.tblPr
        borders = OxmlElement("w:tblBorders")
        for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
            el = OxmlElement(f"w:{edge}")
            el.set(qn("w:val"), "single")
            el.set(qn("w:sz"), "4")
            el.set(qn("w:color"), "000000")
            borders.append(el)
        tbl_pr.append(borders)
        for i, row in enumerate(table.rows):
            for cell in row.cells:
                for p in cell.paragraphs:
                    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.LEFT
                    p.paragraph_format.space_after = Pt(2)
                    for r in p.runs:
                        set_font(r, 11, True if i == 0 else None)
                if i == 0:
                    shd = OxmlElement("w:shd")
                    shd.set(qn("w:val"), "clear")
                    shd.set(qn("w:fill"), "D9E2F3")
                    cell._tc.get_or_add_tcPr().append(shd)


def main():
    build_reference()
    pypandoc.convert_file(SRC, "docx", outputfile=OUT, extra_args=[f"--reference-doc={REF}"])
    os.remove(REF)
    doc = Document(OUT)
    for section in doc.sections:
        section.page_width, section.page_height = Cm(21), Cm(29.7)
        section.top_margin = section.bottom_margin = Cm(2)
        section.left_margin, section.right_margin = Cm(3), Cm(2)
    for p in doc.paragraphs:
        for r in p.runs:
            set_font(r)
    border_tables(doc)
    doc.save(OUT)
    print("Created", OUT)


if __name__ == "__main__":
    main()
