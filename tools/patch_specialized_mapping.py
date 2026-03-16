import pandas as pd
import os

def expand_and_fix_mapping():
    file_path = "data/ID/id_mapping_master_super_final_v2.xlsx"
    df = pd.read_excel(file_path)
    
    # 1. Add missing Indices if not present
    new_rows = [
        {'Index': 'd-2', 'Korean': '정격 (Uzbekistan)', 'English': 'Power (Uzbekistan)', 'Example': 'AC 100-240 B~ 50/60 Гц 2,6 A'},
        {'Index': 'z-9', 'Korean': '인증 마크 구역 (UZ)', 'English': 'Regulatory Box (UZ)', 'Example': 'UzTR.517...'}
    ]
    
    for row_data in new_rows:
        if row_data['Index'] not in df['Index'].values:
            # Create a new row with all ITEM columns as NaN
            new_row = {col: None for col in df.columns}
            new_row.update(row_data)
            # Add ID
            new_row['ID'] = len(df) + 1
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(f"Added new index: {row_data['Index']}")

    # 2. Specifically update ITEM_38
    # Uzbekistan needs a specific address
    uz_address = "LG Twin Tauers, Koreya Respublikasi, Seul, Yongdungpo-Gu, Yoydo-Dong 20\nLG Twin towers, 20, Yoido-Dong, Youngdungpo-Gu, Сеул, Корея"
    df.loc[df['Index'] == 'a-29', 'ITEM_38_DG_Uzbekistan_Val'] = uz_address
    
    # Activate d-1 and z-9 for ITEM_38
    # NOTE: Engine maps index 3 to 'd-1', so we use d-1 for Uzbekistan's power slot
    df.loc[df['Index'] == 'd-1', 'ITEM_38_DG_Uzbekistan'] = 'O'
    df.loc[df['Index'] == 'd-1', 'ITEM_38_DG_Uzbekistan_Val'] = "AC 100-240 B~ 50/60 Гц 2,6 A"
    df.loc[df['Index'] == 'z-9', 'ITEM_38_DG_Uzbekistan'] = 'O'
    
    # Deactivate 'd' and 'd-2' for ITEM_38 to avoid confusion
    df.loc[df['Index'] == 'd', 'ITEM_38_DG_Uzbekistan'] = None
    df.loc[df['Index'] == 'd-2', 'ITEM_38_DG_Uzbekistan'] = None
    
    print("Updated ITEM_38 specialized mapping.")

    # 3. Handle localized address for other items if possible
    # (Leaving for now, but identifying that a-29 should probably NOT be batch 'O' if data is missing)

    # Save
    df.to_excel(file_path, index=False)
    print(f"Saved update to {file_path}")

if __name__ == "__main__":
    expand_and_fix_mapping()
