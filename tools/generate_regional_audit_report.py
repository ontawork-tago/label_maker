from src.mapping import IDMappingMaster
import pandas as pd

def generate_regional_audit():
    master = IDMappingMaster("data/ID/id_mapping_master_super_final_v3.xlsx")
    items = [c for c in master.df.columns if c.startswith('ITEM_') and not c.endswith(('_Val', '_Ex'))]
    
    report_data = []
    
    for item_id in items:
        active_ids = master.get_active_fields_for_item(item_id)
        groups = master.get_field_management_groups(active_ids, item_id)
        
        report_data.append({
            'Destination': item_id,
            'Shared (Batch)': len(groups['Shared']),
            'Specific (Regional)': len(groups['Specific']),
            'Fixed (Regulatory)': len(groups['Fixed']),
            'Shared Indices': ", ".join([f["Index"] for f in groups['Shared']]),
            'Specific Indices': ", ".join([f["Index"] for f in groups['Specific']])
        })
        
    df_report = pd.DataFrame(report_data)
    
    output_path = "data/ID/regional_management_audit.md"
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write("# Regional Management Audit Report\n\n")
        f.write("이 리포트는 각 향지별로 공통 관리되는 항목과 개별 관리되는 항목의 분포를 보여줍니다.\n\n")
        f.write(df_report.to_markdown(index=False))
        
        f.write("\n\n## Management Categories Definition\n")
        f.write("- **Shared (Batch)**: 생산 시 공통 입력 가능 항목 (b, c, e, f)\n")
        f.write("- **Specific (Regional)**: 향지별 개별 데이터 유지 필수 항목 (a-29, d, p, h 등)\n")
        f.write("- **Fixed (Regulatory)**: 템플릿 고정 항목 (z, w 시리즈 등)\n")

    print(f"Audit report generated at {output_path}")

if __name__ == "__main__":
    generate_regional_audit()
