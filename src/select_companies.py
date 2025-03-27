# src/select_companies.py

import pandas as pd
import random

def select_companies(modo):
    df = pd.read_csv('company_list.csv')

    if modo == 0:
        print("Seleccionando TODAS las empresas del listado.")
        return df

    elif modo == 1:
        print("Introduce los tickers deseados separados por coma "
              "(ej: AAPL,MSFT,GOOG):")
        input_str = input("Tickers: ").upper()
        tickers = [ticker.strip() for ticker in input_str.split(',')]
        seleccion = df[df['ticker'].isin(tickers)]
        print(f"{len(seleccion)} compañías seleccionadas.")
        return seleccion

    elif modo == 2:
        print("Seleccionando 10 empresas aleatorias.")
        return df.sample(10)

    else:
        raise ValueError("Modo no válido (debe ser 0, 1 o 2).")
