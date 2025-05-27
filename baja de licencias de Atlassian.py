import os
import csv
import requests
from datetime import datetime
from requests.auth import HTTPBasicAuth
from dotenv import load_dotenv

# Cargar variables del archivo .env
load_dotenv()

def process_csv_and_delete_users(csv_filepath, api_url, username, api_token,
                                  group_id, fecha_limite_str, dias_inactivos, excepciones,
                                  col_ultimo_acceso, col_es_usuario, account_id_column):
    try:
        # Convertir fecha límite
        fecha_limite_dt = datetime.strptime(fecha_limite_str, "%Y-%m-%d")

        with open(csv_filepath, 'r', newline='', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)

            # Verificar columnas necesarias (col_es_usuario es opcional)
            columnas_requeridas = [account_id_column, "email", "Added to org", col_ultimo_acceso]
            for col in columnas_requeridas:
                if col not in reader.fieldnames:
                    print(f"Error: Falta la columna requerida '{col}' en el CSV.")
                    return

            col_es_usuario_presente = col_es_usuario in reader.fieldnames
            if not col_es_usuario_presente:
                print(f"Advertencia: No se encontró la columna '{col_es_usuario}' en el CSV. Se omitirá la validación de tipo de usuario.")

            for row in reader:
                email = row.get("email", "").strip().lower()

                # Verificar si está exceptuado
                if email in excepciones:
                    continue

                # Verificar si es tipo "User" solo si la columna existe
                if col_es_usuario_presente:
                    tipo_usuario = row.get(col_es_usuario, "").strip().lower()
                    if tipo_usuario != "user":
                        continue

                # Validar fecha de alta
                added_to_org_str = row.get("Added to org", "").strip()
                try:
                    added_to_org = datetime.strptime(added_to_org_str, "%d %b %Y")
                    if added_to_org > fecha_limite_dt:
                        continue
                except ValueError:
                    continue

                # Validar inactividad
                last_seen_str = row.get(col_ultimo_acceso, "").strip()
                never_accessed = last_seen_str.lower() == "never accessed"
                inactivo_por_dias = False

                if not never_accessed:
                    try:
                        last_seen_date = datetime.strptime(last_seen_str, "%d %b %Y")
                        days_since_last_seen = (datetime.now() - last_seen_date).days
                        inactivo_por_dias = days_since_last_seen >= dias_inactivos
                    except ValueError:
                        continue

                if not (never_accessed or inactivo_por_dias):
                    continue

                account_id = row.get(account_id_column)
                if account_id:
                    delete_url = f"{api_url}/group/user"
                    auth = HTTPBasicAuth(username, api_token)
                    query = {
                        'groupId': group_id,
                        'accountId': account_id
                    }

                    print(f"Eliminando usuario '{email}' (ID: {account_id}) del grupo '{group_id}'...")
                    response = requests.delete(delete_url, params=query, auth=auth)

                    print(f"  Código de estado: {response.status_code}")
                    print(f"  Respuesta: {response.text}")
                    print("-" * 40)
                else:
                    print(f"Advertencia: Falta el ID de usuario. Fila: {row}")

    except FileNotFoundError:
        print(f"Error: No se encontró el archivo CSV '{csv_filepath}'.")
    except Exception as e:
        print(f"Error inesperado: {e}")

if __name__ == "__main__":    
    csv_file = './export-users.csv' # Ruta al archivo CSV
    # Cargar variables de entorno
    atlassian_domain = os.getenv("ATLASSIAN_SITE") 
    atlassian_email = os.getenv("ATLASSIAN_EMAIL")
    atlassian_api_token = os.getenv("ATLASSIAN_API_TOKEN")
    fecha_limite = os.getenv("FECHA_LIMITE")
    dias_inactivos = os.getenv("DIAS_INACTIVOS")
    excepciones_str = os.getenv("USUARIOS_EXCEPTUADOS", "")
    group_id = os.getenv("GROUP_ID")
    col_ultimo_acceso = os.getenv("COLUMNA_ULTIMO_ACCESO")
    col_es_usuario = os.getenv("COLUMNA_ES_USUARIO")
    account_id_column = os.getenv("COLUMNA_ACCOUNT_ID")

    # Validar variables obligatorias
    if not all([atlassian_domain, atlassian_email, atlassian_api_token,
                fecha_limite, dias_inactivos, group_id,
                col_ultimo_acceso, col_es_usuario, account_id_column]):
        raise ValueError("Faltan variables requeridas en el archivo .env")

    try:
        dias_inactivos = int(dias_inactivos)
    except ValueError:
        raise ValueError("DIAS_INACTIVOS debe ser un número entero")

    excepciones = [mail.strip().lower() for mail in excepciones_str.split(",") if mail.strip()]

    process_csv_and_delete_users(
        csv_file,
        f"https://{atlassian_domain}/rest/api/3",
        atlassian_email,
        atlassian_api_token,
        group_id,
        fecha_limite,
        dias_inactivos,
        excepciones,
        col_ultimo_acceso,
        col_es_usuario,
        account_id_column
    )
