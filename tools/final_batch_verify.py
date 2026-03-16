import os
import io
import zipfile
import pandas as pd
from datetime import datetime
import sys

# 프로젝트 경로 추가 (src 폴더 포함)
sys.path.append(os.path.join(os.getcwd(), 'src'))

from engine import IDLabelEngine
from mapping import IDMappingMaster

def run_all_files_verification():
    print(f"[{datetime.now().strftime('%H:%M:%S')}] Starting Full Batch Verification...")
    
    # 1. 초기화
    engine = IDLabelEngine()
    mapping_master = IDMappingMaster("data/ID/id_mapping_master_super_final_v2.xlsx")
    
    output_dir = "output/ID/final_verify"
    os.makedirs(output_dir, exist_ok=True)
    
    items = [col for col in mapping_master.df.columns if col.startswith("ITEM_") and not col.endswith("_Val")]
    print(f"Total Destinations found: {len(items)}")
    
    zip_path = os.path.join(output_dir, f"Bulk_Verify_{datetime.now().strftime('%Y%m%d_%H%M')}.zip")
    
    # Suffix 자동화 헬퍼 (app.py와 동일 로직)
    def get_auto_suffix(item_id):
        parts = item_id.split("_")
        if len(parts) >= 3:
            code = parts[2]
            return f"A{code}Q"
        return "A**Q"

    # 2. 일괄 생성 및 압축
    with zipfile.ZipFile(zip_path, "w", zipfile.ZIP_DEFLATED) as zip_file:
        for i, itm in enumerate(items):
            print(f"[{i+1}/{len(items)}] Processing {itm}...")
            
            # 필드 매핑 및 데이터 준비
            active_ids = mapping_master.get_active_fields_for_item(itm)
            active_data = {}
            for fid in active_ids:
                f_info = mapping_master.get_field_by_id(fid)
                idx = f_info["Index"]
                
                # Suffix(c) 자동화 (기본값)
                if idx == "c":
                    val = get_auto_suffix(itm)
                else:
                    # 신규 룩업 로직 사용: _Val > _Ex > Example
                    val = mapping_master.get_value_for_item(fid, itm)
                
                active_data[idx] = val
            
            # 개별 파일 생성 경로 (임시)
            res_pdf = os.path.join(output_dir, f"temp_{itm}.pdf")
            res_png = os.path.join(output_dir, f"temp_{itm}.png")
            
            try:
                engine.generate_label(itm, active_data, res_pdf, png_path=res_png)
                
                if os.path.exists(res_pdf):
                    zip_file.write(res_pdf, arcname=f"pdf/{itm}.pdf")
                    if os.path.exists(res_png):
                        zip_file.write(res_png, arcname=f"png/{itm}.png")
                    
                    # 로컬 임시 파일 삭제
                    os.remove(res_pdf)
                    if os.path.exists(res_png):
                        os.remove(res_png)
                else:
                    print(f"  FAILED to generate: {itm}")
            except Exception as e:
                print(f"  ERROR processing {itm}: {e}")

    print(f"\n[{datetime.now().strftime('%H:%M:%S')}] Verification Complete!")
    print(f"Result ZIP: {zip_path}")
    
    # 3. 결과 확인 (ZIP 내 파일 수)
    with zipfile.ZipFile(zip_path, 'r') as z:
        files = z.namelist()
        pdf_count = len([f for f in files if f.startswith('pdf/')])
        png_count = len([f for f in files if f.startswith('png/')])
        print(f"ZIP Content Summary:")
        print(f" - PDFs: {pdf_count}")
        print(f" - PNGs: {png_count}")

if __name__ == "__main__":
    run_all_files_verification()
