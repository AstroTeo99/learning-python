import logging
import os
import pandas as pd
from astropy.io.votable import writeto
from astropy.table import Table

def show_columns_interactive(df, columns_info, data_file_name):
    print(f"\n=== Available columns in '{data_file_name}' ===")
    cols_sorted = sorted(df.columns)
    col_width = 25
    unit_width = 15
    desc_width = 40

    header = f"{'COLUMN NAME'.ljust(col_width)} | {'UNIT'.ljust(unit_width)} | {'DESCRIPTION'.ljust(desc_width)}"
    print(header)
    print("-" * len(header))
    for col in cols_sorted:
        unit = columns_info.get(col, {}).get('unit', '') or ''
        desc = columns_info.get(col, {}).get('description', '') or ''
        if not unit:
            unit = "No unit"
        if not desc:
            desc = "No description"
        print(f"{col.ljust(col_width)} | {unit.ljust(unit_width)} | {desc.ljust(desc_width)}")

def _parse_column_selection(selection_str, all_cols):
    selected_cols = set()
    parts = selection_str.split(',')
    for sel in parts:
        sel = sel.strip()
        if '-' in sel:
            try:
                start, end = map(int, sel.split('-'))
                if start < 1 or end > len(all_cols) or start > end:
                    logging.warning(f"Invalid range: {sel}")
                    continue
                for i in range(start, end + 1):
                    selected_cols.add(all_cols[i - 1])
            except ValueError:
                logging.warning(f"Invalid range format: {sel}")
        else:
            try:
                idx = int(sel)
                if 1 <= idx <= len(all_cols):
                    selected_cols.add(all_cols[idx - 1])
                else:
                    logging.warning(f"Invalid column index: {sel}")
            except ValueError:
                logging.warning(f"Invalid column index format: {sel}")
    return [c for c in all_cols if c in selected_cols]

def filter_and_export_data_interactive(df, columns_info, data_file_name):
    logging.info("Starting data filtering and export.")
    try:
        print("\nSelect columns to include in the exported file.")
        all_cols = list(df.columns)
        for idx, col in enumerate(all_cols, start=1):
            print(f"{idx}. {col}")

        selection_str = input("Enter column numbers separated by commas (e.g. 1,3,5 or 2-10,15): ")
        selected_cols = _parse_column_selection(selection_str, all_cols)

        if not selected_cols:
            print("No valid columns selected. Export cancelled.")
            logging.warning("No valid columns selected for export.")
            return

        selected_with_err = set(selected_cols)
        for col in selected_cols:
            err1 = f"{col}err1"
            err2 = f"{col}err2"
            if err1 in df.columns and err2 in df.columns:
                selected_with_err.add(err1)
                selected_with_err.add(err2)

        filtered_df = df[list(selected_with_err)]

        while True:
            fmt = input("Choose export format (csv/votable): ").lower()
            if fmt in ['csv', 'votable']:
                break
            else:
                print("Unrecognized format. Try again.")

        file_name = input(f"Enter the output file name (e.g. filtered_data.{fmt}): ").strip()
        if fmt == 'csv' and not file_name.lower().endswith('.csv'):
            file_name += '.csv'
        elif fmt == 'votable':
            if not (file_name.lower().endswith('.vot') or file_name.lower().endswith('.votable')):
                file_name += '.vot'

        out_path = os.path.join('data', file_name)

        if fmt == 'csv':
            filtered_df.to_csv(out_path, index=False)
            print(f"Data exported to '{out_path}'.")
            logging.info(f"Data exported to CSV: {out_path}")
        else:
            if os.path.exists(out_path):
                try:
                    os.remove(out_path)
                except Exception as e:
                    logging.error(f"Error removing existing file '{out_path}': {e}")
                    print(f"Error removing existing file '{out_path}': {e}")
                    return
            table = Table.from_pandas(filtered_df)
            try:
                writeto(table, out_path)
                print(f"Data exported to '{out_path}'.")
                logging.info(f"Data exported to VOTable: {out_path}")
            except Exception as e:
                print(f"Error exporting to VOTable: {e}")
                logging.error(f"Error exporting to VOTable: {e}")
    except Exception as e:
        logging.error(f"Error during filtering or export: {e}")
        print(f"Error during filtering or export: {e}")
