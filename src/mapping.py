import pandas as pd
import os

class IDMappingMaster:
    def __init__(self, file_path="data/ID/id_mapping_master_super_final_v2.xlsx"):
        self.file_path = file_path
        self.variable_fields = ["c", "p"] # Suffix(c)와 원산지(p)는 향지별로 달라질 수 있는 가변 필드로 분류
        if os.path.exists(file_path):
            self.df = pd.read_excel(file_path)
            self.df['ID'] = self.df['ID'].astype(str)
        else:
            self.df = None
            
    def get_fields(self):
        """모든 필드 리스트 반환"""
        if self.df is None: return []
        return self.df.to_dict('records')
    
    def get_field_categories(self, active_ids):
        """활성 필드를 Global/Variable로 분리하여 반환"""
        global_fields = []
        variable_fields = []
        
        for fid in active_ids:
            field = self.get_field_by_id(fid)
            if not field: continue
            
            if field["Index"] in self.variable_fields:
                variable_fields.append(field)
            else:
                global_fields.append(field)
                
        return global_fields, variable_fields

    def get_field_by_id(self, field_id):
        """고유 ID를 기반으로 특정 필드 정보 반환"""
        if self.df is None: return None
        result = self.df[self.df['ID'] == str(field_id)]
        if not result.empty:
            return result.iloc[0].to_dict()
        return None

    def get_field_by_index(self, index):
        """Index(a, b, p 등)를 기반으로 첫 번째 필드 정보 반환 (app.py 호환성용)"""
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
    print(f"Loaded {len(master.get_fields())} fields.")
    test_id = master.get_active_fields_for_item("ITEM_09_KR_Korea")[0]
    print(f"Test mapping via ID {test_id}: {master.get_field_by_id(test_id)['Korean']}")
