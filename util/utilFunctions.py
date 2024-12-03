import pandas as pd


def custom_round(number):
    if isinstance(number, pd.Series):
        number = number.iloc[0]
    
    int_part = int(number)
    
    if number - int_part >= 0.5:
        return int_part + 1
    else:
        return int_part
    

