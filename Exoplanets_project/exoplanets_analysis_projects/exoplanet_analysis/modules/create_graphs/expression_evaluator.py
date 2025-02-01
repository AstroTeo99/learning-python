import pandas as pd
import logging
from asteval import Interpreter, make_symbol_table
from math import sqrt
from .error_handling import calculate_propagated_uncertainty
from .constants import CONSTANTS

def evaluate_expression(expression, df, include_constant_uncertainty=True, log_x=False, log_y=False):
    sym_table = make_symbol_table(**{"sqrt": sqrt})
    aeval = Interpreter(symtable=sym_table)

    for col in df.columns:
        aeval.symtable[col] = df[col]

    for const, props in CONSTANTS.items():
        aeval.symtable[const] = props['value']

    try:
        result = aeval(expression)
    except Exception as e:
        logging.error(f"Error evaluating expression '{expression}': {e}")
        print(f"Error evaluating expression '{expression}': {e}")
        return None, None

    if isinstance(result, pd.Series):
        uncertainty = calculate_propagated_uncertainty(
            expression,
            df,
            include_constant_uncertainty=include_constant_uncertainty,
            log_transform_x=log_x,
            log_transform_y=log_y
        )
        return result, uncertainty
    else:
        logging.error(f"Expression '{expression}' did not produce a pandas Series.")
        print(f"Expression '{expression}' did not produce a pandas Series.")
        return None, None
