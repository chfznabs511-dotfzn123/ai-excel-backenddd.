# runner.py - Optimized for Render free tier with Plotly charts

import pandas as pd
import numpy as np
import numpy_financial as npf
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
        # 1. WAY IN: Do NOT guess headers. Pass the raw 2D Canvas directly to the AI.
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
            'npf': npf,
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

        # 2. WAY OUT: Pack DataFrames back into 2D Arrays.
        # If the AI explicitly defined custom Pandas columns, prepend them into the 2D array!
        modified_dfs = execution_globals['dfs']
        output_data = {}
        for name, df in modified_dfs.items():
            # Check if columns are custom
            is_default_cols = isinstance(df.columns, pd.RangeIndex) or list(df.columns) == list(range(len(df.columns)))
            
            # Convert NaN to empty string for clean JSON
            df = df.fillna('')
            
            if not is_default_cols:
                # Prepend custom columns to the values matrix so they don't vanish
                new_data = [df.columns.tolist()] + df.values.tolist()
                output_df = pd.DataFrame(new_data)
            else:
                output_df = df
                
            # Convert everything to string for JSON serialization
            output_df = output_df.astype(str).replace('nan', '')
            output_data[name] = {'cells': output_df.values.tolist()}

        # Prepare Plotly chart if created
        chart_base64 = None
        if 'fig' in execution_globals:
            fig = execution_globals['fig']
            # Convert Plotly figure to PNG in memory with higher resolution
            img_bytes = fig.to_image(format="png", scale=5, engine="kaleido")
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
