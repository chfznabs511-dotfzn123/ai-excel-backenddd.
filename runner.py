# runner.py - Optimized for Render free tier with charting

import pandas as pd
import numpy as np
import traceback
import requests
from bs4 import BeautifulSoup
from fuzzywuzzy import fuzz
import statsmodels.api as sm
import matplotlib.pyplot as plt  # Lightweight chart library

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
            'requests': requests,
            'BeautifulSoup': BeautifulSoup,
            'statsmodels': sm,
            'fuzz': fuzz,
            'plt': plt,
        }

        exec(code, execution_globals)

        # Prepare output
        modified_dfs = execution_globals['dfs']
        output_data = {}
        for name, df in modified_dfs.items():
            output_df = df.astype(str).replace('nan', '')
            output_data[name] = {'cells': output_df.values.tolist()}

        return {'status': 'success', 'data': output_data}

    except Exception as e:
        traceback_str = traceback.format_exc()
        print("--- CODE EXECUTION ERROR ---")
        print(traceback_str)
        print("----------------------------")
        return {
            'status': 'error',
            'message': f"Execution failed with {type(e).__name__}: {str(e)}"
        }
