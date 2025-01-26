import pandas as pd
import fitz
import os
from datetime import datetime
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfbase.pdfmetrics import stringWidth
import subprocess
import sys
import time

PDF_TEMPLATE = r"C:\Users\matte\Desktop\Programma\fattura_base.pdf"
OUTPUT_DIR = r"C:\Users\matte\Desktop\Programma\Fatture"
EXCEL_FILE = r"C:\Users\matte\Desktop\Programma\dati_fattura.xlsm"
FONT_DIR = r"C:\Users\matte\Desktop\Programma\fonts"

font_files = {
    "TTNormsPro-Light": "TTNormsPro-Light.ttf",
    "TTNormsPro-Regular": "TTNormsPro-Regular.ttf",
    "TTNormsPro-Bold": "TTNormsPro-Bold.ttf",
    "TTNormsPro-BoldItalic": "TTNormsPro-BoldItalic.ttf",
    "TTNormsPro-Italic": "TTNormsPro-Italic.ttf"
}

for font_name, font_file in font_files.items():
    pdfmetrics.registerFont(TTFont(font_name, os.path.join(FONT_DIR, font_file)))

# Crea la cartella di output se non esiste
os.makedirs(OUTPUT_DIR, exist_ok=True)

def calcola_larghezza_testo(text, fontname, fontsize):
    return stringWidth(text, fontname, fontsize)

def compila_pdf(input_pdf_path, output_pdf_path, data_dict):
    documento = fitz.open(input_pdf_path)
    pagina = documento[0]

    for font_name, font_path in font_files.items():
        pagina.insert_font(fontfile=os.path.join(FONT_DIR, font_path), fontname=font_name)

    font_size = 12

    campi_allineati_destra = [
        {"nome": "numero_fattura", "testo": f"Numero: {data_dict['numero_fattura']}", "x_mm": 186.8, "y_mm": 34.6, "font": "TTNormsPro-Light"},
        {"nome": "data", "testo": f"Data: {data_dict['data']}", "x_mm": 186.8, "y_mm": 42.2, "font": "TTNormsPro-Light"},
        {"nome": "totale1", "testo": f"{data_dict['totale1']}", "x_mm": 183.5, "y_mm": 197.4, "font": "TTNormsPro-Regular"},
        {"nome": "iva", "testo": f"{data_dict['iva']}", "x_mm": 183.5, "y_mm": 206.2, "font": "TTNormsPro-Regular"},
        {"nome": "marca_da_bollo", "testo": f"{data_dict['marca_da_bollo']}", "x_mm": 183.5, "y_mm": 214.9, "font": "TTNormsPro-Regular"},
        {"nome": "netto", "testo": f"{data_dict['netto']}", "x_mm": 183.5, "y_mm": 223.9, "font": "TTNormsPro-BoldItalic"}
    ]

    for campo in campi_allineati_destra:
        target_x_mm = campo["x_mm"]
        target_y_mm = campo["y_mm"]
        testo = campo["testo"]
        font_name = campo["font"]

        target_x_punti = target_x_mm * 72 / 25.4
        target_y_punti = target_y_mm * 72 / 25.4
        larghezza_testo = calcola_larghezza_testo(testo, font_name, font_size)
        x_inizio = target_x_punti - larghezza_testo
        pagina.insert_text((x_inizio, target_y_punti), testo, fontsize=font_size, fontname=font_name, color=(0, 0, 0))

    campi_allineati_sinistra = [
        {"nome": "nome_cognome", "testo": data_dict["nome_cognome"], "x_mm": 67.4, "y_mm": 99.7, "font": "TTNormsPro-Regular"},
        {"nome": "codice_fiscale", "testo": data_dict["codice_fiscale"], "x_mm": 60.8, "y_mm": 108.3, "font": "TTNormsPro-Regular"}
    ]

    for campo in campi_allineati_sinistra:
        target_x_mm = campo["x_mm"]
        target_y_mm = campo["y_mm"]
        testo = campo["testo"].strip()
        font_name = campo["font"]

        target_x_punti = target_x_mm * 72 / 25.4
        target_y_punti = target_y_mm * 72 / 25.4
        pagina.insert_text((target_x_punti, target_y_punti), testo, fontsize=font_size, fontname=font_name, color=(0, 0, 0))

    campi_centrati = [
        {"nome": "quantità", "testo": data_dict["quantità"], "x_mm": 115, "y_mm": 146.5, "font": "TTNormsPro-Bold"},
        {"nome": "prezzo", "testo": data_dict["prezzo"], "x_mm": 142.8, "y_mm": 146.5, "font": "TTNormsPro-Regular"},
        {"nome": "totale", "testo": data_dict["totale1"], "x_mm": 175.3, "y_mm": 146.5, "font": "TTNormsPro-Regular"}
    ]

    for campo in campi_centrati:
        target_x_mm = campo["x_mm"]
        target_y_mm = campo["y_mm"]
        testo = campo["testo"]
        font_name = campo["font"]

        target_x_punti = target_x_mm * 72 / 25.4
        target_y_punti = target_y_mm * 72 / 25.4
        larghezza_testo = calcola_larghezza_testo(testo, font_name, font_size)
        x_inizio = target_x_punti - larghezza_testo / 2
        pagina.insert_text((x_inizio, target_y_punti), testo, fontsize=font_size, fontname=font_name, color=(0, 0, 0))

    box_x1_mm = 26.8
    box_y1_mm = 146.5
    box_x2_mm = 101.6
    box_y2_mm = 182.6

    box_x1_punti = box_x1_mm * 72 / 25.4
    box_y1_punti = box_y1_mm * 72 / 25.4
    box_x2_punti = box_x2_mm * 72 / 25.4
    box_y2_punti = box_y2_mm * 72 / 25.4

    testo_descrizione = data_dict["descrizione"]
    font_name = "TTNormsPro-Italic"
    linea_altezza = font_size * 1.2
    y_posizione = box_y1_punti

    parole = testo_descrizione.split()
    riga_corrente = ""
    y_posizione = box_y1_punti

    for parola in parole:
        if calcola_larghezza_testo(riga_corrente + parola + " ", font_name, font_size) <= (box_x2_punti - box_x1_punti):
            riga_corrente += parola + " "
        else:
            pagina.insert_text((box_x1_punti, y_posizione), riga_corrente.strip(), fontsize=font_size, fontname=font_name, color=(0, 0, 0))
            y_posizione += linea_altezza
            riga_corrente = parola + " "
            
            if y_posizione > box_y2_punti:
                break

    if riga_corrente:
        pagina.insert_text((box_x1_punti, y_posizione), riga_corrente.strip(), fontsize=font_size, fontname=font_name, color=(0, 0, 0))

    documento.save(output_pdf_path)
    documento.close()

