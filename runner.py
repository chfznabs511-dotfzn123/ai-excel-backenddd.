# runner.py # For executing Python code or data operations

import pandas as pd
import numpy as np
import io
import traceback

# Import all allowed libraries
import scipy
import dask
import stringcase
import unidecode
import statsmodels
import pingouin
import sklearn
from fuzzywuzzy import fuzz
from textblob import TextBlob
import re
import matplotlib
import seaborn
import plotly
import missingno
import requests
from bs4 import BeautifulSoup
import cvxpy
import networkx
import openpyxl
import xlsxwriter


def execute_code(code: str, sheet_data: dict) -> dict:
    try:
        # Convert JSON sheets to DataFrames
        dfs = {
            name: pd.DataFrame(data['cells'])
            for name, data in sheet_data.items()
            if 'cells' in data and data['cells']
        }

        execution_globals = {
            'dfs': dfs,
            'pd': pd,
            'np': np,
            'scipy': scipy,
            'dask': dask,
            'stringcase': stringcase,
            'unidecode': unidecode,
            'statsmodels': statsmodels,
            'pingouin': pingouin,
            'sklearn': sklearn,
            'fuzz': fuzz,
            'TextBlob': TextBlob,
            're': re,
            'matplotlib': matplotlib,
            'seaborn': seaborn,
            'plotly': plotly,
            'missingno': missingno,
            'requests': requests,
            'BeautifulSoup': BeautifulSoup,
            'cvxpy': cvxpy,
            'networkx': networkx,
            'openpyxl': openpyxl,
            'xlsxwriter': xlsxwriter,
            
        }

        exec(code, execution_globals)

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
