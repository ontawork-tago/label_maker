import pandas as pd
import os

def patch_mapping():
    file_path = "data/ID/id_mapping_master_super_final_v2.xlsx"
    backup_path = "data/ID/id_mapping_master_super_final_v2_backup.xlsx"
    
    if not os.path.exists(file_path):
        print(f"Error: {file_path} not found.")
        return

    # Backup original
    if not os.path.exists(backup_path):
        import shutil
        shutil.copy2(file_path, backup_path)
        print(f"Backup created at {backup_path}")

    df = pd.read_excel(file_path)
    
    # 1. Index Rename: f-2 -> f
    df.loc[df['Index'] == 'f-2', 'Index'] = 'f'
    print("Renamed index f-2 to f.")

    # 2. Update a-29 Data (Address/Company Info)
    # Drawing says: 
    # LG Electronics Inc.
    # LG Twin Tower 128, Yeoui-daero, Yeongdeungpo-gu,
    # Seoul 07336, Republic of Korea
    address_text = "LG Electronics Inc. LG Twin Tower 128, Yeoui-daero, Yeongdeungpo-gu, Seoul 07336, Republic of Korea"
    df.loc[df['Index'] == 'a-29', 'Korean'] = "제조원/본사 주소"
    df.loc[df['Index'] == 'a-29', 'English'] = "Manufacturer/HQ Address"
    df.loc[df['Index'] == 'a-29', 'Example'] = address_text
    print("Updated a-29 address information.")

    # 3. Batch Activate Core Fields for all 37 destinations
    items = [col for col in df.columns if col.startswith("ITEM_") and not col.endswith("_Val")]
    core_indices = ['a', 'b', 'c', 'd', 'e', 'f', 'p', 'a-29']
    
    for idx in core_indices:
        if idx in df['Index'].values:
            df.loc[df['Index'] == idx, items] = 'O'
            print(f"Activated core index '{idx}' for all items.")
        else:
            print(f"Warning: Core index '{idx}' not found in Excel!")

    # Save patched file
    df.to_excel(file_path, index=False)
    print(f"Successfully patched mapping file: {file_path}")

if __name__ == "__main__":
    patch_mapping()
