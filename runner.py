# runner.py - Optimized for Render free tier with Plotly charts

import pandas as pd
import numpy as np
import numpy_financial as npf  # <-- added numpy-financial
import traceback
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import statsmodels.api as sm
import plotly.express as px
import plotly.io as pio
import base64

def execute_code(code: str, sheet_data: dict) -> dict:
    try:
        # Convert JSON sheets to DataFrames
        dfs = {
            name: pd.DataFrame(data['cells'])
            for name, data in sheet_data.items()
            if 'cells' in data and data['cells']
        }

        # Allowed globals
        execution_globals = {
            'dfs': dfs,
            'pd': pd,
            'np': np,
            'npf': npf,  # <-- added numpy-financial to globals
            'requests': requests,
            'BeautifulSoup': BeautifulSoup,
            'statsmodels': sm,
            'fuzz': fuzz,
            'px': px,
            'pio': pio,
            'base64': base64,
        }

        # Execute user code
        exec(code, execution_globals)

        # Prepare output DataFrames
        modified_dfs = execution_globals['dfs']
        output_data = {}
        for name, df in modified_dfs.items():
            output_df = df.astype(str).replace('nan', '')
            output_data[name] = {'cells': output_df.values.tolist()}

        # Prepare Plotly chart if created
        chart_base64 = None
        if 'fig' in execution_globals:
            fig = execution_globals['fig']
            # Convert Plotly figure to PNG in memory with higher resolution
            img_bytes = fig.to_image(format="png", scale=6, engine="kaleido")  # <-- added scale and engine
            chart_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return {'status': 'success', 'data': output_data, 'chart': chart_base64}

    except Exception as e:
        traceback_str = traceback.format_exc()
        print("--- CODE EXECUTION ERROR ---")
        print(traceback_str)
        print("----------------------------")
        return {
            'status': 'error',
            'message': f"Execution failed with {type(e).__name__}: {str(e)}"
        }
