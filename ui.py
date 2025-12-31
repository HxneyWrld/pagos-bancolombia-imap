import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidget, QTableWidgetItem
from PyQt6.QtCore import QTimer, QThread, pyqtSignal
from backend import revisar_correos


class WorkerRevisarCorreos(QThread):
    pagos_actualizados = pyqtSignal(list)  # señal para enviar la lista de pagos

    def run(self):
        pagos = revisar_correos()
        self.pagos_actualizados.emit(pagos)


class VentanaPrincipal(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Pagos Bancolombia")
        self.setGeometry(200, 200, 800, 400)

        self.tabla = QTableWidget()
        self.tabla.setColumnCount(5)
        self.tabla.setHorizontalHeaderLabels(
            ["Comercio", "Pagador", "Monto", "Fecha", "Hora"]
        )
        self.setCentralWidget(self.tabla)

        self.uids_mostrados = set() # guardamos los UID ya agregados
        self.primera_carga = True

        self.timer = QTimer()
        self.timer.timeout.connect(self.actualizar_pagos)
        self.timer.start(60_000)

        # primera carga
        self.actualizar_pagos()

    def actualizar_pagos(self):
        self.timer.stop()
        self.worker = WorkerRevisarCorreos()
        self.worker.finished.connect(self.timer.start)
        self.worker.pagos_actualizados.connect(self.mostrar_pagos)
        self.worker.start()

    def mostrar_pagos(self, pagos):
        if self.primera_carga:
            # Solo sincroniza, no muestra nada
            for pago in pagos:
                self.uids_mostrados.add(pago["uid"])
            self.primera_carga = False
            return

        for pago in pagos:
            if pago["uid"] in self.uids_mostrados:
                continue

            fila = self.tabla.rowCount()
            self.tabla.insertRow(fila)
            self.tabla.setItem(fila, 0, QTableWidgetItem(pago["comercio"]))
            self.tabla.setItem(fila, 1, QTableWidgetItem(pago["pagador"]))
            self.tabla.setItem(fila, 2, QTableWidgetItem(pago["monto"]))
            self.tabla.setItem(fila, 3, QTableWidgetItem(pago["fecha"]))
            self.tabla.setItem(fila, 4, QTableWidgetItem(pago["hora"]))

            self.uids_mostrados.add(pago["uid"])

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