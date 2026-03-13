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

    def is_close(self, c, target_list, threshold=0.1):
        if not c: return False
        if not isinstance(target_list, list): target_list = [target_list]
        for target in target_list:
            if all(abs(a - b) < threshold for a, b in zip(c, target)):
                return True
        return False

    def get_context_bg_color(self, page, rect):
        """박스 주변의 배경색을 동적으로 감지"""
        # 박스보다 약간 큰 영역에서 드로잉 요소들을 찾아 배경색 파악
        drawings = page.get_drawings()
        # 박스를 포함하는 가장 작은(하지만 박스보다는 큰) 채워진 사각형 찾기
        bg_candidates = []
        for d in drawings:
            if d.get("fill") and not self.is_close(d.get("fill"), self.RED_COLOR):
                d_rect = fitz.Rect(d["rect"])
                if d_rect.contains(rect) and d_rect.width > rect.width:
                    bg_candidates.append(d)
        
        if bg_candidates:
            # 면적이 가장 작은 후보(가장 밀접한 배경)의 색상 반환
            bg_candidates.sort(key=lambda x: fitz.Rect(x["rect"]).width * fitz.Rect(x["rect"]).height)
            return bg_candidates[0]["fill"]
        
        # 후보가 없으면 기본 라벨 배경색(Black) 반환
        return self.BG_BLACK

    def discover_regions(self, item_id):
        pdf_path = os.path.join(self.template_dir, f"{item_id}.pdf")
        if not os.path.exists(pdf_path): return {}

        doc = fitz.open(pdf_path)
        page = doc[0]
        paths = page.get_drawings()
        
        text_dict = page.get_text("rawdict")
        all_spans = []
        for b in text_dict["blocks"]:
            if "lines" in b:
                for l in b["lines"]:
                    for s in l["spans"]:
                        txt = s["text"].strip().lower().replace("\n", "").replace(" ", "")
                        if txt: all_spans.append({"text": txt, "rect": fitz.Rect(s["bbox"])})
        
        markers = []
        boxes = []
        
        for p in paths:
            rect = fitz.Rect(p["rect"])
            stroke = p.get("color")
            fill = p.get("fill")
            
            if self.is_close(stroke, self.RED_COLOR):
                boxes.append(rect)
                continue
            
            if self.is_close(fill, self.GREEN_COLORS) or self.is_close(stroke, self.GREEN_COLORS):
                if rect.width < 35 and rect.height < 35:
                    marker_text = ""
                    search_rect = rect * 3.0
                    for s in all_spans:
                        if search_rect.intersects(s["rect"]):
                            txt = s["text"]
                            if re.match(r'^[a-z](-\d+)?$', txt) or re.match(r'^w-\d+$', txt) or re.match(r'^z(-\d+)?$', txt):
                                marker_text = txt
                                break
                    if marker_text:
                        markers.append({"id": marker_text, "rect": rect})

        mapping = {}
        for m in markers:
            m_id = m["id"]
            m_center = m["rect"].center
            for b in boxes:
                dist = b.distance_to(m_center)
                if dist < 120:
                    if m_id not in mapping: mapping[m_id] = {"boxes": [], "markers": []}
                    if b not in mapping[m_id]["boxes"]: mapping[m_id]["boxes"].append(b)
                    if m["rect"] not in mapping[m_id]["markers"]: mapping[m_id]["markers"].append(m["rect"])
        
        doc.close()
        return mapping

    def generate_label(self, item_id, active_data, output_path):
        pdf_path = os.path.join(self.template_dir, f"{item_id}.pdf")
        if not os.path.exists(pdf_path): return None

        doc = fitz.open(pdf_path)
        page = doc[0]
        regions = self.discover_regions(item_id)
        active_indices = list(active_data.keys())
        
        for idx, info in regions.items():
            # 주변 배경색 감지
            bg_color = self.get_context_bg_color(page, info["boxes"][0] if info["boxes"] else info["markers"][0])
            
            # 박스 지우기
            for rect in info["boxes"]:
                # 배경색에 맞춰 채우기 (동적 감지된 bg_color 사용)
                page.draw_rect(rect, color=bg_color, fill=bg_color, overlay=True)
            
            # 마커 지우기
            for rect in info["markers"]:
                page.draw_rect(rect, color=bg_color, fill=bg_color, overlay=True)

            # 활성 필드 텍스트 합성
            if idx in active_indices:
                val = str(active_data[idx])
                if val and val != "[MARK]" and info["boxes"]:
                    rect = info["boxes"][0]
                    # 배경색이 밝으면(White계열) 검정색 글자, 어두우면(Black계열) 흰색 글자
                    text_color = (0, 0, 0) if sum(bg_color) > 1.5 else (1, 1, 1)
                    font_size = min(rect.height * 0.8, 10)
                    page.insert_text(
                        fitz.Point(rect.x0 + 1, rect.y1 - (rect.height * 0.2)), 
                        val, 
                        fontsize=font_size, 
                        color=text_color, 
                        fontname=self.default_font
                    )
        
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        doc.save(output_path)
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
