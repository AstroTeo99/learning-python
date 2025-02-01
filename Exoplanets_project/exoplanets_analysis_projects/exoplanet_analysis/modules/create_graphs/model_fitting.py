import logging
from pathlib import Path
import numpy as np
import pandas as pd
from scipy.optimize import curve_fit
import os

def fit_and_choose_best_model(x, y, min_points=5, std_threshold=2, is_log_x=False, is_log_y=False):
    def linear(x, m, c):
        return m * x + c

    def exponential(x, a, b):
        return a * np.exp(b * x)

    def power_law(x, a, b):
        return a * np.power(x, b)

    def logarithmic(x, a, b):
        return a * np.log(np.maximum(x, 1e-12)) + b

    models = {
        'linear': linear,
        'exponential': exponential,
        'power': power_law,
        'logarithmic': logarithmic
    }
    pass

def generate_best_fit_template(
    folder_path,
    plot_title,
    x_col,
    y_col,
    x_label,
    y_label,
    model_info,
    data_file_path,
    custom_filename
):
    data_ext = Path(data_file_path).suffix.lower()
    data_path_str = str(Path(data_file_path).resolve())

    load_data_snippet = ""
    if data_ext in ['.vot', '.votable', '.vot']:
        load_data_snippet = f"""from astropy.io.votable import parse
votable_file = parse(r'{data_path_str}')
table = votable_file.get_first_table()
df = table.to_table().to_pandas()
"""
    elif data_ext == '.csv':
        load_data_snippet = f"""import pandas as pd
df = pd.read_csv(r'{data_path_str}')
"""
    elif data_ext == '.db':
        load_data_snippet = f"""import sqlite3
import pandas as pd
conn = sqlite3.connect(r'{data_path_str}')
# If multiple tables, manually set the table name here:
table_name = 'YOUR_TABLE_NAME'
df = pd.read_sql_query(f"SELECT * FROM {{table_name}}", conn)
conn.close()
"""
    else:
        load_data_snippet = f"""import pandas as pd
df = pd.DataFrame()  # Unsupported extension, df empty
"""

    template = f'''import sys
import os
import time
import numpy as np
import plotly.express as px
from scipy.optimize import curve_fit
from pathlib import Path

this_file = Path(__file__).resolve()
project_root = this_file.parents[3]
sys.path.append(str(project_root))

{load_data_snippet}

if df.empty:
    print("Warning: DataFrame is empty (unsupported extension or problem loading).")
    import sys
    sys.exit(0)

print("Data loaded successfully.")
print("Columns in df:", df.columns.tolist())

x_data = df['{x_col}'].values
y_data = df['{y_col}'].values

print("\\n=== INTERACTIVE BEST FIT ===")
print("You can choose to provide a custom function or use a standard model.\\n")

def linear_func(x, m, c):
    return m*x + c

def exponential_func(x, a, b):
    return a*np.exp(b*x)

def log_func(x, a, b):
    return a*np.log(np.maximum(x,1e-12)) + b

def power_func(x, a, b):
    return a*(x**b)

def poly_generic(x, *params):
    val = np.zeros_like(x, dtype=float)
    for i, coef in enumerate(params):
        val += coef*(x**i)
    return val

def parse_custom_function(func_str):
    import re
    param_names = ['a','b','c','d','e','f','g','h','i','j']
    used_params = []
    for pn in param_names:
        if pn in func_str:
            used_params.append(pn)
    used_params_ordered = []
    for up in used_params:
        if up not in used_params_ordered:
            used_params_ordered.append(up)
    param_map = {pn: f"p[{i}]" for i,pn in enumerate(used_params_ordered)}
    custom_expr = func_str
    for pn in used_params_ordered:
        custom_expr = custom_expr.replace(pn, param_map[pn])
    def model_func(x, *p):
        return eval(custom_expr, {{"np":np, "x":x, "p":p}})
    return model_func, len(used_params_ordered)

def main():
    # Menu
    print("Choose an option:")
    print("1) Custom function (y(x) = ...)")
    print("2) Standard model (linear, exp, log, power, polynomial)")
    choice = input("Enter [1/2]: ").strip()

    if choice == '1':
        print("\\nYou selected custom function.")
        print("Type your function, e.g. 'a*x + b' or 'a*np.exp(b*x)' etc.")
        func_str = input("y(x) = ")
        custom_model, n_params = parse_custom_function(func_str)
        p0 = [1.0]*n_params
        try:
            popt, pcov = curve_fit(custom_model, x_data, y_data, p0=p0)
            print(f"Fitted parameters: {{popt}}")
            x_fit = np.linspace(x_data.min(), x_data.max(), 200)
            y_fit = custom_model(x_fit, *popt)
        except Exception as e:
            print("Error in curve_fit:", e)
            return
        model_name = "Custom"
    elif choice == '2':
        print("\\nSelect model:")
        print("1) linear (m*x + c)")
        print("2) exponential (a*exp(b*x))")
        print("3) log (a*ln(x) + b)")
        print("4) power (a*x^b)")
        print("5) polynomial of order N")
        mc = input("Enter [1..5]: ").strip()
        if mc == '1':
            model_func = linear_func
            p0 = [1,1]
            model_name = "Linear"
        elif mc == '2':
            model_func = exponential_func
            p0 = [1,1]
            model_name = "Exponential"
        elif mc == '3':
            model_func = log_func
            p0 = [1,1]
            model_name = "Log"
        elif mc == '4':
            model_func = power_func
            p0 = [1,1]
            model_name = "Power"
        elif mc == '5':
            N = input("Polynomial order N: ")
            try:
                N = int(N)
            except:
                N = 2
            model_func = poly_generic
            p0 = [1.0]*(N+1)
            model_name = f"Poly_order_{N}"
        else:
            print("Invalid choice. Exiting.")
            return
        try:
            popt, pcov = curve_fit(model_func, x_data, y_data, p0=p0)
            print(f"Fitted parameters: {{popt}}")
            x_fit = np.linspace(x_data.min(), x_data.max(), 200)
            y_fit = model_func(x_fit, *popt)
        except Exception as e:
            print("Error in curve_fit:", e)
            return
    else:
        print("Invalid choice. Exiting.")
        return

    import plotly.express as px
    fig = px.scatter(
        x=x_data, y=y_data,
        labels={{"x":"{x_label}", "y":"{y_label}"}},
        title=f"{plot_title} - Model: {{model_name}}"
    )
    fig.add_scatter(x=x_fit, y=y_fit, mode='lines', name="Best Fit")

    timestamp = int(time.time())
    html_name = f"best_fit_{{model_name}}_{{timestamp}}.html"
    fig.write_html(html_name)
    print(f"Plot saved in {{html_name}}.")

if __name__ == "__main__":
    main()
'''

    py_path = Path(folder_path) / custom_filename
    py_path.parent.mkdir(parents=True, exist_ok=True)
    with open(py_path, 'w', encoding='utf-8') as f:
        f.write(template)

    return str(py_path)
