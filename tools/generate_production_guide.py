import pandas as pd
import os

def generate_production_guide():
    file_path = "data/ID/id_mapping_master_super_final_v2.xlsx"
    df = pd.read_excel(file_path)
    
    # Categorization Logic
    variable_indices = ['b', 'c', 'e', 'f'] # Model Name, ModelSuffix, S/N, Date
    maintenance_indices = ['a', 'a-1', 'a-2', 'a-29', 'p', 'd', 'd-1', 'd-2', 'h'] # Fixed per destination
    regulatory_indices = [idx for idx in df['Index'].unique() if idx.startswith(('z', 'w'))]
    
    guide_data = []
    
    for _, row in df.iterrows():
        idx = row['Index']
        korean = row['Korean']
        
        category = "IGNORE/DELETE"
        action = "관리 불필요 (비활성)"
        
        if idx in variable_indices:
            category = "BATCH ENTRY"
            action = "생산 시 매번 기입 필요 (S/N, 날짜 등)"
        elif idx in maintenance_indices:
            category = "MAINTENANCE"
            action = "최초 1회 기입 및 유지 (주소, 제품명 등)"
        elif idx in regulatory_indices:
            category = "REGULATORY"
            action = "규격 인증 마크 (유지)"
            
        guide_data.append({
            'Index': idx,
            'Item Name (KR)': korean,
            'Category': category,
            'Management Action': action
        })
        
    guide_df = pd.DataFrame(guide_data)
    
    # Save to Markdown for easy view
    output_path = "data/ID/production_management_guide.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# ID Label Production Management Guide\n\n")
        f.write("이 가이드는 벌크 생산 시 각 항목이 어떻게 관리되어야 하는지 정의합니다.\n\n")
        
        f.write("## 1. 정기 관리 항목 (Batch Entry)\n")
        f.write("생산 배치마다 값이 달라지는 항목입니다. 최종 엑셀에서 각 향지별 `_Val` 컬럼을 수정해야 합니다.\n\n")
        f.write(guide_df[guide_df['Category'] == 'BATCH ENTRY'][['Index', 'Item Name (KR)', 'Management Action']].to_markdown(index=False) + "\n\n")
        
        f.write("## 2. 고정 유지 항목 (Maintenance / Regulatory)\n")
        f.write("향지별로 고정되어 있으며 초기 세팅 후 변하지 않는 항목입니다.\n\n")
        f.write(guide_df[guide_df['Category'].isin(['MAINTENANCE', 'REGULATORY'])][['Index', 'Item Name (KR)', 'Management Action']].to_markdown(index=False) + "\n\n")
        
        f.write("## 3. 미사용/삭제 항목 (Ignore)\n")
        f.write("현재 마스터 파일에는 존재하나 도면이나 템플릿에 활성화되지 않은 서비스 필드입니다.\n\n")
        f.write(guide_df[guide_df['Category'] == 'IGNORE/DELETE'][['Index', 'Item Name (KR)', 'Management Action']].to_markdown(index=False) + "\n\n")

    print(f"Production guide generated at {output_path}")

if __name__ == "__main__":
    generate_production_guide()
