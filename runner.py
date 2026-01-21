# runner.py - Optimized for large data and Excel compatibility
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
        # Convert JSON sheets to DataFrames
        dfs = {
            name: pd.DataFrame(data['cells'])
            for name, data in sheet_data.items()
            if 'cells' in data and data['cells']
        }

        execution_globals = {
            'dfs': dfs, 'pd': pd, 'np': np, 'npf': npf,
            'requests': requests, 'BeautifulSoup': BeautifulSoup,
            'statsmodels': sm, 'fuzz': fuzz, 'px': px, 'pio': pio, 'base64': base64,
        }

        # Execute user code
        exec(code, execution_globals)

        # Prepare output DataFrames
        modified_dfs = execution_globals['dfs']
        output_data = {}
        for name, df in modified_dfs.items():
            # Keep numbers as numbers and dates as dates
            output_df = df.fillna('') 
            output_data[name] = {'cells': output_df.values.tolist()}

        # Prepare Plotly chart if created
        chart_base64 = None
        if 'fig' in execution_globals:
            fig = execution_globals['fig']
            img_bytes = fig.to_image(format="png", scale=5, engine="kaleido")
            chart_base64 = base64.b64encode(img_bytes).decode('utf-8')

        return {'status': 'success', 'data': output_data, 'chart': chart_base64}

    except Exception as e:
        traceback_str = traceback.format_exc()
        return {
            'status': 'error',
            'message': f"Execution failed with {type(e).__name__}: {str(e)}"
        }
