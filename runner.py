# runner.py - Execute Python code safely with allowed libraries

import pandas as pd
import numpy as np
import traceback
import matplotlib
import seaborn
import plotly
import requests
from bs4 import BeautifulSoup
import cvxpy
import networkx
import statsmodels.api as sm
from fuzzywuzzy import fuzz
from textblob import TextBlob

def execute_code(code: str, sheet_data: dict) -> dict:
    """
    Executes user-provided Python code on given sheet data.
    
    :param code: Python code as string
    :param sheet_data: Dictionary of sheet data (JSON-like)
    :return: Dictionary with status and modified data or error message
    """
    try:
        # Convert JSON sheets to pandas DataFrames
        dfs = {
            name: pd.DataFrame(data['cells'])
            for name, data in sheet_data.items()
            if 'cells' in data and data['cells']
        }

        # Define the allowed globals for exec
        execution_globals = {
            'dfs': dfs,
            'pd': pd,
            'np': np,
            'matplotlib': matplotlib,
            'seaborn': seaborn,
            'plotly': plotly,
            'requests': requests,
            'BeautifulSoup': BeautifulSoup,
            'cvxpy': cvxpy,
            'networkx': networkx,
            'statsmodels': sm,
            'fuzz': fuzz,
            'TextBlob': TextBlob,
        }

        # Execute user code safely
        exec(code, execution_globals)

        # Prepare output
        modified_dfs = execution_globals['dfs']
        output_data = {}
        for name, df in modified_dfs.items():
            # Convert NaNs to empty strings and export as list
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

