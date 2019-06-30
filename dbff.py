#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 15.06.2019

@author: marazmista
"""

from src.Dialog_configuration import *
from src.Dialog_import import *
from src.DatabaseManager import *
import locale
import os.path
from src.PlotManager import *
from src.create_database import *
import time


class MainFrame(wx.Frame):
    def __init__(self, title, size):
        wx.Frame.__init__(self, None, -1, title, size=size)

        self.createMenu()

        panel = wx.Panel(self, -1)
        # panel2 = wx.Panel(self, -1)
        box_main = wx.BoxSizer(wx.HORIZONTAL)
        box_main2 = wx.BoxSizer(wx.VERTICAL)

        # button = wx.Button(panel, -1, "Close", pos = (130,50), size = (100, 50))

        self.mainList = wx.ListCtrl(panel, wx.ID_ANY, pos = (10, 10), size=(200, 350), style =wx.LC_REPORT | wx.BORDER_SUNKEN)
        self.mainList.InsertColumn(0, "Date")
        self.mainList.InsertColumn(1, "Resting HR")
        self.mainList.InsertColumn(2, "Sleep HR (avg, min, max)")
        self.mainList.InsertColumn(3, "Sleep")
        self.mainList.InsertColumn(4, "Efficiency")

        self.mainList.SetColumnWidth(0,150)
        self.mainList.SetColumnWidth(3,170)


        box_main.Add(self.mainList, 1, wx.EXPAND | wx.ALL, 10)
        box_main.Add(box_main2, 0, wx.EXPAND | wx.ALL, 10)
        panel.SetSizer(box_main)

        self.Bind(wx.EVT_LIST_ITEM_SELECTED, self.ItemClick, self.mainList)
        self.Bind(wx.EVT_LIST_ITEM_RIGHT_CLICK, self.popupMenuOnItem, self.mainList)


        dbPath = self.getkDatabasePath()
        if not dbPath:
            self.Close(True)

        DatabaseManager.databasePath = dbPath

        self.dbMan = DatabaseManager()
        self.dd = DataDownloader()
        self.pm = PlotManager()

        self.loadDaysTable()


        print("a")


    def popupMenuOnItem(self, event):
        popupMenu = wx.Menu()

        item_plotHr = wx.MenuItem(popupMenu, wx.ID_ANY, "Plot heartrate")
        item_plotSleep = wx.MenuItem(popupMenu, wx.ID_ANY, "Plot sleep")
        item_plotSteps = wx.MenuItem(popupMenu, wx.ID_ANY, "Plot steps")
        item_plotHrSleep = wx.MenuItem(popupMenu, wx.ID_ANY, "Plot heartrate and sleep")
        item_plotHrSteps = wx.MenuItem(popupMenu, wx.ID_ANY, "Plot heartrate and steps")

        item_noteDay = wx.MenuItem(popupMenu, wx.ID_ANY, "Add day note")
        item_noteSleep = wx.MenuItem(popupMenu, wx.ID_ANY, "Add sleep note")

        popupMenu.Append(item_plotHr)
        popupMenu.Append(item_plotSleep)
        popupMenu.Append(item_plotSteps)
        popupMenu.Append(item_plotHrSleep)
        popupMenu.Append(item_plotHrSteps)
        popupMenu.Append(item_noteDay)
        popupMenu.Append(item_noteSleep)

        self.Bind(wx.EVT_MENU, self.plotHeartrate, item_plotHr)
        self.Bind(wx.EVT_MENU, self.plotSleep, item_plotSleep)
        self.Bind(wx.EVT_MENU, self.plotSteps, item_plotSteps)
        self.Bind(wx.EVT_MENU, self.plotHrSleep, item_plotHrSleep)
        self.Bind(wx.EVT_MENU, self.plotHrSteps, item_plotHrSteps)
        self.Bind(wx.EVT_MENU, self.addDayNote, item_noteDay)
        self.Bind(wx.EVT_MENU, self.addSleepNote, item_noteSleep)

        self.mainList.PopupMenu(popupMenu)

    def createMenu(self):
        menuBar = wx.MenuBar()

        menu_app = wx.Menu()
        menu_fitbit = wx.Menu()
        menu_data = wx.Menu()
        menuBar.Append(menu_app, "App")
        menuBar.Append(menu_fitbit, "Fitbit")
        menuBar.Append(menu_data, "Data")

        item_plotRestingHr = wx.MenuItem(menu_data, wx.ID_ANY, text="Plot resting HR")
        menu_data.Append(item_plotRestingHr)

        item_plotWeight= wx.MenuItem(menu_data, wx.ID_ANY, text="Plot weight")
        menu_data.Append(item_plotWeight)

        item_import = wx.MenuItem(menu_fitbit, wx.ID_ANY, text="Import data")
        menu_fitbit.Append(item_import)

        item_tests = wx.MenuItem(menu_fitbit, wx.ID_ANY, text="do test")
        menu_fitbit.Append(item_tests)

        item_configure = wx.MenuItem(menu_fitbit, wx.ID_ANY, text="Configure")
        menu_app.Append(item_configure)

        item_exit = wx.MenuItem(menu_app, wx.ID_ANY, text="Exit")
        menu_app.Append(item_exit)

        self.SetMenuBar(menuBar)

        self.Bind(wx.EVT_MENU, self.configure, item_configure)
        self.Bind(wx.EVT_MENU, self.importData, item_import)
        self.Bind(wx.EVT_MENU, self.dotest, item_tests)
        self.Bind(wx.EVT_MENU, self.closeApp, item_exit)
        self.Bind(wx.EVT_MENU, self.plotWeight, item_plotWeight)
        self.Bind(wx.EVT_MENU, self.plotRestingHr, item_plotRestingHr)


        # menu_fitbit.Append(wx.NewId(), "Update local database")
        # menu_fitbit.Append(wx.NewId(), "Get auth key")
        # menu_app.Append(wx.NewId(), "Select database file")

    def getkDatabasePath(self):
        dbPath = ""

        if not os.path.isfile("database_path.txt"):
            open("database_path.txt", "x").close()

        with open("database_path.txt", "r") as f:
            dbPath = f.readline()
            if not dbPath:
                dlg = wx.TextEntryDialog(self, 'Enter database file path', 'Database configuration')

                if not dlg.ShowModal() == wx.ID_OK:
                    return ''

                dbPath = dlg.GetValue()
                dlg.Destroy()


        if not os.path.isfile(dbPath):
            dlg = wx.MessageDialog(None, "Create database in " + dbPath + "?", 'Database', wx.YES_NO | wx.ICON_QUESTION)
            result = dlg.ShowModal()

            if result == wx.ID_YES:
                createDatabase(dbPath)
            else:
                with open("database_path.txt", "w") as f:
                    f.write('')
                self.getkDatabasePath()

            dlg.Destroy()

        with open("database_path.txt", "w") as f:
            f.write(dbPath)

        return dbPath


    def loadDaysTable(self):
        self.mainListData = self.dbMan.getMainListData()
        sleepStartEnd = self.dbMan.getMainListSleepData()

        for i, row in self.mainListData.iterrows():
            dt = datetime.datetime.strptime(row["date"], "%Y-%m-%d")

            self.mainList.InsertItem(i, dt.strftime("%Y-%m-%d %A "))
            self.mainList.SetItem(i, 1, str(row["restingHr"]))
            self.mainList.SetItem(i, 2, str(row["averageHr"]) + " (" + str(row["minHr"]) + "/" + str(row["maxHr"]) + ")")

            sleepSum = row["sumRem"] + row["sumLight"] + row["sumDeep"]

            sleepData = sleepStartEnd[sleepStartEnd["ID_SLEEP"] == row["ID_SLEEP"]]
            start = sleepData.iloc[0,:]["dateTime"][11:-4]

            endDt = datetime.datetime.strptime(sleepData.iloc[-1,:]["dateTime"][:-4], "%Y-%m-%dT%H:%M:%S")
            end = endDt + datetime.timedelta(seconds=int(sleepData.iloc[-1,:]["durationInSec"]))

            self.mainList.SetItem(i, 3, start + " - " + end.strftime("%H:%M:%S") + " ("+str(int(sleepSum / 60)) + "h " + str(sleepSum % 60) + "m)")

            self.mainList.SetItem(i, 4, str(row["efficiency"]))


    def configure(self, arg):
        dialogAuth = Dialog_configuration()
        dialogAuth.ShowModal()
        dialogAuth.Destroy()

    def importData(self, arg):

        if (self.mainListData["date"].count() > 0):
            startDate = self.mainListData["date"][0]
        else:
            startDate = None

        dialogImport = Dialog_import(startDate)
        result = dialogImport.ShowModal()

        if dialogImport.importFinished:
            self.mainList.DeleteAllItems()
            self.loadDaysTable()

        dialogImport.Destroy()

    def ItemClick(self, event):
        date = event.GetText()
        print(date)

    def dotest(self, args):
        # aa = self.dd.getActivities()
        # tt = json.loads(aa)

        data = self.dbMan.getSleepStagesSummary()

        self.pm.plotSleepStages(data)


        print("aa")

    def plotRestingHr(self, arg):
        resrtingHr = self.dbMan.getRestingHr()
        if resrtingHr.empty:
            self.showMessage('Error', "No restring heartrate data.")
            return

        self.pm.plotDailyData(resrtingHr, "restingHr", "Resting heartrate")

    def plotWeight(self, arg):
        weightData = self.dbMan.getWeight()
        if weightData.empty:
            self.showMessage('Error', "No weight data.")
            return

        self.pm.plotWeight(weightData)


    def plotSteps(self, arg):
        date = self.mainListData["date"][self.mainList.GetFirstSelected()]

        stepsData = self.dbMan.getStepsDay(date, date)
        if stepsData.empty:
            self.showMessage('Error', "No steps data.")
            return

        self.pm.plotSteps(stepsData)

    def plotHrSteps(self, arg):
        date = self.mainListData["date"][self.mainList.GetFirstSelected()]

        stepsData = self.dbMan.getStepsDay(date, date)
        if stepsData.empty:
            self.showMessage('Error', "No steps data.")
            return

        hrData = self.dbMan.getHeartrateDay(date, date)

        self.pm.plotStepsAndHr(stepsData, hrData)


    def plotHeartrate(self, arg):
        date = self.mainListData["date"][self.mainList.GetFirstSelected()]
        hrData = self.dbMan.getHeartrateDay(date, date)
        if hrData.empty:
            self.showMessage('Error', "No heartrate data.")
            return

        self.pm.plotHrRange(hrData)

    def plotHrSleep(self, arg):
        date = self.mainListData["date"][self.mainList.GetFirstSelected()]
        sleepData = self.dbMan.getSleep(date)
        if sleepData.empty:
            self.showMessage('Error', "No sleep data.")
            return

        hrData = self.dbMan.getHeartrateFine(sleepData['dateTime'][0], sleepData['dateTime'][sleepData.shape[0] - 1])

        self.pm.plotHrAndSleep(sleepData, hrData)

    def plotSleep(self, arg):
        date = self.mainListData["date"][self.mainList.GetFirstSelected()]
        sleepData = self.dbMan.getSleep(date)
        if sleepData.empty:
            self.showMessage('Error', "No sleep data.")
            return

        self.pm.plotSleep(sleepData)

    def askNote(self, caption):
        dlg = wx.TextEntryDialog(self, caption, 'Note')

        if not dlg.ShowModal() == wx.ID_OK:
            return ''

        note = dlg.GetValue()
        dlg.Destroy()

        return note

    def addDayNote(self, arg):
        note = self.askNote("Day note:")

        if not note:
            return

        self.dbMan.saveNote("days", note,  self.mainListData["ID"][self.mainList.GetFirstSelected()])

    def addSleepNote(self, arg):
        note = self.askNote("Sleep note:")

        if not note:
            return

        self.dbMan.saveNote("sleepLog", note, self.mainListData["ID_SLEEP"][self.mainList.GetFirstSelected()])

    def closeApp(self, event):
        self.Close(True)

    def onCloseWindow(self, event):
        self.Destroy()

    def showMessage(self, title, text):
        dlg = wx.MessageDialog(None, text, title, wx.OK | wx.ICON_INFORMATION)
        dlg.ShowModal()
        dlg.Destroy()


class FitbitApp(wx.App):
    def OnInit(self):
        frame = MainFrame("Data Browser for Fitbit", (700, 600))
        frame.Show()
        self.SetTopWindow(frame)
        return True

if __name__ == '__main__':
    app = FitbitApp(False)
    locale.setlocale(locale.LC_ALL, "pl_PL")

    app.MainLoop()