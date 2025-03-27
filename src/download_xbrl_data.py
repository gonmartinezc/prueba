import os
import xml.etree.ElementTree as ET
import pandas as pd
from typing import List, Dict
from datetime import datetime, timedelta

# Configuración general
TAGS_FILE = "../dataset/xbrl_tags_sample.csv"
XML_FOLDER = "../dataset/xml_reports"
OUTPUT_CSV = "../dataset/xbrl_data_extracted.csv"

# Cargar etiquetas desde CSV
def load_tag_list(tags_file: str) -> List[str]:
    tags_df = pd.read_csv(tags_file)
    return tags_df["tag_name"].str.strip().str.lower().tolist()

# Extraer contextoRef relevante basado en la fecha estimada del informe
def extract_relevant_contexts(root, target_date: str) -> List[str]:
    contexts = []
    try:
        filing_dt = datetime.strptime(target_date, "%Y%m%d")
        for elem in root.findall(".//{http://www.xbrl.org/2003/instance}context"):
            context_id = elem.attrib.get("id", "")
            end_date_elem = elem.find(".//{http://www.xbrl.org/2003/instance}endDate")
            if end_date_elem is not None:
                try:
                    context_dt = datetime.strptime(end_date_elem.text.strip(), "%Y-%m-%d")
                    if abs((context_dt - filing_dt).days) <= 1:
                        contexts.append(context_id)
                except:
                    continue
    except:
        pass
    return contexts

# Extraer datos de un archivo XML

def extract_from_xml(xml_path: str, tag_list: List[str]) -> Dict[str, str]:
    data = {}
    try:
        tree = ET.parse(xml_path)
        root = tree.getroot()

        # Inferir fecha desde el nombre del archivo: ejemplo goog-20221231_htm.xml
        filename = os.path.basename(xml_path)
        date_part = filename.split("-")[-1].split("_")[0]  # "20221231"
        relevant_contexts = extract_relevant_contexts(root, date_part)

        for elem in root.iter():
            tag = elem.tag.split("}")[-1].strip().lower()
            context = elem.attrib.get("contextRef", "")
            if tag in tag_list and elem.text and context in relevant_contexts:
                data[tag] = elem.text.strip()

    except Exception as e:
        print(f"Error processing {xml_path}: {e}")
    return data

# Procesar todos los XML en la carpeta
def process_all_xml(xml_folder: str, tag_list: List[str]) -> pd.DataFrame:
    records = []
    for filename in os.listdir(xml_folder):
        if filename.endswith(".xml"):
            xml_path = os.path.join(xml_folder, filename)
            print(f"Processing: {filename}")
            row = extract_from_xml(xml_path, tag_list)

            # Inferir metadatos desde el nombre del archivo
            row["filename"] = filename
            row["accession_number"] = filename.replace("_htm.xml", "").replace(".xml", "")
            records.append(row)
    return pd.DataFrame(records)

if __name__ == "__main__":
    tag_list = load_tag_list(TAGS_FILE)
    df = process_all_xml(XML_FOLDER, tag_list)

    # Reordenar columnas: metadatos primero
    cols = ["filename", "accession_number"] + [tag for tag in tag_list if tag in df.columns]
    df = df[cols]

    df.to_csv(OUTPUT_CSV, index=False)
    print(f"Saved extracted XBRL data to {OUTPUT_CSV}")



