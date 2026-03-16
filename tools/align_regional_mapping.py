import pandas as pd
import os

def align_regional_mappings():
    file_path = "data/ID/id_mapping_master_super_final_v2.xlsx"
    df = pd.read_excel(file_path)
    
    # 1. Ensure all relevant indices exist
    required_indices = [
        {'Index': 'w-9', 'Korean': '무선인증 (ANATEL)', 'English': 'Wireless (ANATEL)', 'Example': '01234-16-05662'},
        {'Index': 'w-5', 'Korean': '무선인증 (UAE TRA)', 'English': 'Wireless (UAE TRA)', 'Example': 'REGISTERED No: ER45435/16\nDEALER No: DA0041614/10'},
        {'Index': 'w-24', 'Korean': '무선인증 (NOM Mexico)', 'English': 'Wireless (NOM Mexico)', 'Example': 'IFT : RCPLGLG16-1583'},
        {'Index': 'a-29_BR', 'Korean': '주소 (Brazil)', 'English': 'Address (Brazil)', 'Example': 'Av. D. Pedro I, W 7777, Área industrial\nCEP: 12091-000 Taubaté-SP Brasil'},
    ]
    
    for row_data in required_indices:
        if row_data['Index'] not in df['Index'].values:
            new_row = {col: None for col in df.columns}
            new_row.update(row_data)
            new_row['ID'] = len(df) + 1
            df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
            print(f"Added index: {row_data['Index']}")

    # 2. Brazil (ITEM_21_WZ_Brazil) Alignment
    df.loc[df['Index'] == 'a-29', 'ITEM_21_WZ_Brazil'] = 'O'
    df.loc[df['Index'] == 'a-29', 'ITEM_21_WZ_Brazil_Val'] = "Av. D. Pedro I, W 7777, Área industrial\nCEP: 12091-000 Taubaté-SP Brasil"
    df.loc[df['Index'] == 'w-9', 'ITEM_21_WZ_Brazil'] = 'O'
    
    # 3. UAE (ITEM_24_MA_UAE) Alignment
    df.loc[df['Index'] == 'w-5', 'ITEM_24_MA_UAE'] = 'O'
    
    # 4. Mexico (ITEM_20_WM_Mexico) Alignment
    df.loc[df['Index'] == 'w-24', 'ITEM_20_WM_Mexico'] = 'O'
    
    # 5. Algeria (ITEM_22_GS_Algeria) Alignment
    # Algeria uses ARPCE (w-10), let's ensure it's active
    if 'w-10' not in df['Index'].values:
        new_row = {col: None for col in df.columns}
        new_row.update({'Index': 'w-10', 'Korean': '무선인증 (Algeria ARPCE)', 'English': 'Wireless (Algeria ARPCE)', 'Example': 'AGREEMENT No: 123/ARPCE/...' })
        new_row['ID'] = len(df) + 1
        df = pd.concat([df, pd.DataFrame([new_row])], ignore_index=True)
    df.loc[df['Index'] == 'w-10', 'ITEM_22_GS_Algeria'] = 'O'

    # Clean up incorrect columns from previous run
    bad_cols = ['ITEM_21_Brazil', 'ITEM_24_UAE', 'ITEM_20_Mexico']
    df = df.drop(columns=[c for c in bad_cols if c in df.columns])

    # Save
    df.to_excel(file_path, index=False)
    print(f"Saved regional alignment to {file_path}")

if __name__ == "__main__":
    align_regional_mappings()
