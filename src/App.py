import os
import sqlite3 as sql3
import sys

from PyQt5 import QtGui
from PyQt5.QtCore import pyqtSignal, Qt, QThread
from PyQt5.QtWidgets import QMainWindow, QApplication, QMessageBox, \
    QDialog, QFileDialog, QWidget

from src.helpers import database
from src.ui import inizelog, avvio, main, realtime
from src.utente import Utente
from src.salvatore import Salvatore


class App(QMainWindow, main.Ui_MainWindow):
    cartella = os.path.join(os.sys.path[0], 'utenti')
    utente = ''

    def __init__(self, parent=None):
        super(App, self).__init__(parent)
        self.setupUi(self)
        model = QtGui.QStandardItemModel()
        self.postList.setModel(model)
        self.selezionante = Selezionatore(self.cartella, self)
        self.selezionante.show()
        self.selezionante.utente_segnale.connect(self.ottieni_dati)
        self.listaTxt.itemActivated.connect(self.popola_e_sceglie_sub)
        self.aggiornaButton.clicked.connect(self.lavora_up)
        self.salvaButton.clicked.connect(self.salvataggio)
        self.salvaDirButton.clicked.connect(self.scegli_dir)

    def ottieni_dati(self, dati_utente):
        self.utente = dati_utente
        print("nell'App con {}". format(self.utente))
        self.popolaTxt()

    def aggiorna_dopo_nuovo_redditore(self, redditore):
        # Aggiornamento non funzioante
        print("ecco: {}".format(redditore))
        if redditore and not self.redditorList.findItems(redditore, Qt.MatchExactly):
            self.redditorList.addItem(redditore)

    def popolaTxt(self):
        for file in os.listdir(self.utente.cartella):
            if file.endswith('txt'):
                self.listaTxt.addItem(file[:-4])

    def popola_e_sceglie_sub(self):
        self.subscelte = set()
        model = QtGui.QStandardItemModel()
        self.subscelteLstView.setModel(model)
        with open (os.path.join(self.utente.cartella, self.listaTxt.currentItem().text() + '.txt'),'r', encoding='utf-8') as f:
            for n, line in enumerate(f):
                item = QtGui.QStandardItem(str(n+1) + '\t' + line)
                model.appendRow(item)
                self.subscelte.add(line[:-1].lower())

    def lavora_up(self):
        """Per migliorare il programma la funzione è stata divisa in due, la prima parte preparatoria è qui
        La seconda parte sfrutta l'idea del Multi-Threading così da non bloccare l'app mentre viene popolata
        la lista dei post upvotati dell'utente"""
        try:
            self.subscelte
        except:
            self.errore('Non hai scelto i subreddit che ti interessano!')
            return
        self.post_da_salvare = []
        self.n_post_da_salvare = self.numPostdaSalvare.value()

        #Serve per creare una lista bianca, così che ad ogni tentativo di riaggiornare la lista, qyesta si resetta
        blank = QtGui.QStandardItemModel()
        self.postList.setModel(blank)

        #in questo modo creo una barra pulsante, anzichè una che va da 0 a 100
        self.progressBar.setRange(0,0)

        self.lavoratore = LavoraThread(self)
        self.lavoratore.start()
        self.lavoratore.finito.connect(self.aggiorna_barra)

    def mostra_ups(self, n, sub, up, is_to_be_saved):
        n_str = str(n + 1) #' ' * (3 - len(str(n + 1))) + str(n + 1)
        sub_str = str(sub)
        titolo_str = str(up.title.encode(errors='replace'))
        num = QtGui.QStandardItem(n_str)
        primo = QtGui.QStandardItem(sub_str)
        secondo = QtGui.QStandardItem(titolo_str)
        if is_to_be_saved:
            self.evidenzia_post(num, primo, secondo)
        self.postList.model().appendRow([num, primo, secondo])
        self.postList.resizeColumnToContents(0)
        self.postList.resizeColumnToContents(1)
        #self.aggiorna_barra(n+1)

    def aggiorna_barra(self):
        #Blocca la pulsazione della barra
        self.progressBar.setRange(0,1)

    def evidenzia_post(self, *pezzi_post):
        font = QtGui.QFont('', -1, QtGui.QFont.Bold, True)
        for pezzo in pezzi_post:
            pezzo.setFont(font)

    def salvataggio(self, perc=""):
        self.mostro = Mostratore()
        if not perc:
            self.salvatore = Salvatore(self.utente, self.post_da_salvare, self.listaTxt.currentItem().text(),
                                       self.mostro, app=self)
        else:
            self.salvatore = Salvatore(self.utente, self.post_da_salvare, self.listaTxt.currentItem().text(),
                                       self.mostro, perc, app=self)

    def scegli_dir(self):
        perc = QFileDialog.getExistingDirectory(self, "Pick a folder")
        self.salvataggio(perc)
        #self.salvatore = Salvatore(self.utente, self.post_da_salvare, self.listaTxt.currentItem().text(), self, path)

    def errore(self, msg_errore):
        err = QMessageBox()
        err.setIcon(QMessageBox.Information)
        err.setWindowTitle("Errore")
        err.setText(msg_errore)
        err.exec_()


