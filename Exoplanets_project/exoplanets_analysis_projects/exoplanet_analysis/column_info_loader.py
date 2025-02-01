import os

def load_ps_columns_info(ps_columns_file='ps_columns.txt'):
    info_dict = {}
    if not os.path.exists(ps_columns_file):
        print(f"[WARNING] File '{ps_columns_file}' not found. No extra columns info will be used.")
        return info_dict

    with open(ps_columns_file, 'r', encoding='utf-8') as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split('\t\t\t\t')
            if len(parts) < 3:
                continue
            col_name = parts[0].strip()
            unit = parts[1].strip()
            desc = parts[2].strip()
            info_dict[col_name] = {
                'unit': unit,
                'description': desc
            }

    return info_dict
