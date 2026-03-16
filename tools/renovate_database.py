import pandas as pd
import numpy as np

def renovate_database():
    file_path = "data/ID/id_mapping_master_super_final_v2.xlsx"
    df = pd.read_excel(file_path)
    
    # Identify all ITEM columns
    item_cols = [c for c in df.columns if c.startswith('ITEM_') and not c.endswith(('_Val', '_Ex'))]
    
    # Create a new column list starting with core metadata
    core_metadata = ['ID', 'Index', 'English', 'Korean', 'Example', 'Type', 'Deletable']
    new_cols = core_metadata.copy()
    
    for item in sorted(item_cols):
        # Add Selection, Value, and Example columns per item
        new_cols.append(item)
        val_col = f"{item}_Val"
        ex_col = f"{item}_Ex"
        
        # Initialize if not present
        if val_col not in df.columns:
            # If item was active ('O'), maybe we have partial data? 
            # For now, initialize with global Example if active
            df[val_col] = df.apply(lambda row: row['Example'] if row[item] == 'O' else np.nan, axis=1)
        
        if ex_col not in df.columns:
            # Initialize with current Example as reference
            df[ex_col] = df.apply(lambda row: row['Example'] if row[item] == 'O' else np.nan, axis=1)
            
        new_cols.append(val_col)
        new_cols.append(ex_col)
        
    # Reorder and save
    df_new = df[new_cols]
    
    # Special Fix for Uzbekistan and Brazil which already had some specialized data
    # (Actually they were in _Val, so we keep them)
    
    output_path = "data/ID/id_mapping_master_super_final_v3.xlsx"
    df_new.to_excel(output_path, index=False)
    print(f"Renovated database saved to {output_path}")
    print(f"Total columns added: {len(new_cols) - len(df.columns)}")

if __name__ == "__main__":
    renovate_database()
