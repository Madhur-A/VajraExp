# -*- coding: utf-8 -*-
"""
BSD 3-Clause License

Copyright (c) 2019, Varush Varsha
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

1. Redistributions of source code must retain the above copyright notice, this
   list of conditions and the following disclaimer.

2. Redistributions in binary form must reproduce the above copyright notice,
   this list of conditions and the following disclaimer in the documentation
   and/or other materials provided with the distribution.

3. Neither the name of the copyright holder nor the names of its
   contributors may be used to endorse or promote products derived from
   this software without specific prior written permission.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
"""



from PyQt5.QtCore             import *
from PyQt5.QtGui              import *
from PyQt5.QtWidgets          import *
from PyQt5.QtWebEngineWidgets import *
from vajra    import *

import overlay
import pandas
import sys
import warnings
import shutil
import urllib3
import json
import datetime

import matplotlib.pyplot as plt
plt.style.use("fivethirtyeight")
plt.rcParams.update({"font.family": "MathJax_Fraktur"})
plt.rcParams.update({"font.size": 12})
plt.rcParams.update({"lines.linewidth": 0.55})
warnings.simplefilter(action="ignore", category=FutureWarning)

hx        = urllib3.PoolManager() 
fundsList = []
with open("./.cache/fundsList.txt", "r") as f:
    string = f.read()
    fundsList.append(string)

fundsList = fundsList[0].split('\n')
del fundsList[-1]
fundsList = sorted(list(set(fundsList)))

def getFundsInstruments(fundName):
    filePath = "./cache/"+fundName+".csv"
    w = []
    try:
        df = pandas.DataFrame.from_csv(filePath)
        w  = list(df.index)
        w  = sorted(list(set(w)))
        return w
    except FileNotFoundError: 
        print("DEBUG: Perhaps, the firm has NOT submitted 13F filings and does not appear to be an investment advisor.")
        return w 

    
