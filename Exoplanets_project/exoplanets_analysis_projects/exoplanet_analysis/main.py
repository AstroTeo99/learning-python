import os
import sys
import logging
import re

script_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(script_dir)
os.chdir(parent_dir)

from config_reader import load_config
from modules.data_loader import select_data_file, load_data, convert_votable_to_csv
from modules.create_graphs import create_personal_chart
from modules.query_data import run_sql_query_on_data
from modules.filter_show_columns import show_columns_interactive, filter_and_export_data_interactive

def setup_logging(config):
    logs_folder = config['DEFAULT'].get('logs_folder', 'logs')
    log_file = config['DEFAULT'].get('log_file', 'exoplanet_analysis.log')
    log_level_str = config['DEFAULT'].get('log_level', 'INFO').upper()

    if not os.path.exists(logs_folder):
        os.makedirs(logs_folder, exist_ok=True)
    log_path = os.path.join(logs_folder, log_file)

    log_level = getattr(logging, log_level_str, logging.INFO)

    logging.basicConfig(
        filename=log_path,
        level=log_level,
        format='%(asctime)s - %(levelname)s - %(message)s',
        filemode='a'
    )
    console = logging.StreamHandler()
    console.setLevel(logging.ERROR)
    formatter = logging.Formatter('%(levelname)s - %(message)s')
    console.setFormatter(formatter)
    logging.getLogger('').addHandler(console)

def sub_menu_columns_and_filters(df, columns_info, data_file_name):
    while True:
        print("\n=== Columns & Filters ===")
        print("1. Show the number of rows and columns")
        print("2. Show available columns")
        print("3. Filter and export data")
        print("4. Return to main menu")

        choice = input("Choose an option: ")

        if choice == '1':
            rows, cols = df.shape
            print(f"\nDataFrame has {rows} rows and {cols} columns.")
        elif choice == '2':
            show_columns_interactive(df, columns_info, data_file_name)
        elif choice == '3':
            filter_and_export_data_interactive(df, columns_info, data_file_name)
        elif choice == '4':
            break
        else:
            print("Invalid choice. Try again.")

def interactive_menu():
    # 1) Select file
    df, columns_info, data_file_name, data_file_path = select_data_file()
    if df is None:
        print("Program terminated (no file loaded or error).")
        return

    print(f"File '{data_file_name}' loaded successfully.")

    while True:
        print("\n=== Exoplanet Catalog Analysis ===")
        print("1. Select another data file")
        print("2. Create a custom chart (Plotly)")
        print("3. Run an in-memory SQL query on the DataFrame")
        print("4. Columns & Filters")
        
        votable_exts = ('.vot', '.votable')
        file_ext = os.path.splitext(data_file_name)[1].lower()
        if file_ext in votable_exts:
            print("5. Convert the file to CSV")
            print("6. Exit")
            max_option = 6
        else:
            print("5. Exit")
            max_option = 5

        choice = input("Enter the number of the operation: ")

        if choice == '1':
            # Select a new file
            new_df, new_ci, new_file, new_path = select_data_file()
            if new_df is not None:
                df = new_df
                columns_info = new_ci
                data_file_name = new_file
                data_file_path = new_path
                print(f"File '{data_file_name}' loaded successfully.")

        elif choice == '2':
            # Create chart
            if df is not None:
                print("\nEnter the expression for the X axis (e.g. 'pl_orbsmax', or 'pl_orbsmax [au]'):")
                x_expr = input("X expression: ").strip()
                print("Enter the expression for the Y axis (e.g. 'pl_orbper', or 'pl_orbper [days]'):")
                y_expr = input("Y expression: ").strip()
                create_personal_chart(df, x_expr, y_expr, columns_info, data_file_path)
            else:
                print("No DataFrame loaded.")

        elif choice == '3':
            if df is not None:
                run_sql_query_on_data()
            else:
                print("No DataFrame loaded.")

        elif choice == '4':
            if df is not None:
                sub_menu_columns_and_filters(df, columns_info, data_file_name)
            else:
                print("No DataFrame loaded.")

        elif choice == '5' and max_option == 6:
            if file_ext in votable_exts:
                success = convert_votable_to_csv(os.path.join('data', data_file_name))
                if success:
                    print("File successfully converted to CSV.")
            else:
                print("Option only valid for VOTable files.")

        elif (choice == '5' and max_option == 5) or (choice == '6' and max_option == 6):
            print("Exiting program.")
            break
        else:
            print("Invalid choice.")

def main():
    config = load_config()
    setup_logging(config)

    logging.info("Starting 'Exoplanet Catalog Analysis' program.")
    print("Welcome to the Exoplanet Catalog Analysis!")
    interactive_menu()

if __name__ == "__main__":
    main()
