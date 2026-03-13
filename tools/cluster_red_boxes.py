import fitz
import json

def get_merged_rects(pdf_path, pages=[4, 5, 6]):
    doc = fitz.open(pdf_path)
    results = {}
    
    TARGET_RED = (0.93, 0.11, 0.14)
    
    for pno in pages:
        page = doc[pno]
        drawings = page.get_drawings()
        red_segments = []
        for d in drawings:
            s_color = d.get("color")
            f_color = d.get("fill")
            is_red = False
            for c in [s_color, f_color]:
                if c and len(c) == 3:
                    if abs(c[0] - TARGET_RED[0]) < 0.05 and abs(c[1] - TARGET_RED[1]) < 0.05 and abs(c[2] - TARGET_RED[2]) < 0.05:
                        is_red = True
                        break
            if is_red:
                rect = d.get("rect")
                if rect and rect.width > 0 and rect.height > 0:
                    red_segments.append(rect)
        
        if not red_segments:
            print(f"Page {pno+1}: No red segments found")
            continue
            
        # 1차 병합
        merged = []
        for r in red_segments:
            assigned = False
            for i, m in enumerate(merged):
                expanded_m = fitz.Rect(m.x0-10, m.y0-10, m.x1+10, m.y1+10)
                if expanded_m.intersect(r).is_valid:
                    merged[i] = m.include_rect(r)
                    assigned = True
                    break
            if not assigned:
                merged.append(r)
        
        # 2차 병합
        final_boxes = []
        for b in merged:
            assigned = False
            for i, f in enumerate(final_boxes):
                expanded_f = fitz.Rect(f.x0-5, f.y0-5, f.x1+5, f.y1+5)
                if expanded_f.intersect(b).is_valid:
                    final_boxes[i] = f.include_rect(b)
                    assigned = True
                    break
            if not assigned:
                final_boxes.append(b)
        
        final_boxes = [b for b in final_boxes if b.width > 5 and b.height > 3]
        
        # 라벨 그룹화: 인접한 빨간 박스들끼리 묶어 하나의 라벨로 간주
        labels = []
        for b in final_boxes:
            assigned = False
            for l in labels:
                # 라벨 하나의 크기가 보통 400x300pt 내외이므로 400pt 여유
                l_rect = l["rect"]
                expanded_l = fitz.Rect(l_rect.x0-100, l_rect.y0-100, l_rect.x1+100, l_rect.y1+100)
                if expanded_l.intersect(b).is_valid:
                    l["rect"] = l_rect.include_rect(b)
                    l["fields"].append(b)
                    assigned = True
                    break
            if not assigned:
                labels.append({"rect": b, "fields": [b]})
        
        # 각 라벨의 필드 정렬 및 텍스트 추출
        final_labels = []
        for i, l in enumerate(labels):
            fields = []
            for fb in sorted(l["fields"], key=lambda x: (x.y0, x.x0)):
                text = page.get_text("text", clip=fb).strip().replace("\n", " ")
                fields.append({"rect": [round(fb.x0,2), round(fb.y0,2), round(fb.x1,2), round(fb.y1,2)], "text": text})
            
            # 라벨 상단 텍스트를 조사하여 이름 추측
            name_rect = fitz.Rect(l["rect"].x0, l["rect"].y0 - 40, l["rect"].x1, l["rect"].y0)
            name = page.get_text("text", clip=name_rect).strip().split("\n")[0]
            if not name: name = f"LABEL_{i+1}"
            
            final_labels.append({"name": name, "fields": fields})
            
        results[pno+1] = final_labels
        print(f"Page {pno+1}: Detected {len(final_labels)} labels")
        for fl in final_labels:
            print(f"  - {fl['name']}: {len(fl['fields'])} fields")
            
    with open("src/variable_fields_analysis.json", "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    return results

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    get_merged_rects(pdf_path)
