"""
upload_s3.py — Sube los archivos PDF de la carpeta s3/ a un bucket de Amazon S3.

Uso:
    python upload_s3.py

Requisitos:
    - Tener configuradas las credenciales de AWS (aws configure)
    - Tener un archivo .env con las variables S3_BUCKET_NAME y AWS_REGION
"""

import os
import sys
import boto3
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

# --- Configuracion ---
AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
S3_BUCKET_NAME = os.environ.get("S3_BUCKET_NAME")

CARPETA_LOCAL = Path(__file__).parent / "s3"


def validar_configuracion():
    """Verifica que las variables de entorno y la carpeta existan."""
    if not S3_BUCKET_NAME:
        print("[ERROR] No se encontro la variable S3_BUCKET_NAME en el archivo .env")
        print("        Agrega la variable con el nombre de tu bucket de S3.")
        sys.exit(1)

    if not CARPETA_LOCAL.exists():
        print(f"[ERROR] No se encontro la carpeta '{CARPETA_LOCAL}'.")
        print("        Crea la carpeta y coloca tus archivos PDF ahi.")
        sys.exit(1)


def obtener_pdfs():
    """Busca todos los archivos PDF en la carpeta s3/."""
    archivos = list(CARPETA_LOCAL.glob("*.pdf"))
    if not archivos:
        print(f"[AVISO] No se encontraron archivos PDF en '{CARPETA_LOCAL}'.")
        print("        Coloca tus archivos PDF de la NSR-10 en esa carpeta e intenta de nuevo.")
        sys.exit(0)
    return archivos


def subir_archivos(archivos):
    """Sube cada archivo PDF al bucket de S3."""
    print(f"Conectando a AWS (region: {AWS_REGION})...")
    s3_client = boto3.client("s3", region_name=AWS_REGION)

    print(f"Bucket destino: {S3_BUCKET_NAME}")
    print(f"Archivos encontrados: {len(archivos)}")
    print("-" * 50)

    exitosos = 0
    fallidos = 0

    for archivo in archivos:
        nombre = archivo.name
        try:
            print(f"  Subiendo: {nombre} ...", end=" ")
            s3_client.upload_file(
                Filename=str(archivo),
                Bucket=S3_BUCKET_NAME,
                Key=nombre,
            )
            print("OK")
            exitosos += 1
        except Exception as e:
            print(f"FALLO")
            print(f"    Detalle: {e}")
            fallidos += 1

    print("-" * 50)
    print(f"Resultado: {exitosos} subidos correctamente, {fallidos} fallidos.")

    if exitosos > 0:
        print()
        print("SIGUIENTE PASO:")
        print("  Ve a la consola de AWS > Bedrock > Knowledge bases > Tu KB > Sync")
        print("  para que los nuevos documentos sean indexados.")


def main():
    print("=" * 50)
    print(" Upload S3 — Subir PDFs de la NSR-10")
    print("=" * 50)
    print()

    validar_configuracion()
    archivos = obtener_pdfs()
    subir_archivos(archivos)


if __name__ == "__main__":
    main()
