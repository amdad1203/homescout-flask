# utils.py

def to_int(x):
    try:
        return int(x)
    except:
        return None

def to_float(x):
    try:
        return float(x)
    except:
        return None

def currency(x):
    try:
        return f"{float(x):,.2f}"
    except:
        return x
