import fitz
import sys
import os

pdf_path = 'assets/templates/ID/ITEM_23_WN_Argentina.pdf'
doc = fitz.open(pdf_path)
page = doc[0]
print(f"Page Rect: {page.rect}")

drawings = page.get_drawings()
print(f"Total drawings: {len(drawings)}")

for i, d in enumerate(drawings):
    rect = fitz.Rect(d["rect"])
    fill = d.get("fill")
    stroke = d.get("color")
    if fill or stroke:
        # 가시 범위(0,0 ~ 300, 150) 내에 있는 것들 위주로 출력
        if rect.x0 > -100 and rect.x0 < 400:
            print(f"Drawing {i}: {rect}, fill={fill}, stroke={stroke}")

print("--- Text Check ---")
text_dict = page.get_text("rawdict")
for b in text_dict['blocks']:
    if 'lines' in b:
        for l in b['lines']:
            for s in l['spans']:
                print(f" Text: '{s['text']}' at {s['bbox']}")

doc.close()
