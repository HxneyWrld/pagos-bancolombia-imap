import os
from dotenv import load_dotenv

ENV_FILE = ".env"
REQUIRED_VARS = ["MAIL_USERNAME", "MAIL_PASSWORD"]

def crear_o_validar_env():
    if not os.path.exists(ENV_FILE):
        with open(ENV_FILE, "w") as f:
            for var in REQUIRED_VARS:
                f.write(f"{var}=\n")
        print(f"{ENV_FILE} creado. Por favor completa las variables necesarias.")
        return False


    load_dotenv()
    faltantes = [var for var in REQUIRED_VARS if not os.getenv(var)]
    if faltantes:
        print(f"Variables faltantes en {ENV_FILE}: {', '.join(faltantes)}")
        return False

    return True