class InterfaceUI(overlay.Ui_mainWindow):
    def __init__(self):
        self.mainWindow    = QMainWindow()
        self.displayWidget = QWidget()
        self.displayWidget.setMinimumSize(1000, 500)
        self.displayWidget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.webLayout     = QVBoxLayout(self.displayWidget)
        self.viewer        = QWebEngineView()
        self.displayWidget.setWindowTitle("Chart Displayer")
        self.textEditEval  = QTextEdit()
        self.textEditEval.setMinimumSize(700, 300)
        self.setupInterface(self.mainWindow)
        self.interfaceImplement(self.mainWindow)

    def closeAll(self):
        self.mainWindow.close()
        self.displayWidget.close()
        self.textEditEval.close();
        
    def about(self):
        QMessageBox.about(self.mainWindow, "VajraExp (Compromised Version)",
                          "Vajra [Compromised Version]\nViewing Utility for Funds\n \u00A9 Varush Varsha 2019-2020")

    def addFundMenu(self):
        fileAddress = QFileDialog.getOpenFileName(self.mainWindow, self.mainWindow.tr("Open File"),
                                                  ".", self.mainWindow.tr("CSV (*.csv)"))
        destFileAddress = "./.cache/funds/"+fileAddress[0].split("/")[-1]
        fileName        = fileAddress[0].split("/")[-1].replace(".csv", "")
        shutil.copyfile(fileAddress[0], destFileAddress, follow_symlinks=False)
        with open("./.cache/fundsList.txt", "a+") as f:
            f.write(fileName+"\n")        
        QMessageBox.information(self.mainWindow, "{} Saved!".format(fileName), "Written {} to the list!".format(fileName))


    def addInstrumentMenu(self):
        fileAddress = QFileDialog.getOpenFileName(self.mainWindow, self.mainWindow.tr("Open File"),
                                                  ".", self.mainWindow.tr("CSV (*.csv)"))
        destFileAddress = "./.cache/"+fileAddress[0].split("/")[-1]
        fileName        = fileAddress[0].split("/")[-1].replace(".csv", "")
        shutil.copyfile(fileAddress[0], destFileAddress, follow_symlinks=False)
        QMessageBox.information(self.mainWindow, "{}.csv Saved!".format(fileName),
                                "Written {}.csv Execute Test Enabled!".format(fileName))
        
    def setupInterface(self, mainWindow):
        self.setupUi(mainWindow)
        self.actionExitMenu.triggered.connect(self.mainWindow.close)
        self.actionAboutMenu.triggered.connect(self.about)
        self.actionAddFundMenu.triggered.connect(self.addFundMenu)
        self.actionAddInstrument.triggered.connect(self.addInstrumentMenu)
        self.pushButtonClear.clicked.connect(self.clearAll)
        for fund in fundsList:
            self.fundNameComboBox.addItem(fund)
        self.fundNameComboBox.setEditable(True)
        self.instrumentNameComboBox.setEditable(False)

    def onFundsComboboxCurrentTextChanged(self):
        self.instrumentNameComboBox.clear()
        instrumentName = self.fundNameComboBox.currentText()
        filePath = "./.cache/funds/"+instrumentName+".csv"
        self.instrumentNameComboBox.clear()
        try:
            ff = pandas.DataFrame.from_csv(filePath)
            fl = sorted(list(set(sorted(list(ff.index)))))
            self.instrumentNameComboBox.addItems(fl)
        except FileNotFoundError:
            self.instrumentNameComboBox.clear()
            self.instrumentNameComboBox.addItem("N/A")
            self.instrumentNameComboBox.setCurrentText("N/A")
            print("the isntrument {} cannot be found!".format(instrumentName))

    def onInstrumentNameTextChanged(self):
        instrumentName = self.fundNameComboBox.currentText()
        filePath       = "./.cache/funds/"+instrumentName+".csv"
        instrumentName = self.instrumentNameComboBox.currentText()
        try:
            ff             = pandas.DataFrame.from_csv(filePath)
            sectorValue    = ff.at[instrumentName, "sector"]
            self.sectorComboBox.addItem(sectorValue)
            self.sectorComboBox.setCurrentText(sectorValue)
            self.lineEditAveragePrice.setText(str(ff.at[instrumentName, "Avg Price"]))
            self.lineEditRanking.setText(str(ff.at[instrumentName, "Type"]))
            self.lineEditChangeInShares.setText(str(ff.at[instrumentName, "Change in shares"]))
            self.lineEditSharesHeld.setText(str(ff.at[instrumentName, "Shares Held"]))
            self.lineEditMarketValue.setText(str(ff.at[instrumentName, "Market Value"]))
            self.lineEditPrPerOfPortfolio.setText(str(ff.at[instrumentName, r"% of Portfolio"]))
            self.lineEditPercentageChange.setText(str(ff.at[instrumentName, r"% Change"]))
            self.lineEditPerOwnership.setText(str(ff.at[instrumentName, r"% Ownership"]))
            self.lineEditQtrFirstOwned.setText(str(ff.at[instrumentName, "Qtr first owned"]))
            self.lineEditSoureType.setText(str(ff.at[instrumentName, "source_type"]))
            self.lineEditSourceData.setText(str(ff.at[instrumentName, "source_date"]))
            self.lineEditChangeType.setText(str(ff.at[instrumentName, "Change Type"]).title())
        except (FileNotFoundError, TypeError, ValueError):
            self.haltExecution(instrumentName, instrumentName.title() + " Not Found!", False)
            

    def haltExecution(self, tickerSymbol, msgString, okOrCancel=True): # make this as elaborate as you may please
        self.displayWidget.close()
        messageString = msgString.strip()
        popUp = QMessageBox(self.mainWindow)
        popUp.setIcon(QMessageBox.Information)
        popUp.setText(messageString)
        popUp.setMinimumSize(500, 300)
        ticker = ""
        if type(tickerSymbol) == str:
            ticker = tickerSymbol
        else:
            ticker = tickerSymbol[0]
        popUp.setWindowTitle(ticker + ".csv Does NOT exist!")
        if okOrCancel == True:
            popUp.setStandardButtons(QMessageBox.Ok)
        else:
            popUp.setStandardButtons(QMessageBox.Cancel)
        popUp.show()
    
    def clearAll(self):
        self.textEditEval.close()
        self.displayWidget.close()
        self.sectorComboBox.clear()
        self.lineEditAveragePrice.clear()
        self.lineEditRanking.clear()
        self.lineEditChangeInShares.clear()
        self.lineEditSharesHeld.clear()
        self.lineEditMarketValue.clear()
        self.lineEditPrPerOfPortfolio.clear()
        self.lineEditPercentageChange.clear()
        self.lineEditPerOwnership.clear()
        self.lineEditQtrFirstOwned.clear()
        self.lineEditSoureType.clear()
        self.lineEditSourceData.clear()
        self.lineEditChangeType.clear()
        self.displayWidget.close()

    def setNewWindowTitle(self):
        self.displayWidget.setWindowTitle(self.viewer.page().title())

    def onDisplayButtonClicked(self):
        instrument     = self.instrumentNameComboBox.currentText();
        instrumentName = self.fundNameComboBox.currentText()
        filePath = "./.cache/funds/"+instrumentName+".csv"
        dbDict   = pandas.DataFrame.from_csv(filePath)
        tickerSymbol = dbDict.at[instrument, "Symbol"]
        try:
            url        = "http://finance.yahoo.com/chart/{}".format(tickerSymbol)
            print("{}".format(url))
            self.viewer.load(QUrl(url))
            self.webLayout.addWidget(self.viewer)
            self.viewer.page().loadFinished.connect(self.setNewWindowTitle)
            self.displayWidget.show()
        except (FileNotFoundError, TypeError, ValueError):
            self.haltExecution(instrumentName, instrument + " Not Found!")

    def getCurrentPrice(self, tickerSymbol):
        url = "https://query2.finance.yahoo.com/v7/finance/options/{}".format(tickerSymbol)
        rxx = hx.request("GET", url)
        if rxx.status == 200:
            rxs = rxx.data.decode("utf-8")
            jsx = json.loads(rxs)
            try:
                cpx = jsx["optionChain"]["result"][0]["quote"]["regularMarketPrice"]
                return cpx;
            except IndexError:
                self.haltExecution(tickerSymbol, "IndexError: [" + tickerSymbol + "] Can't Be Reached!")
        else:
            self.haltExecution(tickerSymbol, tickerSymbol + " Can't Be Reached! Try Later!")

    def onExecuteButtonClicked(self):
        instrument     = self.instrumentNameComboBox.currentText();
        instrumentName = self.fundNameComboBox.currentText()
        filePath = "./.cache/funds/"+instrumentName+".csv"
        dbDict   = pandas.DataFrame.from_csv(filePath)
        tickerSymbol = dbDict.at[instrument, "Symbol"]
        if self.checkBoxEvaluation.checkState() == 2:
            currentPrice = self.getCurrentPrice(tickerSymbol)
            sharesHeld   = dbDict.at[instrument, "Shares Held"]
            avgPrice     = dbDict.at[instrument, "Avg Price"]
            evaluationPast    = sharesHeld * avgPrice
            evaluationPresent = sharesHeld * currentPrice
            pastYear    = int(dbDict.at[instrument, "Qtr first owned"][-4:])
            currentYear = datetime.datetime.now().year
            totalYears  = currentYear - pastYear
            title       = instrumentName.title()
            inst        = instrument.title()
            
            firstLine = "Past Valuation {} and the present Valuation {} for {} in {} years".format(
                evaluationPast, evaluationPresent, instrument.title(), totalYears)
            plFactor = evaluationPresent - evaluationPast
            plString = ""
            if plFactor > 0:
                plString = "PROFIT: "
            else:
                plString = "LOSS:   "
            percentage = (abs(plFactor) * 100.0)/evaluationPast
            plLine = "{} is ${}(~ ${} Approx.) on the investment of ${} {} %age is {}".format(
                plString, plFactor, getInWords(abs(plFactor)), getInWords(abs(evaluationPast)), plString, percentage)
            lineStart   = "{0:25s}{1}{2:25s}".format("-----------------------", instrument.title(), "-----------------------")
            lineBreak   = "{0:25s}{1}{2:25s}".format("=======================", instrument.title(), "=======================")
            for element in [lineStart, title, inst, firstLine, plLine, lineBreak]:
                self.textEditEval.append(element)
            self.textEditEval.setWindowTitle(instrument.title())
            self.textEditEval.show()
        elif self.checkBoxEvaluation.checkState() == 0:
            ecV = 0
            try:
                ecV = exponentialCompromisedVersion(tickerSymbol)
            except FileNotFoundError:
                self.haltExecution(tickerSymbol, instrument.title() +
                               " Not Found! Download the file first and then try executing the test!", False)
            if type(ecV) == tuple:
                ecv = ecV[0]
                erv = ecV[1]
                messageString = "Exponential measure of stability is " + str(ecv) \
                                + " and the correlation between Tencent[0700.HK] and " + \
                                instrument + " is " + str(erv)
                popUp = QMessageBox(self.mainWindow)
                popUp.setIcon(QtWidgets.QMessageBox.Information)
                popUp.setText(messageString)
                popUp.setWindowTitle(tickerSymbol + "'s Exp Value")
                popUp.setStandardButtons(QtWidgets.QMessageBox.Ok)
                popUp.show()
            else:
                self.haltExecution(tickerSymbol, instrument.title() +
                                   ": Could NOT Generate the Resultant Tuple! Maybe {}.csv Needs to be Downloaded First".format(tickerSymbol),
                                   True)
        else:
            pass

    def onChekced(self):
        if self.checkBoxEvaluation.checkState() == 2:
            self.executeButton.setText("Evaluate")
            self.executeButton.setStyleSheet("background-color: RoyalBlue")
        elif self.checkBoxEvaluation.checkState() == 0:
            self.executeButton.setText("Execute Test")
            self.executeButton.setStyleSheet("background-color: SkyBlue")
        else:
            pass

    def onExitButtonClicked(self):
        self.closeAll()
        
    def interfaceImplement(self, mainWindow):
        self.retranslateUi(mainWindow)
        self.fundNameComboBox.currentTextChanged.connect(self.onFundsComboboxCurrentTextChanged)
        self.instrumentNameComboBox.currentTextChanged.connect(self.onInstrumentNameTextChanged)
        self.displayButton.setStyleSheet("background-color: RoyalBlue")
        self.displayShortCut   = QShortcut(QKeySequence(self.mainWindow.tr("Ctrl+D")), self.mainWindow)
        self.checkBoxEvaluation.stateChanged.connect(self.onChekced)
        self.exitButton.clicked.connect(self.onExitButtonClicked)
        self.displayButton.clicked.connect(self.onDisplayButtonClicked)
        self.executeButton.clicked.connect(self.onExecuteButtonClicked)
    
    def show(self):        
        self.mainWindow.show()

if __name__ == "__main__":
    QCoreApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QCoreApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)
    app = QApplication(sys.argv)
    ui = InterfaceUI()
    ui.show()
    app.exec_()