class Selezionatore(QMainWindow, avvio.Ui_MainWindow):
    # TODO: questa classe deve fare il login di tutti gli utenti
    utente_segnale = pyqtSignal(object)

    def __init__(self, cartella, main_app, parent=None):
        super(Selezionatore, self).__init__(parent)
        self.setupUi(self)
        self.cartella = cartella
        self.main_app = main_app
        self.popolaUserLst()
        self.aggiungi_redditor = Aggiungitore()
        self.addRedditorbtn.clicked.connect(self.show_add_redditor)
        self.redditorList.itemActivated.connect(self.login_rsu)

    def popolaUserLst(self):
        if not os.path.exists(self.cartella):
            os.makedirs(self.cartella, exist_ok=True)
        for dir in os.listdir(self.cartella):
            self.redditorList.addItem(dir)

    def show_add_redditor(self):
        self.aggiungi_redditor.show()
        self.aggiungi_redditor.utente_segnale.connect(self.ottieni_utente)
        self.close()

    def ottieni_utente(self, segnalato):
        self.utente = segnalato
        print('Ecco il segnale dell\'aggiungitore')
        print(self.utente)
        self.emetti_utente()

    def login_rsu(self):
        self.utente = Utente(username=self.redditorList.currentItem().text())
        self.utente.attiva_utente()
        self.emetti_utente()

    def emetti_utente(self):
        self.utente_segnale.emit(self.utente)
        self.main_app.show()
        self.close()


class Aggiungitore(QDialog, inizelog.Ui_Dialog):
    cartella = ''
    utente_segnale = pyqtSignal(object)

    def __init__(self, parent=None):
        super(Aggiungitore, self).__init__(parent)
        self.setupUi(self)
        self.logButton.pressed.connect(self.aggiungi_e_logga_utente)

    def aggiungi_e_logga_utente(self):
        # Quando crei l'oggetto Reddit non puoi modificarlo in altra maniera
        # Se questa funzione fallisce il programma si chiude
        self.ut_obj = Utente(username=self.userEdit.text(), password=self.passEdit.text())
        print(self.ut_obj.cartella)
        print(os.path.exists(self.ut_obj.cartella))
        self.ut_obj.attiva_utente()
        self.utente_segnale.emit(self.ut_obj)
        self.close()

    def collega_db(self):
        print('collego db')
        db_file = os.path.join(self.cartella, self.diz_utente["username"] + '.db')
        print(db_file)
        # Connettiamo il database e verifichiamo che ci siano le tabelle
        db = sql3.connect(db_file)
        database(db)
        self.diz_utente['cursore_db'] = db.cursor()


class LavoraThread(QThread):
    finito = pyqtSignal()
    def __init__(self, app):
        QThread.__init__(self)
        self.app = app
        print('STO LAVORANDO!1')

    def lavora_up(self):
        """Prende i post upvotati, seleziona quelli che andranno salvati,
        chiama la funzione che popola la lista dei post
        ed evidenzia quelli che verranno salvati"""
        for n, up in enumerate(self.app.utente.redditor.upvoted(limit=self.app.n_post_da_salvare)):
            is_to_be_saved = False
            sub = str(up.subreddit).lower()
            if sub in self.app.subscelte:
                self.app.post_da_salvare.append(up)
                is_to_be_saved = True
                self.app.mostra_ups(n, sub, up, is_to_be_saved)
            else:
                self.app.mostra_ups(n, sub, up, is_to_be_saved)
            #self.app.aggiorna_barra(n+1)
        print('invio l\'emitto')
        self.finito.emit()

    def run(self):
        # print('Pre-RUNNANDO')
        self.lavora_up()


class Mostratore(QWidget, realtime.Ui_real_time):
    def __init__(self, parent=None):
        super(Mostratore, self).__init__(parent)
        self.setupUi(self)





if __name__ == '__main__':
    app = QApplication(sys.argv)
    form = App()
    app.exec_()