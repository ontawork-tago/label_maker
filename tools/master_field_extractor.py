import fitz
import pandas as pd
import os

def extract_perfect_mapping(pdf_path, page_num):
    doc = fitz.open(pdf_path)
    page = doc[page_num - 1]
    blocks = page.get_text("dict")["blocks"]
    
    spans = []
    for b in blocks:
        if b["type"] == 0:
            for l in b["lines"]:
                for s in l["spans"]:
                    spans.append(s)
    
    # 인덱스 후포들 (보통 작은 숫자/문자)
    indices = []
    potential_labels = []
    
    for s in spans:
        txt = s["text"].strip()
        # 인덱스 패턴 매칭 (a, a-1, b, w-1, z-1 등)
        if 1 <= len(txt) <= 5:
            indices.append(s)
        else:
            potential_labels.append(s)
            
    # 매핑 결과
    mapping = []
    
    # 각 인덱스에 대해 가장 가까운 오른쪽에 있는 텍스트 찾기
    for idx_s in indices:
        idx_txt = idx_s["text"].strip()
        if not idx_txt: continue
        
        # 인덱스 오른쪽에 있는 텍스트들 필터링
        idx_rect = fitz.Rect(idx_s["bbox"])
        closest_label = None
        min_dist = 1000
        
        for lbl_s in spans:
            if lbl_s == idx_s: continue
            lbl_txt = lbl_s["text"].strip()
            if not lbl_txt or len(lbl_txt) < 3: continue
            
            lbl_rect = fitz.Rect(lbl_s["bbox"])
            # y좌표가 비슷하고 (약 10px 내외)
            if abs(idx_rect.y0 - lbl_rect.y0) < 15:
                # x좌표가 인덱스보다 크고 가깝다면
                dist = lbl_rect.x0 - idx_rect.x1
                if 0 < dist < 200: # 200px 이상 차이나면 다른 컬럼일 가능성
                    if dist < min_dist:
                        min_dist = dist
                        closest_label = lbl_s
        
        if closest_label:
            full_text = closest_label["text"].strip()
            # 영문 : 한글 분리 시도
            if ":" in full_text:
                parts = full_text.split(":")
                eng = parts[0].strip()
                kor = parts[1].strip()
            elif " " in full_text:
                # 공백으로 분리 (영어 단어들이 많을 수 있으니 뒤에서부터 한국어 찾기 등)
                parts = full_text.rsplit(" ", 1)
                eng = parts[0].strip()
                kor = parts[1].strip()
            else:
                eng = full_text
                kor = ""
                
            mapping.append({
                "Index": idx_txt,
                "English": eng,
                "Korean": kor,
                "Full": full_text
            })
            
    return mapping

if __name__ == "__main__":
    pdf_path = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    mapping = extract_perfect_mapping(pdf_path, 4)
    df = pd.DataFrame(mapping)
    # 중복 제거 및 정렬
    df = df.drop_duplicates(subset=["Index", "Full"])
    df.to_excel("data/ID/raw_field_mapping.xlsx", index=False)
    print(f"Extracted {len(df)} fields to data/ID/raw_field_mapping.xlsx")
