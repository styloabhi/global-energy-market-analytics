"""
Defines the global energy stock universe used in the application.
This is the ONLY place where core stock lists are maintained.
"""

ENERGY_STOCKS = {
    "United States": {
        "XOM": "Exxon Mobil",
        "CVX": "Chevron",
        "COP": "ConocoPhillips",
        "OXY": "Occidental Petroleum",
        "PSX": "Phillips 66"
    },
    "Europe": {
        "SHEL": "Shell",
        "BP": "BP",
        "TTE": "TotalEnergies",
        "E": "Eni",
        "EQNR": "Equinor",
        "REP.MC": "Repsol"
    },
    "India (NSE)": {
        "RELIANCE.NS": "Reliance Industries",
        "IOC.NS": "Indian Oil",
        "ONGC.NS": "ONGC",
        "BPCL.NS": "BPCL",
        "HINDPETRO.NS": "Hindustan Petroleum",
        "GAIL.NS": "GAIL"
    },
    "Other Markets": {
        "PBR": "Petrobras",
        "EC": "Ecopetrol",
        "SU": "Suncor Energy",
        "CNQ": "Canadian Natural Resources",
        "IMO": "Imperial Oil",
        "5020.T": "ENEOS",
        "1605.T": "Inpex",
        "2222.SR": "Saudi Aramco"
    }
}

# --------------------------------------------------
# Derived helpers (DO NOT duplicate data elsewhere)
# --------------------------------------------------

def get_all_tickers() -> list:
    """Returns flat list of all tickers."""
    return [
        ticker
        for region in ENERGY_STOCKS.values()
        for ticker in region.keys()
    ]


def get_ticker_name_map() -> dict:
    """Returns {ticker: company_name} mapping."""
    return {
        ticker: name
        for region in ENERGY_STOCKS.values()
        for ticker, name in region.items()
    }
