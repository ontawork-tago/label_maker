import pandas as pd
import os

def generate_report():
    file_path = "data/ID/id_mapping_master_super_final_v2.xlsx"
    if not os.path.exists(file_path):
        print("Mapping file not found.")
        return

    df = pd.read_excel(file_path)
    # Ensure ID is string
    df['ID'] = df['ID'].astype(str)
    
    # Create Excel Report
    excel_output_path = "data/ID/mapping_summary_final_v2.xlsx"
    
    # Identify items
    items = [col for col in df.columns if col.startswith("ITEM_") and not col.endswith("_Val")]
    base_info = ["ID", "Index", "Korean", "English", "Example"]
    
    mapping_summary = df[base_info + items].copy()
    
    try:
        mapping_summary.to_excel(excel_output_path, index=False)
        print(f"Excel report generated at {excel_output_path}")
    except Exception as e:
        print(f"Failed to generate Excel report (is it open?): {e}")

    # Provide group-based markdown for quick view
    report_content = "# ID Label Destination-Field Mapping Summary\n\n"
    report_content += "이 리포트는 각 향지별로 어떤 필드가 활성화('O')되어 있는지 보여줍니다.\n\n"

    chunk_size = 5
    for i in range(0, len(items), chunk_size):
        chunk = items[i:i+chunk_size]
        cols = ["Index", "Korean", "English"] + chunk
        table_df = df[cols].fillna("")
        report_content += f"## Group {i//chunk_size + 1}\n\n"
        report_content += table_df.to_markdown(index=False)
        report_content += "\n\n"

    with open("data/ID/mapping_summary_report.md", "w", encoding="utf-8") as f:
        f.write(report_content)

    # NEW: Create Concise List Report
    concise_report = "# Destination Mapping (Concise List)\n\n"
    for itm in items:
        active_indices = df[df[itm] == 'O']['Index'].tolist()
        concise_report += f"{itm} = {active_indices}\n"
    
    concise_output_path = "data/ID/mapping_summary_concise.txt"
    with open(concise_output_path, "w", encoding="utf-8") as f:
        f.write(concise_report)
    
    print(f"Concise list report generated at {concise_output_path}")

if __name__ == "__main__":
    generate_report()
