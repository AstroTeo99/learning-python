import sympy as sp
import numpy as np
import pandas as pd
import logging
from .constants import CONSTANTS

def calculate_propagated_uncertainty(expression, df, include_constant_uncertainty=True, log_transform_x=False, log_transform_y=False):
    symbols = {}
    for col in df.columns:
        symbols[col] = sp.Symbol(col)
    for const in CONSTANTS:
        symbols[const] = sp.Symbol(const)

    try:
        expr = sp.sympify(expression, locals=symbols)
    except Exception as e:
        logging.error(f"Error parsing expression '{expression}': {e}")
        print(f"Error parsing expression '{expression}': {e}")
        return None

    derivatives = {}
    for var in symbols:
        derivatives[var] = expr.diff(symbols[var])

    ordered_vars = list(df.columns) + list(CONSTANTS.keys())
    deriv_funcs = {}
    for var, deriv in derivatives.items():
        deriv_funcs[var] = sp.lambdify([symbols[v] for v in ordered_vars], deriv, 'numpy')

    data_arrays = []
    for c in df.columns:
        data_arrays.append(df[c].values)
    for c in CONSTANTS:
        data_arrays.append(CONSTANTS[c]['value'])

    n_rows = len(df)
    uncertainty_sq = np.zeros(n_rows, dtype=float)

    for var in derivatives:
        if var in df.columns:
            err1 = var + 'err1'
            err2 = var + 'err2'
            if err1 in df.columns and err2 in df.columns:
                delta_plus = df[err1].abs()
                delta_minus = df[err2].abs()
                delta = 0.5 * (delta_plus + delta_minus)
            else:
                delta = 0
        elif var in CONSTANTS and include_constant_uncertainty:
            delta = CONSTANTS[var]['uncertainty']
        else:
            delta = 0

        deriv_val = deriv_funcs[var](*data_arrays)
        if isinstance(delta, (int, float)):
            part = (deriv_val * delta) ** 2
        else:
            part = (deriv_val * delta.values) ** 2
        uncertainty_sq += part

    total_uncertainty = np.sqrt(uncertainty_sq)
    return pd.Series(total_uncertainty, index=df.index)
