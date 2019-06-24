#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 16.06.2019

@author: marazmista
"""

import wx
import webbrowser
from src.DataDownloader import *

class Dialog_configuration(wx.Dialog):

    def __init__(self):
        wx.Dialog.__init__(self, None, 0, "Configuration", pos = wx.DefaultPosition, style=wx.DEFAULT_DIALOG_STYLE)
        self.Center()
        box_grid = wx.GridSizer(5, 2, 5, 5)
        box_main = wx.BoxSizer(wx.VERTICAL)


        btn_authPage = wx.Button(self, wx.ID_ANY,"Open Auth Page")
        btn_getAccessToken = wx.Button(self, wx.ID_ANY, "Get Access Token")
        btn_refreshToken = wx.Button(self, wx.ID_ANY, "Refresh Token")
        btn_ok = wx.Button(self, wx.ID_OK, "OK")
        btn_cancel = wx.Button(self, wx.ID_CANCEL, "Cancel")


        self.txt_fbUserId = wx.TextCtrl(self, -1)
        self.txt_clientId = wx.TextCtrl(self, -1)
        self.txt_clientSecret = wx.TextCtrl(self, -1, size = (200,30))
        self.txt_redirectUri = wx.TextCtrl(self, -1)

        l_fbUserId = wx.StaticText(self, -1, "Fitibit ID:")
        l_clientId = wx.StaticText(self, -1, "Client ID:")
        l_clientSecret = wx.StaticText(self, -1, "Client secret:")
        l_redirectUri = wx.StaticText(self, -1, "Redirect URI :")


        box_main.Add(btn_authPage, 0,  wx.EXPAND | wx.ALL,5)
        box_main.Add(btn_getAccessToken,0,  wx.EXPAND | wx.ALL, 5)
        box_main.Add(btn_refreshToken, 0,  wx.EXPAND | wx.ALL, 5)

        box_grid.Add(l_fbUserId, 1, wx.EXPAND)
        box_grid.Add(self.txt_fbUserId , 1, wx.EXPAND)
        box_grid.Add(l_clientId , 1, wx.EXPAND)
        box_grid.Add(self.txt_clientId , 1, wx.EXPAND)
        box_grid.Add(l_clientSecret , 1, wx.EXPAND)
        box_grid.Add(self.txt_clientSecret, 1, wx.EXPAND)
        box_grid.Add(l_redirectUri, 1, wx.EXPAND)
        box_grid.Add(self.txt_redirectUri, 1, wx.EXPAND)
        box_grid.Add(btn_cancel, 1, wx.EXPAND)
        box_grid.Add(btn_ok, 1, wx.EXPAND)

        box_main.Add(box_grid, 1, wx.EXPAND | wx.ALL, 5)

        box_grid.SetSizeHints(self)
        box_main.SetSizeHints(self)
        self.SetSizer(box_main)

        self.Bind(wx.EVT_BUTTON, self.okClick, btn_ok)
        self.Bind(wx.EVT_BUTTON, self.refreshToken, btn_refreshToken)
        self.Bind(wx.EVT_BUTTON, self.getTokens, btn_getAccessToken)
        self.Bind(wx.EVT_BUTTON, self.openAuthPage, btn_authPage)

        self.dbManager = DatabaseManager()

        settings = self.dbManager.getSettings()

        self.txt_fbUserId.SetValue(settings["fitbitId"][0])
        self.txt_clientId.SetValue(settings["clientId"][0])
        self.txt_clientSecret.SetValue(settings["clientSecret"][0])
        self.txt_redirectUri.SetValue(settings["redirectUri"][0])


    def refreshToken(self, arg):
        token = self.dbManager.getRefreshToken()

        if not token:
            return

        dd = DataDownloader()
        response = dd.refreshToken(self.txt_clientId.GetValue(), self.txt_clientSecret.GetValue(), token)

        if not self.checkResponse(response):
            return

        tokens = json.loads(response.text)
        self.dbManager.saveTokens(tokens["access_token"], tokens["refresh_token"])

        dlg = wx.MessageDialog(None, 'Token refreshed.',
                               'Token status', wx.OK | wx.ICON_ERROR)
        dlg.ShowModal()
        dlg.Destroy()


    def getTokens(self, arg):
        dlg = wx.TextEntryDialog(self, 'Enter code or returned URL', 'Code')

        if not dlg.ShowModal() == wx.ID_OK:
            return

        code = dlg.GetValue()
        dlg.Destroy()

        if "http" in code:
            code = code[code.find("code=") + 5 : code.find("#")]

        dd = DataDownloader()
        response = dd.getTokens(self.txt_clientId.GetValue(), self.txt_clientSecret.GetValue(), code, self.txt_redirectUri.GetValue())

        if not self.checkResponse(response):
            return

        tokens = json.loads(response.text)
        self.dbManager.saveTokens(tokens["access_token"], tokens["refresh_token"])

    def checkResponse(self, response):
        if response.status_code != 200:
            dlg = wx.MessageDialog(None, json.loads(response.text)["errors"][0]["message"], 'Error', wx.OK | wx.ICON_ERROR)
            result = dlg.ShowModal()
            dlg.Destroy()
            return False

        return True

    def openAuthPage(self, arg):
        webbrowser.open("https://www.fitbit.com/oauth2/authorize?response_type=code&client_id=" + self.txt_clientId.GetValue() +
        "&redirect_uri=" + self.txt_redirectUri.GetValue() + "&scope=activity+heartrate+sleep+weight", new = 2)


    def okClick(self, arg):
        self.dbManager.saveAccountSettings((self.txt_fbUserId.GetValue(), self.txt_clientId.GetValue(), self.txt_clientSecret.GetValue(), self.txt_redirectUri.GetValue()))
        self.EndModal(wx.ID_OK)
