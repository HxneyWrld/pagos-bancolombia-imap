import sys
import json
import os
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QTableWidget, QTableWidgetItem,
    QWidget, QVBoxLayout, QLabel, QHeaderView
)
from PyQt6.QtCore import QTimer, QThread, pyqtSignal, Qt
from backend import revisar_correos


# ===================== ARCHIVO DE PERSISTENCIA =====================
PAGOS_FILE = "pagos_guardados.json"


def cargar_pagos_guardados():
    if not os.path.exists(PAGOS_FILE):
        return []

    try:
        with open(PAGOS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []


def guardar_pagos(pagos):
    with open(PAGOS_FILE, "w", encoding="utf-8") as f:
        json.dump(pagos, f, indent=2, ensure_ascii=False)


# ===================== WORKER =====================
class WorkerRevisarCorreos(QThread):
    pagos_actualizados = pyqtSignal(list)

    def run(self):
        pagos = revisar_correos()
        self.pagos_actualizados.emit(pagos)


# ===================== VENTANA PRINCIPAL =====================
class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()
        self.primera_revision = True

        self.setWindowTitle("Pagos Bancolombia")
        self.setMinimumSize(1000, 500)

        # ---------- CONTENEDOR ----------
        contenedor = QWidget()
        layout = QVBoxLayout(contenedor)
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # ---------- HEADER ----------
        self.label_titulo = QLabel("🏥 DROGUERÍA XD")
        self.label_titulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_titulo.setStyleSheet("""
            QLabel {
                font-size: 26px;
                font-weight: bold;
                color: white;
                padding: 15px;
                background-color: #2e7d32;
                border-radius: 12px;
            }
        """)

        self.label_subtitulo = QLabel("Pagos recibidos – Bancolombia QR")
        self.label_subtitulo.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.label_subtitulo.setStyleSheet("""
            QLabel {
                font-size: 14px;
                color: #e8f5e9;
                background-color: #2e7d32;
                padding-bottom: 10px;
                border-bottom-left-radius: 12px;
                border-bottom-right-radius: 12px;
            }
        """)

        # ---------- TABLA ----------
        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Comercio", "Pagador", "Monto", "Fecha", "Hora"]
        )

        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setAlternatingRowColors(True)
        self.tabla.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)

        header = self.tabla.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.tabla.setStyleSheet("""
            QTableWidget {
                background-color: white;
                border-radius: 10px;
                font-size: 14px;
                gridline-color: #e0e0e0;
                color: #212121;
            }

            QTableWidget::item {
                padding: 8px;
                color: #212121;
            }

            QTableWidget::item:alternate {
                background-color: #f5f7fa;
            }

            QHeaderView::section {
                background-color: #1565c0;
                color: white;
                font-weight: bold;
                padding: 8px;
                border: none;
            }

            QTableWidget::item:selected {
                background-color: #c8e6c9;
                color: #000000;
            }
        """)

        layout.addWidget(self.label_titulo)
        layout.addWidget(self.label_subtitulo)
        layout.addWidget(self.tabla)
        self.setCentralWidget(contenedor)

        # ---------- LOGICA ----------
        self.uids_mostrados = set()

        # 🔹 Cargar pagos guardados al iniciar
        self.pagos_guardados = cargar_pagos_guardados()
        for pago in self.pagos_guardados:
            self._agregar_pago_a_tabla(pago)
            self.uids_mostrados.add(pago["uid"])

        # ---------- TIMER ----------
        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_pagos)
        self.timer.start(60_000)

        self.actualizar_pagos()

    # ===================== FUNCIONES =====================
    def _agregar_pago_a_tabla(self, pago):
        fila = self.tabla.rowCount()
        self.tabla.insertRow(fila)

        self.tabla.setItem(fila, 0, QTableWidgetItem(pago["comercio"]))
        self.tabla.setItem(fila, 1, QTableWidgetItem(pago["pagador"]))
        self.tabla.setItem(fila, 2, QTableWidgetItem(pago["monto"]))
        self.tabla.setItem(fila, 3, QTableWidgetItem(pago["fecha"]))
        self.tabla.setItem(fila, 4, QTableWidgetItem(pago["hora"]))

        self.tabla.setRowHeight(fila, 40)

    def actualizar_pagos(self):
        self.timer.stop()
        self.worker = WorkerRevisarCorreos()
        self.worker.finished.connect(lambda: self.timer.start(60_000))
        self.worker.pagos_actualizados.connect(self.mostrar_pagos)
        self.worker.start()

    def mostrar_pagos(self, pagos):
        if self.primera_revision:
            # SOLO sincroniza UIDs, NO guarda ni muestra
            for pago in pagos:
                self.uids_mostrados.add(pago["uid"])
            self.primera_revision = False
            return

        for pago in pagos:
            if pago["uid"] in self.uids_mostrados:
                continue

            self._agregar_pago_a_tabla(pago)

            self.uids_mostrados.add(pago["uid"])
            self.pagos_guardados.append(pago)
            guardar_pagos(self.pagos_guardados)


# ===================== MAIN =====================
from config import crear_o_validar_env

if not crear_o_validar_env():
    print("Configura tu .env antes de continuar.")
    exit()


def main():
    app = QApplication(sys.argv)
    ventana = VentanaPrincipal()
    ventana.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()