import fitz
import json

def analyze_page_8(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[7] # Page 8
    
    TARGET_RED = (0.93, 0.11, 0.14)
    drawings = page.get_drawings()
    red_segments = []
    
    for d in drawings:
        # s_color(stroke), f_color(fill) 모두 확인
        s_color = d.get("color")
        f_color = d.get("fill")
        
        is_red = False
        for c in [s_color, f_color]:
            if c and len(c) == 3:
                # 색상 오차 허용 범위를 0.10으로 확대
                if abs(c[0] - TARGET_RED[0]) < 0.10 and abs(c[1] - TARGET_RED[1]) < 0.10 and abs(c[2] - TARGET_RED[2]) < 0.10:
                    is_red = True
                    break
        if is_red:
            rect = d.get("rect")
            if rect and rect.width > 0 and rect.height > 0:
                red_segments.append(rect)
                
    print(f"Detected {len(red_segments)} red segments on Page 8")
    
    if not red_segments:
        return
        
    # 병합 로직 (점선끼리 묶기 위해 20pt 여유)
    merged = []
    for r in red_segments:
        assigned = False
        for i, m in enumerate(merged):
            expanded_m = fitz.Rect(m.x0-20, m.y0-20, m.x1+20, m.y1+20)
            if expanded_m.intersect(r).is_valid:
                merged[i] = m.include_rect(r)
                assigned = True
                break
        if not assigned:
            merged.append(r)
            
    # 필드 추출 (면적 기준 필터링)
    variable_fields = [b for b in merged if b.width > 5 and b.height > 3]
    print(f"Merged into {len(variable_fields)} variable fields")
    
    # 그룹화 (기하학적 배치)
    results = {}
    label_positions = {
        "ITEM 19": fitz.Rect(0, 0, 595, 280),
        "ITEM 22": fitz.Rect(595, 0, 1190, 280),
        "ITEM 20": fitz.Rect(0, 280, 595, 560),
        "ITEM 23": fitz.Rect(595, 280, 1190, 560),
        "ITEM 21": fitz.Rect(0, 560, 595, 840),
        "ITEM 24": fitz.Rect(595, 560, 1190, 840)
    }
    
    for item_name, area in label_positions.items():
        fields = []
        for b in variable_fields:
            if area.contains(b):
                text = page.get_text("text", clip=b).strip().replace("\n", " ")
                fields.append({
                    "rect": [round(b.x0,2), round(b.y0,2), round(b.x1,2), round(b.y1,2)],
                    "text": text
                })
        fields.sort(key=lambda x: (x["rect"][1], x["rect"][0]))
        results[item_name] = fields
        print(f"{item_name}: Found {len(fields)} fields")

    output_path = "src/variable_fields_p8.json"
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    print(f"Successfully saved results to {output_path}")
    
    return results

if __name__ == "__main__":
    analyze_page_8("data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf")
