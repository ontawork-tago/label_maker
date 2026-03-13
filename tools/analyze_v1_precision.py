import fitz
import json
import os

def analyze_v1_labels(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[7] # Page 8
    drawings = page.get_drawings()
    
    # 1. 검정 프레임 감지
    black_frames = []
    for d in drawings:
        fill = d.get("fill")
        rect = d.get("rect")
        if fill and all(c < 0.2 for c in fill) and rect.width > 200 and rect.height > 100:
            should_add = True
            for i, existing in enumerate(black_frames):
                if existing.contains(rect): should_add = False; break
                if rect.contains(existing): black_frames[i] = rect; should_add = False; break
            if should_add: black_frames.append(rect)
    
    black_frames.sort(key=lambda r: (r.y0, r.x0))
    print(f"Analyzing {len(black_frames)} frames...")

    # 2. 초록색 인덱스 감기 (Page 4에서 정의된 것과 동일한 LG Green)
    # 8페이지에도 인덱스 원이 있음
    green_drawings = [d for d in drawings if d.get("fill") and d["fill"][1] > 0.4 and d["fill"][0] < 0.2]
    
    label_configs = {}
    
    DEST_NAMES = [
        "ITEM_19_Colombia", "ITEM_22_Algeria",
        "ITEM_20_Mexico",   "ITEM_23_Argentina",
        "ITEM_21_Brazil",   "ITEM_24_UAE"
    ]
    
    for i, frame in enumerate(black_frames):
        # 템플릿 이름 매칭 (extract_label_pdfs.py와 동일하게)
        label_id = DEST_NAMES[i] if i < len(DEST_NAMES) else f"ITEM_UNKNOWN_{i+1}"
        
        # 실제 헤더 텍스트 추출 시도 (UI 표시용)
        header_rect = fitz.Rect(frame.x0, frame.y0 - 35, frame.x1, frame.y0)
        header_text = page.get_text("text", clip=header_rect).strip().split('\n')[0]
        if not header_text: header_text = label_id
        
        print(f"Processing: {label_id}")
        
        # 프레임 내부의 레드 박스(데이터 영역) 찾기
        item_fields = []
        for d in drawings:
            if d.get("color") and d["color"][0] > 0.8 and d["color"][1] < 0.2 and frame.contains(d["rect"]):
                rb = d["rect"]
                rel_x = rb.x0 - frame.x0
                rel_y = rb.y0 - frame.y0
                
                # 주변 초록 인덱스 찾기 (확장 영역에서 검색)
                field_index = ""
                # Rect 확장 (수동 계산)
                expanded_rb = fitz.Rect(rb.x0 - 5, rb.y0 - 5, rb.x1 + 5, rb.y1 + 5)
                for gd in green_drawings:
                    if rb.contains(gd["rect"]) or gd["rect"].intersects(expanded_rb):
                         idx_text = page.get_text("text", clip=gd["rect"]).strip()
                         if idx_text: field_index = idx_text; break
                
                item_fields.append({
                    "index": field_index,
                    "pos": [round(rel_x, 1), round(rel_y, 1)],
                    "size": 7 # Default
                })
        
        label_configs[label_id] = {
            "name": header_text,
            "template": label_id,
            "layout": item_fields
        }

    # config.json 형식으로 출력
    final_config = {
        "default_values": {
            "sales_model_name": "LED-OS-ALPHA",
            "product_name": "LED MONITOR",
            "product_code": "LED-OS.SUFFIX",
            "power": "AC 100-240V~ 50/60Hz 1.5A",
            "origin": "MADE IN CHINA",
            "serial_no": "S12345678S",
            "manufacture_date": "06/2020"
        },
        "destinations": label_configs
    }
    
    with open("src/config.json", "w", encoding="utf-8") as f:
        json.dump(final_config, f, indent=4, ensure_ascii=False)
    
    print("Updated src/config.json with precision vector mapping.")

if __name__ == "__main__":
    analyze_v1_labels("data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf")
