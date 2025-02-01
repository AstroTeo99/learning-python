# exoplanet_analysis/modules/query_data.py

import sqlite3
import pandas as pd
import logging
import os

from modules.data_loader import select_data_file, load_data

def run_sql_query_on_data():
    data_folder = os.path.join(os.getcwd(), "data")
    try:
        files = os.listdir(data_folder)
        supported_exts = ('.csv', '.vot', '.votable', '.db')
        supported_files = [f for f in files if f.lower().endswith(supported_exts)]
        if not supported_files:
            print(f"No supported files found in folder '{data_folder}'.")
            logging.warning("No supported files in data folder.")
            return

        print(f"\nFiles available in '{data_folder}':")
        for idx, file in enumerate(supported_files, start=1):
            print(f"{idx}. {file}")
        print("0. Cancel")

        choice = input("Select the number of the file to use for the SQL query: ")
        try:
            choice = int(choice)
        except ValueError:
            print("Please enter a valid number.")
            return

        if choice == 0:
            print("Query cancelled.")
            return
        elif 1 <= choice <= len(supported_files):
            file_name = supported_files[choice - 1]
            file_path = os.path.join(data_folder, file_name)
            df, _ = load_data(file_path)
            if df is None:
                print("Error loading data.")
                return
            print(f"File '{file_name}' loaded successfully for SQL query.")
        else:
            print("Invalid choice.")
            return

        print("\n=== SQL QUERY (in-memory) ===")
        print("Example: SELECT col1, col2 FROM mydata WHERE col3 > 10 ORDER BY col2 DESC;")
        query = input("Enter your SQL query: ").strip()
        if not query:
            print("No query entered. Cancelling.")
            return

        conn = sqlite3.connect(":memory:")
        try:
            df.to_sql("mydata", conn, if_exists='replace', index=False)
            result_df = pd.read_sql_query(query, conn)
        except Exception as e:
            logging.error(f"Error executing SQL query: {e}")
            print(f"Error executing SQL query: {e}")
            conn.close()
            return
        finally:
            conn.close()

        print("\n=== Query Result ===")
        if result_df.empty:
            print("The query returned no results (empty DataFrame).")
        else:
            print(result_df)

        save_choice = input("\nDo you want to save this result to a file? (y/n): ").strip().lower()
        if save_choice != 'y':
            print("Result not saved.")
            return

        while True:
            fmt = input("Choose export format (csv/votable/db): ").lower()
            if fmt in ['csv', 'votable', 'db']:
                break
            else:
                print("Unrecognized format. Try again.")

        safe_query = "".join([c if c.isalnum() else "_" for c in query])
        base, ext = os.path.splitext(file_name)
        new_file_name = f"{base}_WHERE_{safe_query}.{fmt}"
        out_path = os.path.join(data_folder, new_file_name)

        if fmt == 'csv':
            result_df.to_csv(out_path, index=False)
            print(f"Query result saved to '{out_path}'.")
        elif fmt == 'votable':
            from astropy.io.votable import writeto
            from astropy.table import Table
            try:
                if os.path.exists(out_path):
                    os.remove(out_path)
                table = Table.from_pandas(result_df)
                writeto(table, out_path)
                print(f"Query result saved to '{out_path}'.")
            except Exception as e:
                logging.error(f"Error exporting to VOTable: {e}")
                print(f"Error exporting to VOTable: {e}")
        elif fmt == 'db':
            try:
                if os.path.exists(out_path):
                    os.remove(out_path)
                conn_db = sqlite3.connect(out_path)
                result_df.to_sql("query_result", conn_db, if_exists='replace', index=False)
                conn_db.close()
                print(f"Query result saved to '{out_path}'.")
            except Exception as e:
                logging.error(f"Error exporting to DB: {e}")
                print(f"Error exporting to DB: {e}")

    except Exception as e:
        logging.error(f"Error in run_sql_query_on_data: {e}")
        print(f"Error in run_sql_query_on_data: {e}")
