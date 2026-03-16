import pandas as pd
import os

class IDMappingMaster:
    def __init__(self, file_path="data/ID/id_mapping_master_super_final_v3.xlsx"):
        self.file_path = file_path
        # [A] Shared (Bulk Entry) Indices: 생산 시 매번 바뀌어 공통 입력되는 항목
        self.shared_indices = ["b", "c", "e", "f"]
        # [B] Specific (Regional) Indices: 향지별로 개별 관리되는 정적 항목 (주소, 정격 등)
        self.specific_indices = ["a-29", "d", "d-1", "d-2", "p", "h"]
        
        if os.path.exists(file_path):
            self.df = pd.read_excel(file_path)
            self.df['ID'] = self.df['ID'].astype(str)
        else:
            self.df = None
            
    def get_fields(self):
        """모든 필드 리스트 반환"""
        if self.df is None: return []
        return self.df.to_dict('records')
    
    def get_field_management_groups(self, active_ids, item_id):
        """활성 필드를 관리 유형별로 분류: Shared, Specific, Regulatory (Fixed)"""
        groups = {
            "Shared": [],    # b, c, e, f
            "Specific": [],  # a-29, d, p, h 등 개별 데이터 필요 항목
            "Fixed": []      # z, w 시리즈 등 고정 마크
        }
        
        for fid in active_ids:
            field = self.get_field_by_id(fid)
            if not field: continue
            idx = field["Index"]
            
            if idx in self.shared_indices:
                groups["Shared"].append(field)
            elif idx in self.specific_indices:
                groups["Specific"].append(field)
            else:
                groups["Fixed"].append(field)
                
        return groups

    def get_value_for_item(self, field_id, item_id):
        """데이터 조회 우선순위: {item}_Val > {item}_Ex > Global Example"""
        field = self.get_field_by_id(field_id)
        if not field: return ""
        
        val_col = f"{item_id}_Val"
        ex_col = f"{item_id}_Ex"
        
        # 1. 현재 배치 값 (_Val)
        if val_col in field and pd.notna(field[val_col]) and str(field[val_col]).strip() != "":
            return field[val_col]
        # 2. 향지별 개별 예시/가이드 (_Ex)
        if ex_col in field and pd.notna(field[ex_col]) and str(field[ex_col]).strip() != "":
            return field[ex_col]
        # 3. 글로벌 예시 (Fallback)
        return field.get("Example", "")

    def get_field_by_id(self, field_id):
        """고유 ID를 기반으로 특정 필드 정보 반환"""
        if self.df is None: return None
        result = self.df[self.df['ID'] == str(field_id)]
        if not result.empty:
            return result.iloc[0].to_dict()
        return None

    def get_field_by_index(self, index):
        """Index(a, b, p 등)를 기반으로 첫 번째 필드 정보 반환"""
        if self.df is None: return None
        result = self.df[self.df['Index'] == str(index)]
        if not result.empty:
            return result.iloc[0].to_dict()
        return None

    def get_active_fields_for_item(self, item_id):
        """특정 향지에서 'O'로 표시된 활성 필드의 고유 ID 목록 반환"""
        if self.df is None or item_id not in self.df.columns:
            return []
        return self.df[self.df[item_id] == 'O']['ID'].tolist()

if __name__ == "__main__":
    master = IDMappingMaster()
    print(f"Loaded {len(master.get_fields())} fields from v3.")
    item = "ITEM_38_DG_Uzbekistan"
    fids = master.get_active_fields_for_item(item)
    print(f"Active fields for {item}: {len(fids)}")
    val = master.get_value_for_item(fids[0], item)
    print(f"Sample value for first field: {val}")

if __name__ == "__main__":
    master = IDMappingMaster()
    print(f"Loaded {len(master.get_fields())} fields.")
    test_id = master.get_active_fields_for_item("ITEM_09_KR_Korea")[0]
    print(f"Test mapping via ID {test_id}: {master.get_field_by_id(test_id)['Korean']}")
