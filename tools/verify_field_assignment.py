import fitz
import os
import json

def analyze_fields_per_label(pdf_path):
    doc = fitz.open(pdf_path)
    # ITEM 1~24는 5~8페이지에 있음
    PAGE_CONFIG = {
        5: ["ITEM_01", "ITEM_04", "ITEM_02", "ITEM_05", "ITEM_03", "ITEM_06"],
        6: ["ITEM_07", "ITEM_10", "ITEM_08", "ITEM_11", "ITEM_09", "ITEM_12"],
        7: ["ITEM_13", "ITEM_16", "ITEM_14", "ITEM_17", "ITEM_15", "ITEM_18"],
        8: ["ITEM_19", "ITEM_22", "ITEM_20", "ITEM_23", "ITEM_21", "ITEM_24"]
    }
    
    mapping = {}
    
    for page_num in [5, 6, 7, 8]:
        page = doc[page_num - 1]
        drawings = page.get_drawings()
        
        # 1. 라벨 테두리 찾기 (색상 임계값 완화)
        frames = []
        for d in drawings:
            fill = d.get("fill")
            rect = d.get("rect")
            if fill and sum(fill) < 0.7 and 200 < rect.width < 350 and 70 < rect.height < 180:
                should_add = True
                for i, existing in enumerate(frames):
                    if existing.contains(rect): should_add = False; break
                    if rect.contains(existing): frames[i] = rect; should_add = False; break
                if should_add: frames.append(rect)
        
        frames.sort(key=lambda r: (round(r.y0 / 40), r.x0))
        dest_names = PAGE_CONFIG.get(page_num, [])
        
        for i, f_rect in enumerate(frames):
            if i >= len(dest_names): break
            item_id = dest_names[i]
            
            # 프레임 내부 및 주변 텍스트 분석
            exp_rect = fitz.Rect(f_rect.x0 - 10, f_rect.y0 - 10, f_rect.x1 + 10, f_rect.y1 + 10)
            blocks = page.get_text("dict", clip=exp_rect)["blocks"]
            
            fields = []
            for b in blocks:
                if b["type"] == 0:
                    for l in b["lines"]:
                        for s in l["spans"]:
                            txt = s["text"].strip().lower()
                            # 인덱스 패턴 매칭: 'a', 'b', 'a-1', 'z-5', 'v-1' 등
                            # 1~4글자이고 숫자나 기호 포함 가능
                            if len(txt) > 0 and len(txt) <= 5:
                                # 'lg'나 'mm', 'vac' 같은 단위/브랜드 제외
                                if txt not in ["lg", "mm", "vac", "hz", "v~", "v-", "a", "d"]:
                                    # 사용자 가이드의 인덱스는 보통 원 안에 있으며 특정 색상일 확률이 높으나 
                                    # 여기서는 텍스트 패턴과 프레임 내 위치로 판단
                                    fields.append(txt)
                                # 'a','b','c','d','e' 등은 핵심 인덱스이므로 포함
                                if txt in ["a", "b", "c", "d", "e", "f", "g", "h", "p", "s", "t", "u", "v"]:
                                    fields.append(txt)
            
            mapping[item_id] = sorted(list(set(fields)))
            
    doc.close()
    return mapping

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    result = analyze_fields_per_label(pdf_path)
    with open("data/field_presence_mapping.json", "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    print("Field presence mapping saved to data/field_presence_mapping.json")
