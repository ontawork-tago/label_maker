import fitz
import os
import re
import pandas as pd

class IDLabelEngine:
    def __init__(self, template_dir="assets/templates/ID"):
        self.template_dir = template_dir
        # 가이드 실측 색상
        self.RED_COLOR = (0.930418848991394, 0.1109025701880455, 0.1414511352777481)
        self.GREEN_COLORS = [
            (0.0, 0.6955825090408325, 0.5287556052207947),
            (0.07278553396463394, 0.6494392156600952, 0.31042954325675964)
        ]
        self.BG_BLACK = (0.13588158786296844, 0.12239261716604233, 0.1250782012939453)
        self.BG_WHITE = (1.0, 1.0, 1.0)
        self.default_font = "helv"

    def is_red(self, c):
        if not c or len(c) != 3: return False
        r, g, b = c
        return r > 0.8 and g < 0.3 and b < 0.3

    def is_green(self, c):
        if not c or len(c) != 3: return False
        r, g, b = c
        return g > 0.4 and g > r and g > b

    def get_context_bg_color(self, page, rect):
        """박스 주변의 배경색을 동적으로 감지"""
        drawings = page.get_drawings()
        bg_candidates = []
        for d in drawings:
            fill = d.get("fill")
            if fill and not self.is_red(fill) and not self.is_green(fill):
                d_rect = fitz.Rect(d["rect"])
                if d_rect.contains(rect) and d_rect.width > rect.width:
                    bg_candidates.append(d)
        
        if bg_candidates:
            bg_candidates.sort(key=lambda x: fitz.Rect(x["rect"]).width * fitz.Rect(x["rect"]).height)
            return bg_candidates[0]["fill"]
        return self.BG_BLACK

    def discover_regions(self, item_id):
        pdf_path = os.path.join(self.template_dir, f"{item_id}.pdf")
        if not os.path.exists(pdf_path): return {}

        doc = fitz.open(pdf_path)
        page = doc[0]
        paths = page.get_drawings()
        
        # 텍스트 스팬 수집 (rawdict보다 더 넓은 범위로 검색하기 위해 미리 수집)
        text_dict = page.get_text("rawdict")
        all_spans = []
        for b in text_dict["blocks"]:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        txt = s["text"].strip().lower().replace(" ", "")
                        if txt: all_spans.append({"text": txt, "rect": fitz.Rect(s["bbox"])})
        
        markers = []
        boxes = []
        
        for p in paths:
            rect = fitz.Rect(p["rect"])
            stroke = p.get("color")
            fill = p.get("fill")
            
            # 레드 박스 (텍스트 입력 구역)
            if self.is_red(stroke) or self.is_red(fill):
                # 아르헨티나 등 일부 템플릿의 박스가 작을 수 있으므로 임계값 완화
                if rect.width > 2 and rect.height > 2:
                    boxes.append(rect)
                continue
            
            # 그린 마커 (필드 ID 원)
            if self.is_green(fill) or self.is_green(stroke):
                if rect.width < 40 and rect.height < 40:
                    marker_id = ""
                    # 마커 내부 또는 아주 주변에 있는 텍스트 찾기
                    search_area = rect + (-5, -5, 5, 5) # 5px씩 확장하여 검색
                    for s in all_spans:
                        if search_area.intersects(s["rect"]):
                            txt = s["text"]
                            if re.match(r'^[a-z]$|^[a-z]-\d+$|^w-\d+$|^z(-\d+)?$', txt):
                                marker_id = txt
                                break
                    if marker_id:
                        markers.append({"id": marker_id, "rect": rect})
                    else:
                        # [NEW] 텍스트가 없는 경우에도 위치 파악을 위해 후보로 보관
                        markers.append({"id": "UNKNOWN", "rect": rect})

        # 마커와 인접한 레드 박스 매핑
        mapping = {}
        
        # [Normalization] 가시 영역 밖의 좌표들을 가시 영역(0,0 ~ page.rect)으로 정합 (Argentina 대응)
        all_rects = [m["rect"] for m in markers] + boxes
        if all_rects:
            content_bbox = all_rects[0]
            for r in all_rects[1:]: content_bbox = content_bbox | r
            
            # 만약 content_bbox가 page.rect를 완전히 벗어난다면 오프셋 계산 (상하좌우 여백 고려)
            # Rect.inset 대신 좌표 연산 사용
            check_rect = fitz.Rect(content_bbox.x0 + 5, content_bbox.y0 + 5, content_bbox.x1 - 5, content_bbox.y1 - 5)
            if not page.rect.contains(check_rect):
                offset_x = -content_bbox.x0 + (page.rect.width - content_bbox.width) / 2
                offset_y = -content_bbox.y0 + (page.rect.height - content_bbox.height) / 2
                # 모든 좌표에 오프셋 적용
                for m in markers: 
                    m["rect"] = m["rect"] + (offset_x, offset_y, offset_x, offset_y)
                boxes = [b + (offset_x, offset_y, offset_x, offset_y) for b in boxes]

        # [Layout Fallback] 텍스트 마커가 0개인 경우 (Argentina 등 대부분의 템플릿)
        unknown_markers = [m for m in markers if m["id"] == "UNKNOWN"]
        if unknown_markers and not any(m["id"] != "UNKNOWN" for m in markers):
            # Y축 기준으로 정렬하여 전형적인 레이아웃 매핑 시도
            unknown_markers.sort(key=lambda x: (x["rect"].y0, x["rect"].x0))
            
            layout_map = {
                0: "a-3", # 제품명칭 (아르헨티나 등)
                1: "b",   # 기기명칭
                2: "c",   # 모델명칭
                3: "d-1", # 정격
                4: "e",   # 일련번호
                5: "f",   # 날짜
                6: "p",   # 원산지
                7: "w-9"  # 무선/인증
            }
            for i, m in enumerate(unknown_markers):
                if i in layout_map:
                    m["id"] = layout_map[i]

        for m in markers:
            if m["id"] == "UNKNOWN": continue
            m_id = m["id"]
            # Rect.center 대신 직접 계산 (AttributeError 방지)
            m_x = (m["rect"].x0 + m["rect"].x1) / 2
            m_y = (m["rect"].y0 + m["rect"].y1) / 2
            m_center = fitz.Point(m_x, m_y)
            
            if m_id not in mapping:
                mapping[m_id] = {"boxes": [], "markers": [m["rect"]]}
            else:
                mapping[m_id]["markers"].append(m["rect"])
            
            # 모든 박스와의 거리 계산 후 가장 가까운 그룹 추출
            candidates = []
            for b in boxes:
                b_x = (b.x0 + b.x1) / 2
                b_y = (b.y0 + b.y1) / 2
                dist = fitz.Point(b_x, b_y).distance_to(m_center)
                if dist < 120: # 최대 유효 거리
                    candidates.append((dist, b))
            
            if candidates:
                candidates.sort(key=lambda x: x[0])
                min_dist = candidates[0][0]
                # 최단 거리와 유사한(20px 이내) 박스들을 모두 선택 (분할된 박스 대응)
                for d, b in candidates:
                    if d <= min_dist + 20:
                        if b not in mapping[m_id]["boxes"]:
                            mapping[m_id]["boxes"].append(b)
        
        doc.close()
        return mapping

    def generate_label(self, item_id, active_data, output_path, png_path=None):
        pdf_path = os.path.join(self.template_dir, f"{item_id}.pdf")
        if not os.path.exists(pdf_path): return None

        doc = fitz.open(pdf_path)
        page = doc[0]
        regions = self.discover_regions(item_id)
        
        for idx, info in regions.items():
            # 주변 배경색 감지 (첫 번째 박스나 마커 기준)
            sample_rect = info["boxes"][0] if info["boxes"] else info["markers"][0]
            bg_color = self.get_context_bg_color(page, sample_rect)
            
            # [USER REQUEST] 가이드 문서를 위해 빨간 박스와 마커를 지우지 않음 (주석 처리)
            # ... 지우기 로직 생략 ...

            # 2. 데이터 합성
            if idx in active_data:
                val = active_data[idx]
                
                # 체크박스인 경우: 가이드 모드이므로 마커가 이미 있으니 별도 드로잉 불필요
                if isinstance(val, bool):
                    continue

                # 텍스트 필드인 경우: 해당 marker(idx)에 연결된 모든 박스에 작성
                txt_val = str(val)
                if txt_val and txt_val != "[MARK]" and info["boxes"]:
                    for rect in info["boxes"]:
                        # 가독성을 위해 배경색에 따른 반전 유지
                        text_color = (0, 0, 0) if sum(bg_color) > 1.5 else (1, 1, 1)
                        font_size = min(rect.height * 0.8, 10.5)
                        # 박스 안에 텍스트 삽입
                        page.insert_text(
                            fitz.Point(rect.x0 + 1, rect.y1 - (rect.height * 0.2)), 
                            txt_val, 
                            fontsize=font_size, 
                            color=text_color, 
                            fontname=self.default_font
                        )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        # 1. PDF 저장
        doc.save(output_path)
        
        # 2. PNG 저장 (사용자 추가 요청)
        try:
            target_png = png_path if png_path else output_path.replace(".pdf", ".png")
            os.makedirs(os.path.dirname(target_png), exist_ok=True)
            
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2)) # 고해상도(2배)로 저장
            pix.save(target_png)
        except Exception as e:
            print(f"PNG 저장 실패: {e}")
            
        doc.close()
        return output_path

def run_batch_generation():
    engine = IDLabelEngine()
    df = pd.read_excel("data/ID/id_mapping_master_super_final.xlsx")
    output_dir = "output/ID/batch"
    item_cols = [col for col in df.columns if col.startswith("ITEM_") and not col.endswith("_Val")]
    
    for item in item_cols:
        active_data = {}
        for _, row in df.iterrows():
            if row[item] == "O":
                idx = row["Index"]
                spec_val_col = f"{item}_Val"
                val = row[spec_val_col] if spec_val_col in df.columns and pd.notna(row[spec_val_col]) else row["Example"]
                active_data[idx] = val
        
        out_path = os.path.join(output_dir, f"{item}_Prod.pdf")
        engine.generate_label(item, active_data, out_path)

if __name__ == "__main__":
    run_batch_generation()
