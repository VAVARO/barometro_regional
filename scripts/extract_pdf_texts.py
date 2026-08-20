import os
import pypdf
import json

def extract_pdf_text(path):
    reader = pypdf.PdfReader(path)
    text = ""
    for i, page in enumerate(reader.pages):
        text += f"\n--- Page {i+1} ---\n" + (page.extract_text() or "")
    return text

# Check available PDFs
pdf_files = [
    r"C:\AGY\BAROMETRO\Diccionario de Variables - UAYSÉN. 2025.03.10.pdf",
    r"C:\AGY\BAROMETRO\Cuestionario Estudio Barómetro Regional Aysén_2024.12.27_v4_cambios post Pretest.pdf",
    r"C:\AGY\BAROMETRO\documentos_barometros_regionales\barometro_Informe-Nacional-Barometro-2024.pdf"
]

for pdf in pdf_files:
    if os.path.exists(pdf):
        print(f"Reading {pdf}...")
        t = extract_pdf_text(pdf)
        out_txt = os.path.splitext(pdf)[0] + "_extracted.txt"
        with open(out_txt, "w", encoding="utf-8") as f:
            f.write(t)
        print(f"Wrote extracted text ({len(t)} chars) to {out_txt}")
