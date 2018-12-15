from PyQt5 import QtWidgets
from PyQt5.QtCore import pyqtSignal
import os, sys
from src.ui import iniziale
from src.ui import inizelog


class LoginWindow(QtWidgets.QMainWindow, inizelog.Ui_Dialog):
    cartella = os.path.join(os.sys.path[0], 'utenti')
    utente = pyqtSignal(str)
    def __init__(self):
        super(LoginWindow, self).__init__()
        self.setupUi(self)
        self.popola()

        self.listWidget.itemActivated.connect(self.scegli_utente)


    def popola(self):
        for dir in os.listdir(self.cartella):
            self.listWidget.addItem(dir)

    def scegli_utente(self):
        self.utente.emit(self.listWidget.currentItem().text())
        print(self.utente)


class MainWindow(QtWidgets.QMainWindow, iniziale.Ui_MainWindow):
    def __init__(self, parent=None):
        super(MainWindow, self).__init__(parent)
        self.setupUi(self)

        self.login = LoginWindow()
        self.login.utente.connect(self.mostra_utente)
        self.pushButton2.clicked.connect(self.get_login)
        self.login.utente

    def get_login(self):
        self.login.show()

    def mostra_utente(self, ut):
        self.lineEdit.setText(ut)

    def browse_folder(self):
        self.listWidget.clear()
        directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Pick a folder")
        if directory:
            for file_name in os.listdir(directory):
                self.listWidget.addItem(file_name)

    #COME MOSTRARE UN MESSAGGIO DI ERRORE
    def add_user_to_list(self, utente):
        # Questa va modificata in moodo da riceve gli utenti "corretti"
        if os.path.join(self.cartella, utente):
            print('c è già')
            err = QMessageBox()
            err.setIcon(QMessageBox.Information)
            err.setInformativeText("This is additional information")
            err.setWindowTitle("MessageBox demo")
            err.setDetailedText("The details are as follows:")
            err.setText("utente già in lista-> Logging...")
            err.exec_()

if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)

    form = MainWindow()
    form.show()
    app.exec_()