# Comprime un singolo file PDF (sovrascrivendo l'originale)
def compress_pdf(input_file):
    if sys.platform.startswith('win'):
        gs_command_base = 'gswin64c'  # o 'gswin32c' a seconda della propria installazione
    else:
        gs_command_base = 'gs'

    # Crea un file temporaneo per evitare conflitti durante la sovrascrittura
    temp_output = input_file + ".tmp"

    gs_command = [
        gs_command_base,
        '-sDEVICE=pdfwrite',
        '-dCompatibilityLevel=1.4',
        '-dPDFSETTINGS=/ebook',  # Modifica questo parametro per qualità/compressione
        '-dNOPAUSE',
        '-dQUIET',
        '-dBATCH',
        f'-sOutputFile={temp_output}',
        input_file
    ]

    if sys.platform.startswith('win'):
        creationflags = subprocess.CREATE_NO_WINDOW
        result = subprocess.run(gs_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, creationflags=creationflags)
    else:
        result = subprocess.run(gs_command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if result.returncode != 0:
        print(f'Errore durante la compressione di {input_file}: {result.stderr.decode()}')
    else:
        os.replace(temp_output, input_file)

df = pd.read_excel(EXCEL_FILE, skiprows=2)

scelta = input("Generare i PDF di tutte le righe o di un intervallo? (T per tutte, I per intervallo): ").strip().upper()

if scelta == "T":
    righe_da_generare = df.index
elif scelta == "I":
    numero_iniziale = int(input("Da quale numero fattura? "))
    numero_finale = int(input("A quale numero fattura? "))
    righe_da_generare = df[(df.iloc[:, 8] >= numero_iniziale) & (df.iloc[:, 8] <= numero_finale)].index

    if len(righe_da_generare) == 0:
        print("Nessuna fattura trovata nell'intervallo specificato.")
        exit()

    nome_iniziale = df.loc[righe_da_generare[0], df.columns[0]].strip()
    nome_finale = df.loc[righe_da_generare[-1], df.columns[0]].strip()
    conferma = input(f"Generare i PDF dal numero {numero_iniziale} ({nome_iniziale}) fino al numero {numero_finale} ({nome_finale})? (Y/N): ").strip().upper()
    if conferma != "Y":
        exit()
else:
    print("Scelta non valida.")
    exit()

for idx in righe_da_generare:
    numero_fattura = df.iloc[idx, 8]
    totale_valore = df.iloc[idx, 3] * df.iloc[idx, 4]
    totale_formattato = f"€ {totale_valore:.2f}".replace('.', ',')
    data_format = pd.to_datetime(df.iloc[idx, 7], dayfirst=True).strftime("%d/%m/%Y")

    dati = {
        "nome_cognome": df.iloc[idx, 0],
        "codice_fiscale": df.iloc[idx, 1],
        "descrizione": df.iloc[idx, 2],
        "quantità": str(df.iloc[idx, 3]),
        "prezzo": f"€ {df.iloc[idx, 4]:.2f}".replace('.', ','),
        "iva": f"{df.iloc[idx, 5]:.2f}".replace('.', ',') + " %",
        "marca_da_bollo": f"€ {df.iloc[idx, 6]:.2f}".replace('.', ','),
        "totale1": totale_formattato,
        "netto": f"€ {(totale_valore * (1 + df.iloc[idx, 5] * 0.01) + df.iloc[idx, 6]):.2f}".replace('.', ','),
        "numero_fattura": numero_fattura,
        "data": data_format
    }

    nome_cognome_pulito = dati["nome_cognome"].strip()
    output_pdf_path = os.path.join(OUTPUT_DIR, f"Fatt. n. {numero_fattura} - {nome_cognome_pulito}.pdf")

    compila_pdf(PDF_TEMPLATE, output_pdf_path, dati)
    print(f"Generato PDF: {output_pdf_path}")

    # Assicura che il file sia stato completamente scritto su disco
    #time.sleep(0.5)  # Attendi mezzo secondo (puoi regolare o rimuovere questo se non necessario)

    # Comprime il PDF generato (sovrascrivendo l'originale)
    compress_pdf(output_pdf_path)
    print(f"Compresso PDF: {output_pdf_path}")

print("Processo completato.")
