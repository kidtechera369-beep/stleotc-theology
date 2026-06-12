#!/usr/bin/env python3
"""
Generates a printable study guide PDF for every lesson in build.py.
Run AFTER build.py edits:  python3 make_study_guides.py
Outputs: downloads/<Slug>_StudyGuide.pdf
"""
import os, re, importlib.util
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib.colors import HexColor
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, HRFlowable, ListFlowable, ListItem

ROOT = os.path.dirname(os.path.abspath(__file__))

# load LESSONS from build.py without re-running the site build
src = open(os.path.join(ROOT, "build.py"), encoding="utf-8").read()
src = src.split("# ---------------------------------------------------------------\n# Category themes")[0] + \
      src.split("# Category themes: accent color, icon (inline SVG), special-section kind\n# ---------------------------------------------------------------")[1].split("def page(")[0]
ns = {"__file__": os.path.join(ROOT, "build.py")}
exec(compile(src, "build_data", "exec"), ns)
LESSONS = ns["LESSONS"]

MAROON = HexColor("#6e1e1e")
GOLD = HexColor("#b07d2b")
GREEN = HexColor("#1f4d2e")

styles = getSampleStyleSheet()
S = dict(
 title=ParagraphStyle("t", parent=styles["Title"], textColor=MAROON, fontName="Times-Bold", fontSize=19, spaceAfter=2),
 byline=ParagraphStyle("b", parent=styles["Normal"], fontName="Times-Italic", textColor=GREEN, alignment=1, fontSize=11, spaceAfter=10),
 h=ParagraphStyle("h", parent=styles["Heading2"], textColor=MAROON, fontName="Times-Bold", fontSize=13, spaceBefore=12, spaceAfter=4),
 body=ParagraphStyle("n", parent=styles["Normal"], fontName="Times-Roman", fontSize=10.5, leading=14),
 verse=ParagraphStyle("v", parent=styles["Normal"], fontName="Times-Italic", fontSize=10.5, leading=14, textColor=GREEN, leftIndent=14, spaceAfter=3),
 footer=ParagraphStyle("f", parent=styles["Normal"], fontName="Times-Italic", fontSize=8.5, textColor=GREEN, alignment=1),
)

def sg_name(l):
    return re.sub(r'_Lesson_Slides\.pptx$|_Lesson_Notes\.docx$', '', l["file"]) + "_StudyGuide.pdf"

def bullets(items):
    return ListFlowable([ListItem(Paragraph(x, S["body"]), leftIndent=16) for x in items],
                        bulletType="bullet", bulletFontSize=8, leftIndent=14)

for l in LESSONS:
    out = os.path.join(ROOT, "downloads", sg_name(l))
    doc = SimpleDocTemplate(out, pagesize=letter, topMargin=0.7*inch, bottomMargin=0.7*inch,
                            leftMargin=0.85*inch, rightMargin=0.85*inch,
                            title=l["title"] + " — Study Guide", author="Dn Yonnas")
    story = [
        Paragraph("&#10016; Study Guide &#10016;", S["byline"]),
        Paragraph(l["title"], S["title"]),
        Paragraph("By Dn Yonnas &middot; " + l["category"] + " &middot; " + l["audience"], S["byline"]),
        HRFlowable(width="100%", thickness=1.2, color=GOLD),
        Paragraph("Summary", S["h"]), Paragraph(l["summary"], S["body"]),
        Paragraph("Lesson Objectives", S["h"]), bullets(l["objectives"]),
        Paragraph("Key Bible Verses", S["h"]),
    ]
    story += [Paragraph(v, S["verse"]) for v in l["verses"]]
    story += [Paragraph("Main Teaching Points", S["h"]), bullets(l["points"])]
    if l.get("terms"):
        story += [Paragraph("Key Terms", S["h"]),
                  bullets([f"<b>{t}</b> — {d}" for t, d in l["terms"]])]
    story += [Paragraph("Discussion &amp; Reflection", S["h"]), bullets(l["discussion"])]
    story += [Spacer(1, 14), HRFlowable(width="100%", thickness=1.2, color=GOLD), Spacer(1, 4),
              Paragraph("Debre Nazreth St. Mary &amp; St. Gabriel Ethiopian Orthodox Tewahedo Church — STL Theology Class", S["footer"]),
              Paragraph("Glory be to the Father, the Son, and the Holy Spirit, one God. Amen.", S["footer"])]
    doc.build(story)
    print("wrote downloads/" + sg_name(l))
print(f"\n{len(LESSONS)} study guides generated.")
