import os
import io
import pandas as pd
from src.engine import IDLabelEngine
from src.mapping import IDMappingMaster

def test_bulk_logic():
    engine = IDLabelEngine()
    mapping_master = IDMappingMaster()
    
    # 1. 대상 향지 선정 (테스트용 3개)
    test_items = ["ITEM_09_KR_Korea", "ITEM_18_US_USA", "ITEM_21_WZ_Brazil"]
    
    # 2. Global 데이터 시뮬레이션
    global_inputs = {
        "a": "TEST-BULK-MODEL",
        "c": "TEST.SUFFIX",
        "d": "AC 220V",
        "f-2": "03/2026"
    }
    
    # 3. Variable 데이터 시뮬레이션 (원산지)
    var_data = [
        {"Destination": "ITEM_09_KR_Korea", "p": "MADE IN KOREA"},
        {"Destination": "ITEM_18_US_USA", "p": "MADE IN VIETNAM"},
        {"Destination": "ITEM_21_WZ_Brazil", "p": "MADE IN BRAZIL"}
    ]
    var_df = pd.DataFrame(var_data)
    
    print("--- Starting Bulk Test ---")
    for _, row in var_df.iterrows():
        target_item = row["Destination"]
        print(f"Generating: {target_item}")
        
        target_active_ids = mapping_master.get_active_fields_for_item(target_item)
        current_active_data = {}
        
        for fid in target_active_ids:
            f_info = mapping_master.get_field_by_id(fid)
            idx = f_info["Index"]
            
            if idx in global_inputs:
                current_active_data[idx] = global_inputs[idx]
            elif idx in row:
                current_active_data[idx] = row[idx]
            else:
                current_active_data[idx] = f_info["Example"]
        
        out_path = f"output/ID/test_bulk_{target_item}.pdf"
        engine.generate_label(target_item, current_active_data, out_path)
        
        if os.path.exists(out_path):
            print(f"  [SUCCESS] {out_path} created.")
        else:
            print(f"  [FAILED] {out_path} not found.")

if __name__ == "__main__":
    test_bulk_logic()
