import fitz
from pathlib import Path

def find_id_label_boxes(pdf_path):
    doc = fitz.open(pdf_path)
    page = doc[0]
    drawings = page.get_drawings()
    
    # 가로/세로 비율이 ID 라벨과 유사한 사각형들 찾기 (예: 가로가 더 긴 직사각형)
    # 또한 너무 작거나(로고 일부) 너무 큰(배경) 것은 제외
    potential_labels = []
    for d in drawings:
        for item in d["items"]:
            if item[0] == "re":
                r = item[1]
                # ID 라벨 대략적인 크기 (pt 단위로 100~300 사이)
                if 100 < r.width < 400 and 50 < r.height < 250:
                    potential_labels.append(r)
    
    # 중복 제거 (비슷한 좌표)
    unique_labels = []
    for r in potential_labels:
        is_duplicate = False
        for u in unique_labels:
            if abs(r.x0 - u.x0) < 5 and abs(r.y0 - u.y0) < 5:
                is_duplicate = True
                break
        if not is_duplicate:
            unique_labels.append(r)
            
    doc.close()
    return unique_labels

if __name__ == "__main__":
    pdf_file = "data/LMEA012_Label/Label/MEZ68824201_LED OS ID_1.7.pdf"
    labels = find_id_label_boxes(pdf_file)
    print(f"Detected {len(labels)} ID Labels on Page 1:")
    for i, r in enumerate(labels):
        print(f"Label {i+1}: Rect({r.x0:.2f}, {r.y0:.2f}, {r.x1:.2f}, {r.y1:.2f}) - Size({r.width:.2f} x {r.height:.2f})")
