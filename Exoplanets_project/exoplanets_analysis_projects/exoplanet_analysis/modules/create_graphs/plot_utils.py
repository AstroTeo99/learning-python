import plotly.express as px
import logging
import os

def save_chart(fig, chart_type):
    charts_dir = os.path.join('grafici', chart_type)
    os.makedirs(charts_dir, exist_ok=True)
    file_name = f"{chart_type}.html"
    chart_path = os.path.join(charts_dir, file_name)
    fig.write_html(chart_path)
    logging.info(f"Chart saved in '{chart_path}'.")
    fig.show()
