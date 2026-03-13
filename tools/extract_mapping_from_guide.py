import fitz
import os
import pandas as pd
import re

def analyze_mapping_from_guide(pdf_path):
    doc = fitz.open(pdf_path)
    
    # tools/extract_label_pdfs.py의 PAGE_CONFIG와 동일하게 가져옴
    PAGE_CONFIG = {
        5: ["ITEM_01", "ITEM_04", "ITEM_02", "ITEM_05", "ITEM_03", "ITEM_06"],
        6: ["ITEM_07", "ITEM_10", "ITEM_08", "ITEM_11", "ITEM_09", "ITEM_12"],
        7: ["ITEM_13", "ITEM_16", "ITEM_14", "ITEM_17", "ITEM_15", "ITEM_18"],
        8: ["ITEM_19", "ITEM_22", "ITEM_20", "ITEM_23", "ITEM_21", "ITEM_24"],
        9: ["ITEM_25", "ITEM_28", "ITEM_26", "ITEM_29", "ITEM_27", "ITEM_30"],
        10: ["ITEM_31", "ITEM_34", "ITEM_32", "ITEM_35", "ITEM_33", "ITEM_36"],
        11: ["ITEM_37", "ITEM_38", "ITEM_39"]
    }
    
    # 39개 향지별 발견된 필드를 저장할 딕셔너리
    found_mapping = {item: [] for sublist in PAGE_CONFIG.values() for item in sublist}
    
    for page_num, item_names in PAGE_CONFIG.items():
        if page_num > len(doc): continue
        page = doc[page_num - 1]
        
        # 1. 메인 라벨 프레임 감지 (어두운 사각형)
        drawings = page.get_drawings()
        main_frames = []
        for d in drawings:
            fill = d.get("fill")
            rect = fitz.Rect(d.get("rect"))
            # 메인 라벨 사이즈 (어두운 배경)
            if fill and sum(fill) < 1.2 and 220 < rect.width < 380 and 70 < rect.height < 180:
                is_duplicate = False
                for mf in main_frames:
                    if mf.contains(rect): is_duplicate = True; break
                if not is_duplicate:
                    main_frames.append(rect)
        
        main_frames.sort(key=lambda r: (round(r.y0 / 80), r.x0))
        print(f"Page {page_num}: Found {len(main_frames)} main frames. Expected {len(item_names)}")
        
        # 2. 텍스트 마커 추출
        text_dict = page.get_text("rawdict")
        for b in text_dict["blocks"]:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        if "text" in s:
                            txt = s["text"].strip().lower().replace(" ", "")
                            # 마커 패턴 매칭 (a, b, a-1, w-1, z-1 등)
                            if re.match(r'^[a-z]$|^[a-z]-\d+$|^w-\d+$|^z(-\d+)?$', txt):
                                marker_rect = fitz.Rect(s["bbox"])
                                
                                best_itm = ""
                                min_dist = 1000
                                for i, mf in enumerate(main_frames):
                                    if i < len(item_names):
                                        # 우측 보조 프레임(Japan, Korea 등) 대응을 위해 x1을 대폭 확장 (+400px)
                                        extended_zone = fitz.Rect(mf.x0 - 60, mf.y0 - 60, mf.x1 + 400, mf.y1 + 60)
                                        if extended_zone.contains(marker_rect.center):
                                            itm = item_names[i]
                                            dist = marker_rect.center.distance_to(mf.center)
                                            if dist < min_dist:
                                                min_dist = dist
                                                best_itm = itm
                                
                                if best_itm:
                                    if txt not in found_mapping[best_itm]:
                                        found_mapping[best_itm].append(txt)

    doc.close()
    return found_mapping

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    mapping = analyze_mapping_from_guide(pdf_path)
    
    # 결과를 CSV로 저장
    flattened = []
    for itm, fields in mapping.items():
        for f in fields:
            flattened.append({"ITEM": itm, "Field": f})
    
    df = pd.DataFrame(flattened)
    os.makedirs("data/ID", exist_ok=True)
    df.to_csv("data/ID/detected_mapping.csv", index=False)
    print(f"Mapping saved to data/ID/detected_mapping.csv. Total mapping count: {len(df)}")
