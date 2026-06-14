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

def _looks_like_header(row):
    """Detects if a row is a header using the safe, conservative >50% text rule."""
    if not row or len(row) == 0: 
        return False
        
    str_count = sum(1 for x in row if isinstance(x, str) and str(x).strip())
    if str_count >= (len(row) / 2) and str_count >= 1: 
        return True
        
    return False

def execute_code(code: str, sheet_data: dict) -> dict:
    try:
        # Convert JSON sheets to DataFrames and extract headers natively
        dfs = {}
        for name, data in sheet_data.items():
            if 'cells' in data and data['cells']:
                df = pd.DataFrame(data['cells'])
                if len(df) > 0:
                    row0 = df.iloc[0].tolist()
                    if _looks_like_header(row0):
                        df.columns = row0
                        df = df.iloc[1:].reset_index(drop=True)
                dfs[name] = df

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

        # Prepare output DataFrames and restore headers
        modified_dfs = execution_globals['dfs']
        output_data = {}
        for name, df in modified_dfs.items():
            df = df.fillna('')
            # If the dataframe has custom columns, put them back into Row 0
            is_default_cols = isinstance(df.columns, pd.RangeIndex) or list(df.columns) == list(range(len(df.columns)))
            if not is_default_cols:
                new_data = [df.columns.tolist()] + df.values.tolist()
                df = pd.DataFrame(new_data)
                
            output_df = df.astype(str).replace('nan', '')
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
