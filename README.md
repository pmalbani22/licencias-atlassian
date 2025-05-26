# 🔄 Script de Eliminación de Usuarios Inactivos en Atlassian

Este script en Python permite procesar un archivo CSV exportado desde Jira para eliminar automáticamente usuarios inactivos de un grupo específico, cumpliendo con distintos criterios configurables desde un archivo `.env`.

---

## 📦 Requisitos

- Python 3.7+
- Librerías:
  - `requests`
  - `python-dotenv`

Instalación de dependencias:

```bash
pip install requests python-dotenv
```

---

## ⚙️ Configuración del archivo `.env`

Crear un archivo `.env` en el mismo directorio que el script, con el siguiente contenido:

```env
ATLASSIAN_SITE=tu-sitio.atlassian.net 
ATLASSIAN_EMAIL=mail-usuario-admin
ATLASSIAN_API_TOKEN=token-usuario-admin
COLUMNA_ES_USUARIO=columna donde figura el tipo de usuario
FECHA_LIMITE=2024-12-31 
DIAS_INACTIVOS=45 
GROUP_ID= id del grupo del que hay que eliminar el usuario
COLUMNA_ULTIMO_ACCESO= columna donde figura la fecha de último acceso al producto 
USUARIOS_EXCEPTUADOS=admin@mail.com,soporte@mail.com,otro@ejemplo.com 
```

---

## Función principal: process_csv_and_delete_users

Entradas:
- csv_filepath: ruta del archivo CSV

- api_url: URL base de la API de Jira

- username, api_token: credenciales de API

- group_id: grupo del que se eliminarán usuarios

- fecha_limite_str: fecha máxima de alta permitida

- dias_inactivos: umbral de inactividad en días

- excepciones: lista de correos a excluir

- col_ultimo_acceso: nombre de la columna donde figura la última conexión

- col_es_usuario: nombre de la columna que dice si es tipo "User"

- account_id_column: nombre de la columna con el ID del usuario

---

## 🧾 Formato esperado del archivo CSV

El archivo debe tener las siguientes columnas:

- `"email"`: correo electrónico del usuario.
- `"Added to org"`: fecha de creación del usuario (formato `20 May 2025`).
- `"User Type"`: debe tener el valor `User`.
- `"columna donde figura fecha de logueo"`: fecha del último acceso o el valor `Never accessed`.
- `"User id"`: identificador único del usuario.

> El nombre real de algunas columnas puede variar y debe configurarse desde el `.env`.

---

## 🚦 Criterios aplicados por el script

1. **Exclusión por email:** si el email del usuario está en la lista `USUARIOS_EXCEPTUADOS`, será ignorado.
2. **Tipo de usuario:** solo se procesan usuarios cuyo tipo es `User`.
3. **Fecha de creación:** se procesan únicamente usuarios creados en o antes de la fecha `FECHA_LIMITE`.
4. **Inactividad:**
   - Si la fecha del último acceso es anterior a `DIAS_INACTIVOS`.
   - O si el campo indica `Never accessed`.

Solo si se cumplen todas estas condiciones, el usuario será eliminado del grupo definido por `GROUP_ID`.

---

## ▶️ Cómo ejecutar el script

```bash
python nombre_del_script.py
```

Este comando:
- Procesa el CSV definido en el script (variable `csv_file`).
- Aplica las validaciones.
- Elimina por API los usuarios que cumplan con los criterios.

---

## 📤 Ejemplo de salida

```text
Eliminando usuario 'usuario@example.com' (ID: 5a2b3c4d5e6f) del grupo 'nombre-del-grupo'...
  Código de estado: 204
  Respuesta:
----------------------------------------
```

---

## 📌 Notas adicionales

- Asegurate de tener el archivo `.env` correctamente configurado y ubicado.
- Los errores comunes como falta de columnas o formato de fechas inválidas se manejan con mensajes claros en consola.
