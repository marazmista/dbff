#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 15.06.2019

@author: marazmista
"""

import wx
import wx.adv
from src.DataDownloader import *
from src.DatabaseManager import *
import pandas as pd
import datetime

class Dialog_import(wx.Dialog):

    importFinished = False

    def __init__(self, startDate):
        wx.Dialog.__init__(self, None, id=0, title="Import data", pos=wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE)
        self.Center()

        box_main = wx.BoxSizer(wx.VERTICAL)
        box_btn = wx.BoxSizer(wx.HORIZONTAL)
        box_main2 = wx.BoxSizer(wx.HORIZONTAL)

        box1 = wx.StaticBox(self, -1 , "Import slection")
        box2 = wx.StaticBox(self, -1 , "Date range")

        sbox_cb = wx.StaticBoxSizer(box1, wx.VERTICAL)
        sbox_dates = wx.StaticBoxSizer(box2, wx.VERTICAL)

        self.cb_importHr = wx.CheckBox(self, label="Import heartrate")
        self.cb_importSleep = wx.CheckBox(self, label="Import sleep data")
        self.cb_importSteps = wx.CheckBox(self, label="Import steps")
        self.cb_importWeight = wx.CheckBox(self, label="Import weight")

        self.cb_importHr.SetValue(True)
        self.cb_importSleep.SetValue(True)
        self.cb_importSteps.SetValue(True)
        self.cb_importWeight.SetValue(True)

        self.dp_dateStart = wx.adv.DatePickerCtrl(self, size = (100,30))
        self.dp_dateEnd = wx.adv.DatePickerCtrl(self,  size = (100,30))
        self.cb_onlyStartDate = wx.CheckBox(self, label="Import only start date")

        if not startDate == None:
            dtStart = datetime.datetime.strptime(startDate, "%Y-%m-%d") + datetime.timedelta(days=1)
            self.dp_dateStart.SetValue(wx.DateTime(day=dtStart.day, month=dtStart.month - 1, year=dtStart.year))


        l_start = wx.StaticText(self, -1, "Start date: ")
        l_end = wx.StaticText(self, -1, "End date: ")

        btn_import = wx.Button(self, wx.ID_ANY, "Import")
        btn_close = wx.Button(self, wx.ID_CLOSE, "Close")

        self.txt_logOutput = wx.TextCtrl(self, -1, style=wx.TE_MULTILINE | wx.TE_READONLY, size=(200,200))

        box_btn.Add(btn_close)
        box_btn.Add(btn_import)
        box_btn.SetSizeHints(self)

        sbox_dates.Add(l_start, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sbox_dates.Add(self.dp_dateStart, 0, wx.ALL, 5)
        sbox_dates.Add(self.cb_onlyStartDate, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sbox_dates.Add(l_end, 0, wx.ALIGN_CENTER_VERTICAL | wx.ALL, 5)
        sbox_dates.Add(self.dp_dateEnd, 0, wx.ALL, 5)

        sbox_dates.SetSizeHints(self)

        sbox_cb.Add(self.cb_importHr, 0, wx.ALL, 5)
        sbox_cb.Add(self.cb_importSleep, 0, wx.ALL, 5)
        sbox_cb.Add(self.cb_importSteps, 0, wx.ALL, 5)
        sbox_cb.Add(self.cb_importWeight, 0, wx.ALL, 5)
        sbox_cb.SetSizeHints(self)

        box_main2.Add(sbox_dates, 0, wx.EXPAND | wx.ALL, 5)
        box_main2.Add(sbox_cb, 0, wx.EXPAND | wx.ALL, 5)
        box_main.Add(box_main2, 0, wx.EXPAND | wx.ALL, 5)
        box_main.Add(self.txt_logOutput, 1, wx.EXPAND | wx.ALL, 5)
        box_main.Add(box_btn, 0, wx.ALIGN_RIGHT | wx.ALL, 5)
        box_main.SetSizeHints(self)

        self.Bind(wx.EVT_BUTTON, self.importData, btn_import)
        self.Bind(wx.EVT_BUTTON, self.close, btn_close)

        self.SetSizer(box_main)


    def importData(self, args):
        valid, dateStart, dateEnd = self.checkDatesValidity(self.dp_dateStart.GetValue().Format("%Y-%m-%d"), self.dp_dateEnd.GetValue().Format("%Y-%m-%d"))
        if not valid:
            return

        dd = DataDownloader()
        dbMan = DatabaseManager()

        tokenStatus, msg = dd.checkTokenStatus(dbMan.getAccessToken())
        self.txt_logOutput.AppendText(msg + "\n")

        if tokenStatus == 1:

            success, msg = dd.refreshToken2()
            self.txt_logOutput.AppendText(msg + "\n")

            if not success:
                self.txt_logOutput.AppendText(msg + "\n")

        elif tokenStatus == 2:
            return


        dates = pd.date_range(dateStart, dateEnd, freq='D').strftime('%Y-%m-%d')
        for d in dates:
            if self.cb_importHr.IsChecked():
                self.txt_logOutput.AppendText(dd.saveHeartrateToDatabase(d) + "\n")
                wx.Yield()

            if self.cb_importSleep.IsChecked():
                self.txt_logOutput.AppendText(dd.saveSleepToDatabase(d) + "\n")
                wx.Yield()

            if self.cb_importSteps.IsChecked():
                self.txt_logOutput.AppendText(dd.saveStepsToDatabase(d) + "\n")
                wx.Yield()

            if self.cb_importWeight.IsChecked():
                self.txt_logOutput.AppendText(dd.saveWeightToDatabase(d) + "\n")
                wx.Yield()

        self.txt_logOutput.AppendText("Finished")
        self.importFinished = True

    def checkDatesValidity(self, dateStart, dateEnd):

        dtStart = datetime.datetime.strptime(dateStart, "%Y-%m-%d")
        dtEnd = datetime.datetime.strptime(dateStart, "%Y-%m-%d")

        if dtStart.date() >= datetime.date.today() and (self.cb_importHr.IsChecked() or self.cb_importSteps.IsChecked()):
            dlg = wx.MessageDialog(self, 'Cannot import heartrate and steps before end of the day.', "Error")
            dlg.ShowModal()
            dlg.Destroy()

            return False, '', ''

        if dtEnd.date() > datetime.date.today():
            return False, '', ''

        if self.cb_onlyStartDate.IsChecked() or dtStart > dtEnd:
            dateEnd = dateStart

        return True, dateStart, dateEnd


    def close(self, args):
        self.EndModal(wx.ID_CLOSE)

