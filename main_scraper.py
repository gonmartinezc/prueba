# main_scraper.py

from src.select_companies import select_companies
from src.connection import validate_connection

# Los siguientes módulos se agregan más adelante:
# from src import extract_filings, download_xml, extract_xbrl

def main():
    print("=== SEC Scraper ===")
    print("Selecciona modo de ejecución:")
    print(" 0 - Todas las empresas")
    print(" 1 - Empresas seleccionadas manualmente")
    print(" 2 - 10 empresas aleatorias")

    try:
        modo = int(input("Modo: "))
    except ValueError:
        print("Entrada inválida. Debe ser un número.")
        return

    companies_df = select_companies(modo)

    if not validate_connection():
        print("Error de conexión con la SEC. Abortando.")
        return

    # Aquí irán los siguientes pasos del pipeline
    # extract_filings.run(companies_df)
    # download_xml.run(companies_df)
    # extract_xbrl.run(companies_df)

    print("Proceso inicial completado.")

if __name__ == "__main__":
    main()
