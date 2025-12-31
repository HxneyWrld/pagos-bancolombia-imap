from imap_tools import MailBox
from dotenv import load_dotenv
import re
import os

load_dotenv()

MAIL_USERNAME = os.getenv("MAIL_USERNAME")
MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

STATE_FILE = "last_uid.txt"


def get_last_uid():
    if not os.path.exists(STATE_FILE):
        return 0
    with open(STATE_FILE, "r") as f:
        return int(f.read().strip())


def save_last_uid(uid):
    with open(STATE_FILE, "w") as f:
        f.write(str(uid))


def revisar_correos():
    nuevos_pagos = []

    with MailBox("imap.gmail.com").login(MAIL_USERNAME, MAIL_PASSWORD, "INBOX") as mb:
        # Inicializar last_uid.txt si no existe, usando el UID más reciente de la bandeja
        if not os.path.exists(STATE_FILE):
            ult_msg = next(mb.fetch("(UID *)", reverse=True))
            save_last_uid(int(ult_msg.uid))
            print(f"Archivo last_uid.txt creado con UID inicial {ult_msg.uid}")

        last_uid = get_last_uid()
        max_uid_visto = last_uid

        # Solo revisar correos con UID mayor al último guardado
        for msg in mb.fetch(f"(UID {last_uid + 1}:*)"):
            uid = int(msg.uid)
            max_uid_visto = max(max_uid_visto, uid)

            texto = msg.text or msg.html or ""

            print(f"\nUID {uid} -> TEXTO: {texto[:500]}")
            # print(f"UID {uid} | Texto inicio: {texto[:100]}")

            # Patrones de Bancolombia
            PATRON_COMERCIO = re.compile(
                r"Bancolombia:\s*(.+?),\s*recibiste un pago de\s*(.+?)\s*por\s*\$([\d\.,]+).*?el\s*(\d{2}/\d{2}/\d{4})\s*a las\s*(\d{2}:\d{2})",
                re.IGNORECASE | re.DOTALL
            )

            PATRON_PERSONAL = re.compile(
                r"Recibiste\s*\$([\d\.,]+)\s*por\s*QR\s*de\s*(.+?)\s*en tu cuenta.*?el\s*(\d{4}/\d{2}/\d{2})\s*a las\s*(\d{2}:\d{2})",
                re.IGNORECASE | re.DOTALL
            )

            match = PATRON_COMERCIO.search(texto)
            if match:
                pago = {
                    "tipo": "comercio",
                    "comercio": match.group(1).strip(),
                    "pagador": match.group(2).strip(),
                    "monto": match.group(3),
                    "fecha": match.group(4),
                    "hora": match.group(5),
                    "uid": uid
                }
                nuevos_pagos.append(pago)
                continue

            match = PATRON_PERSONAL.search(texto)
            if match:
                pago = {
                    "tipo": "personal",
                    "comercio": "Cuenta Personal (QR)",
                    "pagador": match.group(2).strip(),
                    "monto": match.group(1),
                    "fecha": match.group(3),
                    "hora": match.group(4),
                    "uid": uid
                }
                nuevos_pagos.append(pago)

        # Guardamos el último UID visto, aunque no haya match
        save_last_uid(max_uid_visto)

    return nuevos_pagos