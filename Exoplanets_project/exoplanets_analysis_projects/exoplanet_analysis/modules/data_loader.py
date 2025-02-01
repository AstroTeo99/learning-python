import pandas as pd
import os
import logging
import sqlite3
from astropy.io.votable import parse
from astropy.table import Table

from column_info_loader import load_ps_columns_info

def select_data_file():
    """
    Lets the user select a file from the 'data/' folder.
    Returns (df, columns_info, file_name, file_path).
    """
    data_folder = 'data'
    try:
        files = os.listdir(data_folder)
        supported_exts = ('.csv', '.vot', '.votable', '.db')
        supported_files = [f for f in files if f.lower().endswith(supported_exts)]
        if not supported_files:
            print(f"No supported files found in folder '{data_folder}'.")
            logging.warning("No supported files.")
            return None, {}, None, None

        print(f"\nFiles available in '{data_folder}':")
        for idx, file in enumerate(supported_files, start=1):
            print(f"{idx}. {file}")
        print("0. Cancel")

        choice = input("Select the number of the file to load: ")
        try:
            choice = int(choice)
        except ValueError:
            print("Please enter a valid number.")
            return None, {}, None, None

        if choice == 0:
            return None, {}, None, None
        elif 1 <= choice <= len(supported_files):
            file_path = os.path.join(data_folder, supported_files[choice - 1])
            df, columns_info = load_data(file_path)
            file_name = os.path.basename(file_path)
            return df, columns_info, file_name, file_path
        else:
            print("Invalid choice.")
            return None, {}, None, None

    except Exception as e:
        logging.error(f"File selection error: {e}")
        print(f"Error selecting file: {e}")
        return None, {}, None, None

def load_data(file_path):
    ps_info = load_ps_columns_info(ps_columns_file=os.path.join('exoplanet_analysis', 'ps_columns.txt'))
    columns_info = {}
    df = None
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext == '.csv':
            df = pd.read_csv(file_path)
            for col in df.columns:
                if col in ps_info:
                    columns_info[col] = {
                        'description': ps_info[col].get('description', ''),
                        'unit': ps_info[col].get('unit', '')
                    }
                else:
                    columns_info[col] = {'description': '', 'unit': ''}
            logging.info(f"CSV '{file_path}' loaded successfully.")

        elif ext in ('.vot', '.votable'):
            votable_file = parse(file_path)
            table = votable_file.get_first_table()
            df = table.to_table().to_pandas()

            for field in table.fields:
                name = field.name
                desc = field.description if field.description else ''
                unit = str(field.unit) if field.unit else ''
                columns_info[name] = {
                    'description': desc,
                    'unit': unit
                }
            for col in df.columns:
                if col not in columns_info:
                    columns_info[col] = {'description': '', 'unit': ''}
                if col in ps_info:
                    columns_info[col]['description'] = ps_info[col].get('description', columns_info[col]['description'])
                    columns_info[col]['unit'] = ps_info[col].get('unit', columns_info[col]['unit'])

            logging.info(f"VOTable '{file_path}' loaded successfully.")

        elif ext == '.db':
            conn = sqlite3.connect(file_path)
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            tables = cursor.fetchall()
            if not tables:
                print("No tables found in this .db file.")
                conn.close()
                return None, {}

            print("\nTables found in the .db file:")
            for i, tbl in enumerate(tables, start=1):
                print(f"{i}. {tbl[0]}")
            print("0. Cancel")

            tbl_choice = input("Choose a table number to load: ")
            try:
                tbl_choice = int(tbl_choice)
            except ValueError:
                print("Invalid number. Cancelling.")
                conn.close()
                return None, {}

            if tbl_choice == 0 or not (1 <= tbl_choice <= len(tables)):
                print("Cancelled.")
                conn.close()
                return None, {}

            chosen_table = tables[tbl_choice - 1][0]
            df = pd.read_sql_query(f"SELECT * FROM {chosen_table}", conn)
            conn.close()

            for col in df.columns:
                if col in ps_info:
                    columns_info[col] = {
                        'description': ps_info[col].get('description', ''),
                        'unit': ps_info[col].get('unit', '')
                    }
                else:
                    columns_info[col] = {'description': '', 'unit': ''}

            logging.info(f"DB '{file_path}', table '{chosen_table}' loaded successfully.")

        else:
            print("Unsupported file format (only CSV, VOT, VOTable, DB).")
            logging.warning(f"Unsupported format: {file_path}")
            return None, {}

    except Exception as e:
        logging.error(f"Error loading '{file_path}': {e}")
        print(f"Data loading error: {e}")
        return None, {}

    return df, columns_info

def convert_votable_to_csv(file_path):
    from astropy.io.votable import parse_single_table
    try:
        ext = os.path.splitext(file_path)[1].lower()
        if ext not in ['.vot', '.votable']:
            print("File is not VOTable.")
            return False

        votable = parse_single_table(file_path)
        tab = votable.to_table()
        df = tab.to_pandas()
        base_name = os.path.splitext(os.path.basename(file_path))[0]
        csv_name = base_name + ".csv"
        csv_path = os.path.join('data', csv_name)
        df.to_csv(csv_path, index=False)
        print(f"VOTable converted to CSV: {csv_path}")
        return True
    except Exception as e:
        logging.error(f"Error converting VOTable->CSV: {e}")
        print(f"Conversion error: {e}")
        return False
