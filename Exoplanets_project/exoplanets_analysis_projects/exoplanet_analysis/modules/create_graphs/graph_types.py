import plotly.express as px
import logging
import pandas as pd
import re
import os
import time

from .plot_utils import save_chart
from .expression_evaluator import evaluate_expression
from .model_fitting import fit_and_choose_best_model, generate_best_fit_template

def create_personal_chart(df, x_expr, y_expr, columns_info, data_file_path):
    logging.info(f"Creating chart for X='{x_expr}' vs Y='{y_expr}'.")

    try:
        has_pl_name = ('pl_name' in df.columns and df['pl_name'].notna().any())

        def extract_colname(expr):
            pattern = r'^(.*?)\s*\[(.*?)\]\s*$'
            match = re.match(pattern, expr.strip())
            if match:
                return match.group(1).strip()
            return expr.strip()

        xcol = extract_colname(x_expr)
        ycol = extract_colname(y_expr)

        x_val, x_err = evaluate_expression(xcol, df)
        y_val, y_err = evaluate_expression(ycol, df)
        if x_val is None or y_val is None:
            logging.error("Error evaluating expressions.")
            print("Error evaluating expressions. Check logs.")
            return

        plot_df = pd.DataFrame({
            'X': x_val,
            'Y': y_val
        })

        def get_asymmetric_errors(col):
            """
            Return (err_plus, err_minus) for the column.
            If colerr1/colerr2 exist, use them. Else, (0,0).
            """
            colerr1 = col + 'err1'
            colerr2 = col + 'err2'
            if colerr1 in df.columns and colerr2 in df.columns:
                eplus = df[colerr1].abs()
                eminus = df[colerr2].abs()
                return eplus, eminus
            else:
                return pd.Series([0]*len(df)), pd.Series([0]*len(df))

        x_plus, x_minus = get_asymmetric_errors(xcol)
        y_plus, y_minus = get_asymmetric_errors(ycol)

        plot_df['X_err_plus'] = x_plus
        plot_df['X_err_minus'] = x_minus
        plot_df['Y_err_plus'] = y_plus
        plot_df['Y_err_minus'] = y_minus

        if has_pl_name:
            plot_df['pl_name'] = df['pl_name']

        plot_df.dropna(subset=['X','Y'], inplace=True)

        eb_choice = input("Do you want to enable error bars? (y/n): ").strip().lower()
        show_err_bars = (eb_choice == 'y')

        log_choice = input("Do you want to use log scale? (none/x/y/both): ").strip().lower()
        is_log_x = (log_choice in ['x','both'])
        is_log_y = (log_choice in ['y','both'])

        folder_name = f"{xcol}_VS_{ycol}"
        chart_root = os.path.join('grafici', folder_name)
        os.makedirs(chart_root, exist_ok=True)

        existing_subfolders = [
            d for d in os.listdir(chart_root)
            if os.path.isdir(os.path.join(chart_root, d)) and d.isdigit()
        ]
        next_num = 1
        if existing_subfolders:
            numeric_folders = sorted(int(f) for f in existing_subfolders)
            next_num = numeric_folders[-1] + 1

        this_chart_folder = os.path.join(chart_root, str(next_num))
        os.makedirs(this_chart_folder, exist_ok=True)

        x_desc = columns_info.get(xcol, {}).get('description', xcol)
        x_unit = columns_info.get(xcol, {}).get('unit', '')
        if x_unit:
            x_label = f"{x_desc} [{x_unit}]"
        else:
            x_label = x_desc

        y_desc = columns_info.get(ycol, {}).get('description', ycol)
        y_unit = columns_info.get(ycol, {}).get('unit', '')
        if y_unit:
            y_label = f"{y_desc} [{y_unit}]"
        else:
            y_label = y_desc

        import plotly.graph_objects as go
        fig = go.Figure()

        fig.add_trace(go.Scatter(
            x=plot_df['X'],
            y=plot_df['Y'],
            mode='markers',
            marker=dict(size=6, opacity=0.8),
            name=f"{xcol} vs {ycol}",
            error_x=dict(
                type='data',
                symmetric=False,
                array=plot_df['X_err_plus'],
                arrayminus=plot_df['X_err_minus'],
                visible=show_err_bars
            ),
            error_y=dict(
                type='data',
                symmetric=False,
                array=plot_df['Y_err_plus'],
                arrayminus=plot_df['Y_err_minus'],
                visible=show_err_bars
            ),
            hovertemplate="%{customdata}"
        ))

        fig.update_layout(
            title=f"{xcol} vs {ycol}",
            xaxis_title=x_label,
            yaxis_title=y_label
        )

        if is_log_x:
            fig.update_xaxes(type="log")
        if is_log_y:
            fig.update_yaxes(type="log")

        correlation = plot_df['X'].corr(plot_df['Y'])
        fig.add_annotation(
            text=f"Pearson correlation: {correlation}",
            xref="paper", yref="paper",
            x=0.05, y=0.95, showarrow=False,
            font=dict(size=12)
        )

        hover_texts = []
        for i, row in plot_df.iterrows():
            x_val_str = str(row['X'])
            y_val_str = str(row['Y'])
            xp = row['X_err_plus']
            xm = row['X_err_minus']
            yp = row['Y_err_plus']
            ym = row['Y_err_minus']

            x_err_str = ""
            if xp>0 or xm>0:
                x_err_str = f" (+{xp} / -{xm})"
            y_err_str = ""
            if yp>0 or ym>0:
                y_err_str = f" (+{yp} / -{ym})"

            if has_pl_name:
                planet_name = row['pl_name']
                hover_texts.append(
                    f"Name: {planet_name}<br>"
                    f"X: {x_val_str}{x_err_str}<br>"
                    f"Y: {y_val_str}{y_err_str}"
                )
            else:
                hover_texts.append(
                    f"X: {x_val_str}{x_err_str}<br>"
                    f"Y: {y_val_str}{y_err_str}"
                )

        fig.data[0].customdata = hover_texts

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        html_name = f"{folder_name}_{timestamp}.html"
        html_path = os.path.join(this_chart_folder, html_name)
        fig.write_html(html_path)
        logging.info(f"Chart saved in '{html_path}'.")
        fig.show()

        ans = input("\nDo you want to perform a multi-model fit and detect outliers? (y/n): ").strip().lower()
        if ans == 'y':
            x_array = plot_df['X'].values
            y_array = plot_df['Y'].values

            fit_info = fit_and_choose_best_model(
                x_array, y_array,
                min_points=5,
                std_threshold=2,
                is_log_x=is_log_x,
                is_log_y=is_log_y
            )
            if fit_info is None:
                print("Fit not performed (too few data or no convergence).")
            else:
                if 'models_evaluation' in fit_info:
                    print("\n--- Models evaluation ---")
                    for me in fit_info['models_evaluation']:
                        print(f"Model: {me['model_name']}, AIC: {me['aic']:.3f}, R^2: {me['r2']:.3f}")
                    print("------------------------")

                best_model_name = fit_info['best_model_name']
                best_popt = fit_info['best_popt']
                best_aic = fit_info['best_aic']
                print(f"\nBest model found: {best_model_name}")
                print(f"Parameters: {best_popt}")
                print(f"AIC: {best_aic:.3f}")

                outliers_df = fit_info['outliers_df']
                if not outliers_df.empty:
                    if has_pl_name:
                        outliers_df['pl_name'] = ""
                        for idx_outl, row_outl in outliers_df.iterrows():
                            ox = row_outl['orig_x']
                            oy = row_outl['orig_y']
                            match = plot_df[
                                (plot_df['X']==ox) & (plot_df['Y']==oy)
                            ]
                            if not match.empty and 'pl_name' in match.columns:
                                outliers_df.at[idx_outl, 'pl_name'] = match.iloc[0]['pl_name']

                    outliers_filename = f"outliers_{timestamp}.csv"
                    outliers_path = os.path.join(this_chart_folder, outliers_filename)

                    outliers_df['detection_method'] = "Residual > 2 * std threshold"
                    outliers_df['reason'] = "Deviation from best model"
                    outliers_df['best_model'] = best_model_name
                    outliers_df['parameters'] = str(best_popt)
                    outliers_df['chosen_AIC'] = best_aic

                    try:
                        outliers_df.to_csv(outliers_path, index=False)
                        print(f"\nDetected {len(outliers_df)} outliers. Saved in:\n{outliers_path}")
                    except PermissionError as pe:
                        logging.error(f"Permission denied: {pe}")
                        print("Error: Could not save outliers file. Close any application that might be using it.")
                else:
                    print("\nNo relevant outliers found.")

                py_filename = f"best_fit_template_{timestamp}.py"
                py_path = generate_best_fit_template(
                    folder_path=this_chart_folder,
                    plot_title=f"{folder_name}",
                    x_col=xcol,
                    y_col=ycol,
                    x_label=x_label,
                    y_label=y_label,
                    model_info=fit_info,
                    data_file_path=data_file_path,
                    custom_filename=py_filename
                )
                if py_path:
                    print(f"\nA template file has been generated:\n{py_path}")
                    print("You can edit it to regenerate the chart with your data and the best-fit curve.")
    except Exception as e:
        logging.error(f"Error in 'create_personal_chart': {e}")
        print("An error occurred while creating the chart. Check logs for details.")
