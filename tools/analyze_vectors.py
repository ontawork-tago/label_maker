import fitz  # PyMuPDF
import json
from pathlib import Path

def analyze_pdf_vectors(pdf_path):
    doc = fitz.open(pdf_path)
    analysis = []
    
    for page_num in range(len(doc)):
        page = doc[page_num]
        drawings = page.get_drawings()
        
        # 사각형 모양만 필터링 (라벨 외곽선 후보)
        rects = []
        for d in drawings:
            # fill 또는 stroke가 있는 사각형 찾기
            for item in d["items"]:
                if item[0] == "re": # rectangle
                    rects.append({
                        "rect": list(item[1]), # [x0, y0, x1, y1]
                        "width": item[1].width,
                        "height": item[1].height,
                        "color": d.get("color"),
                        "fill": d.get("fill")
                    })
        
        analysis.append({
            "page": page_num + 1,
            "page_size": [page.rect.width, page.rect.height],
            "detected_rects": rects
        })
        
    doc.close()
    return analysis

if __name__ == "__main__":
    pdf_file = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    if Path(pdf_file).exists():
        results = analyze_pdf_vectors(pdf_file)
        print(json.dumps(results, indent=2))
    else:
        print(f"File not found: {pdf_file}")
