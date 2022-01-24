import snap7
import time, datetime
from PyQt5 import QtWidgets, QtCore
import sys, os
import pandas as pd
import struct, math
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
import matplotlib.pyplot as plt
import numpy as np

class MplGraf(FigureCanvasQTAgg):
    def __init__(self):   
        self.fig = plt.figure()
        self.axes = self.fig.add_subplot(111)
        super(MplGraf, self).__init__(self.fig)

class MainWin(QtWidgets.QMainWindow):
    def __init__(self, *args, **kwargs):
        super(MainWin, self).__init__(*args, **kwargs)

        self.history = False
        self.lim = 21
        self.dataReal = datetime.datetime.now().strftime("%d.%m.%Y_%H:%M")

        self.setWindowTitle("Lakovna")
        self.MainW = QtWidgets.QWidget()
        self.setMinimumWidth(1200)
        self.graf = MplGraf()
        self.mainW = QtWidgets.QWidget()
        self.mainL = QtWidgets.QHBoxLayout()
        self.mainW.setLayout(self.mainL)
        self.setCentralWidget(self.mainW)

        self.mainL.addWidget(self.graf)
        # vertikalni box pro vyber zobrazeni grafu
        self.ovladaniW = QtWidgets.QWidget()
        self.ovladaniL = QtWidgets.QVBoxLayout()
        self.ovladaniW.setLayout(self.ovladaniL)
        self.ovladaniW.setMaximumWidth(200)
        self.mainL.addWidget(self.ovladaniW)
        # box s vyberem rozsahu zobrazeni aktualnich dat
        self.actualW = QtWidgets.QGroupBox("aktualni data")
        self.actualL = QtWidgets.QVBoxLayout()
        self.actualW.setLayout(self.actualL)
        self.actualW.setMaximumHeight(170)
        self.ovladaniL.addWidget(self.actualW)
        self.h1A = QtWidgets.QRadioButton("3 hodiny")
        self.h10A = QtWidgets.QRadioButton("10 hodin")
        self.h24A = QtWidgets.QRadioButton("24 hodin")
        self.actualL.addWidget(self.h1A)
        self.actualL.addWidget(self.h10A)
        self.actualL.addWidget(self.h24A)
        # box s vyberem rozsahu zobrazeni historickych dat
        self.historyW = QtWidgets.QGroupBox("historie")
        self.historyL = QtWidgets.QVBoxLayout()
        self.historyW.setLayout(self.historyL)
        self.ovladaniL.addWidget(self.historyW)
        self.Datum = QtWidgets.QDateEdit()
        self.Datum.setStyleSheet("Height: 30px; font-size: 20px;")
        self.Datum.setCalendarPopup(True)
        self.Datum.setMinimumDate(QtCore.QDate(2020,6,9))
        self.Datum.setMaximumDate(datetime.datetime.now())
        self.Datum.setDisplayFormat("dd.MM.yyyy")
        self.historyL.addWidget(self.Datum)
        self.Cas = QtWidgets.QTimeEdit()
        self.Cas.setDisplayFormat("HH:MM")
        self.Cas.setStyleSheet("Height: 30px; font-size: 20px;")
        self.historyL.addWidget(self.Cas)
        self.h1H = QtWidgets.QRadioButton("3 hodiny")
        self.h10H = QtWidgets.QRadioButton("10 hodin")
        self.h24H = QtWidgets.QRadioButton("24 hodin")
        self.historyL.addWidget(self.h1H)
        self.historyL.addWidget(self.h10H)
        self.historyL.addWidget(self.h24H)
        # propojeni tlacitek na funkce
        self.h1A.clicked.connect(self.clickA)
        self.h10A.clicked.connect(self.clickA)
        self.h24A.clicked.connect(self.clickA)
        self.h1H.clicked.connect(self.clickH)
        self.h10H.clicked.connect(self.clickH)
        self.h24H.clicked.connect(self.clickH)
        
        self.set_graf()    
        self.get_data()

        self.show()
    # vyber aktualnich dat
    def clickA(self):
        self.history = False
        if self.h1A.isChecked():
            self.lim = 21
        elif self.h10A.isChecked():
            self.lim = 60
        elif self.h24A.isChecked():
            self.lim = 144
        self.set_graf() 

    # vyber historickych dat
    def clickH(self):
        self.history = True
        if self.h1H.isChecked():
            self.lim = 21
        elif self.h10H.isChecked():
            self.lim = 60
        elif self.h24H.isChecked():
            self.lim = 144
        self.set_graf() 
    

    # pripojeni k PLC, stazeni dat a ulozeni do csv
    def get_data(self):
        data = []
        zapis = ""
        a = ""
        self.dataReal = datetime.datetime.now().strftime("%d.%m.%Y_%H:%M")
        self.Datum.setMaximumDate(datetime.datetime.now())
        try:
            with open("C:\\Users\\line\\Desktop\\teploty\\teploty.csv", "r", encoding="utf-8") as r:
                for i, value in enumerate(r.readlines()):
                    if i > 0:
                        data.append(value[6:].strip("\n"))
            try:
                with open("C:\\Users\\line\\Desktop\\teploty\\teplotyLakovna.csv","a", encoding="utf-8") as a:
                    zapis = self.dataReal
                    for i in data:
                        zapis = zapis + "," +  i
                    a.write(zapis+"\n")
            except:
                with open("log.txt", "a", encoding="utf-8") as a:
                    a.write(self.dataReal+" ---- nepovedlo se zapsat data do souboru -teplotyLakovna.csv- \n") 
        except:
            with open("log.txt", "a", encoding="utf-8") as a:
                a.write(self.dataReal+" ---- problem se ctenim dat ze souboru -teploty.csv- \n") 
        if not self.history:
            self.set_graf()
        self.store_data()
        # vytvoreni timeru pro volani funkce cteni dat z PLC kazdych 10 min
        self.t = QtCore.QTimer()
        self.t.setSingleShot(True)
        self.t.setInterval(600000)
        self.t.timeout.connect(self.get_data)
        self.t.start()

    # prepis dat do historickeho csv kazdy druhy den v mesici
    def store_data(self):
        zapis = []
        if datetime.datetime.now().day == 2 and datetime.datetime.now().hour == 1 and datetime.datetime.now().minute < 11:
            with open("C:\\Users\\line\\Desktop\\teploty\\teplotyLakovna.csv", "r", encoding="utf-8") as r:
                for i in r.readlines():
                    zapis.append(i)
            x = datetime.datetime.now() - datetime.timedelta(30)
            nazev = x.strftime("C:\\Users\\line\\Desktop\\teploty\\%y.%m_teploty.csv")
            with open(nazev, "w", encoding="utf-8") as w:
                for i in zapis:
                    w.write(i)
            # smazani dat z csv
            with open("C:\\Users\\line\\Desktop\\teploty\\teplotyLakovna.csv", "w+") as W:
                pass
            # vytvoreni noveho aktualniho csv souboru s 1 dennim presahem do predchoziho mesice
            with open("C:\\Users\\line\\Desktop\\teploty\\teplotyLakovna.csv", "w", encoding="utf-8") as w:
                w.write(zapis[0])
                for i, value in enumerate(zapis):
                    if i > len(zapis)-288:
                        w.write(value)
                

    # update grafu novyma hodnotama
    def set_graf(self):

        self.graf.axes.clear()
        self.graf.axes.grid()
        textvar = self.graf.fig.text
        print(self.graf.fig.texts)
        if len(self.graf.fig.texts) > 0:
            del(self.graf.fig.texts[:])
       
        
        # nacteni dat z csv souboru do pandas dataFrame
        y = []
        xg1 = []
        xg2 = []
        xg3 = []
        xg4 = []
        xg5 = []
        xg6 = []
        xg7 = []
        xg8 = []
        # cteni rozsahu aktualnich dat 
        if not self.history:
            data = pd.read_csv("C:\\Users\\line\\Desktop\\teploty\\teplotyLakovna.csv")
            for i,value in enumerate(data["datum"]):                         
                if i > (len(data["datum"]) - self.lim):
                    y.append(value[:2]+value[10:])           
                    xg1.append(data["PG1"][i])
                    xg2.append(data["PG2"][i])
                    xg3.append(data["PG3"][i])
                    xg4.append(data["LG1"][i])
                    xg5.append(data["LG1"][i])
                    xg6.append(data["LG1"][i])
                    xg7.append(data["TT"][i])
                    xg8.append(data["TP"][i])

            # cteni rozsahu historickych dat
        elif self.history:
            if (self.Datum.text()[3:5] == datetime.datetime.now().strftime("%m")) or (self.Datum.text()[3:5] == (datetime.datetime.now()-datetime.timedelta(1)).strftime("%m")):
                zdroj = "C:\\Users\\line\\Desktop\\teploty\\teplotyLakovna.csv"
            else:
                zdroj = "C:\\Users\\line\\Desktop\\teploty\\"+self.Datum.text()[8:12]+"."+self.Datum.text()[3:5]+"_teploty.csv"
            data = pd.read_csv(zdroj)
            for i,value in enumerate(data["datum"]):
                if value[0:13] == (self.Datum.text()+"_"+self.Cas.text())[0:13]:
                    if i + self.lim < len(data["datum"]):
                        s = i + self.lim
                    else:
                        s = len(data["datum"])
                    for j in range(i,s):
                        y.append(data["datum"][j][:2]+data["datum"][j][10:]) 
                        xg1.append(data["PG1"][j])
                        xg2.append(data["PG2"][j])
                        xg3.append(data["PG3"][j])
                        xg4.append(data["LG1"][j])
                        xg5.append(data["LG2"][j])
                        xg6.append(data["LG3"][j])
                        xg7.append(data["TT"][j])
                        xg8.append(data["TP"][j])                       
                    break
                    
        # tvorba jednotliv7ch grafu
        self.graf.axes.plot(y, xg1, label = "prasek G1")
        self.graf.axes.plot(y, xg2, label = "prasek G2")
        self.graf.axes.plot(y, xg3, label = "prasek G3")
        self.graf.axes.plot(y, xg4, label = "lak G1")
        self.graf.axes.plot(y, xg5, label = "lak G2")
        self.graf.axes.plot(y, xg6, label = "lak G3")
        self.graf.axes.plot(y, xg7, label = "TT")
        self.graf.axes.plot(y, xg8, label = "TP")
        self.graf.axes.xaxis.set_major_locator(plt.MaxNLocator(6))
        textvar = self.graf.fig.text(0.5, 0.02, "Den a hodina pro mesic: "+data["datum"][136][3:10], ha='center', va='center')
        #self.graf.fig.text(0.5, 0.02, "Den a hodina pro mesic: "+data["datum"][136][3:10], ha='center', va='center')
        self.graf.fig.text(0.05, 0.4, "Teplota [°C]", rotation=90)
        self.graf.axes.minorticks_on()
        self.graf.axes.grid(which="major", linestyle="-")
        self.graf.axes.grid(which="minor", linestyle=":")  
        self.graf.axes.legend()
        self.graf.draw()

class App(QtWidgets.QApplication):
    def build(self):

        self.mainWin = MainWin()

        sys.exit(self.exec())

app = App(sys.argv)
app.build()

