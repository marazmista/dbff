#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 15.06.2019

@author: marazmista
"""


import requests
import json
from src.DatabaseManager import *
import base64


class DataDownloader:
    def __init__(self):
        self.dbMan = DatabaseManager()
        self.fitbitId = self.dbMan.getFitbitId()


    def getData(self,url):
        headers = {'Authorization': 'Bearer ' + self.dbMan.getAccessToken()}
        r = requests.get(url, headers = headers)
        return r.text

    def getWeightData(self,date):
        url = 'https://api.fitbit.com/1/user/' + self.fitbitId + '/body/log/weight/date/'+ date +'.json'
        return self.getData(url)

    def getSleepData(self,date):
        url = 'https://api.fitbit.com/1.2/user/' + self.fitbitId + '/sleep/date/' + date + '.json'
        return self.getData(url)


    def getHeartrateDataIntraday(self, date):
        url = 'https://api.fitbit.com/1.2/user/' + self.fitbitId + '/activities/heart/date/' + date + '/1d/1sec.json'
        return self.getData(url)


    def getStepsDataIntraday(self, date):
        url = 'https://api.fitbit.com/1/user/' + self.fitbitId + '/activities/steps/date/' + date + '/1d/1min.json'
        return self.getData(url)

    def getActivities(self):
        url = 'https://api.fitbit.com/1/user/' + self.fitbitId + '/activities/list.json?afterDate=2019-05-05&sort=asc&limit=20&offset=0'
        return self.getData(url)

    def checkTokenStatus(self, token):
        # return status:  0 - ok, 1 - not ok, 2 - too many requests

        if not token:
            return 1, 'No token'

        url = 'https://api.fitbit.com/1.1/oauth2/introspect'

        statusData = self.getData(url)
        status = not statusData

        if status:
            return 0, 'Token OK'

        if statusData == "Too Many Requests":
            return 2, statusData

        data = json.loads(statusData)

        if data["success"] == False and data["errors"][0]["errorType"] == "expired_token":
            return 1, "Token expired"

        return 0, "Token OK"

    def refreshToken(self, clientId, clientSecret, refreshToken):
        success = False
        msg = ''

        encodedSecrets = base64.b64encode((clientId + ":" + clientSecret).encode("utf8"))

        headers = { 'Authorization': 'Basic ' + str(encodedSecrets,"utf8") }
        params = { "grant_type" : "refresh_token", "refresh_token" : refreshToken }

        response = requests.post("https://api.fitbit.com/oauth2/token", headers=headers, data=params)
        success = self.isResponseOk(response)

        if not success:
            msg = self.getErrorFromResponse(response)
        else:
            msg = "Token refreshed"

            tokens = json.loads(response.text)
            self.dbMan.saveTokens(tokens["access_token"], tokens["refresh_token"])

        return success, msg

    def refreshToken2(self):
        clientInfo = self.dbMan.query("select clientId, clientSecret, refreshToken from accountSettings where ID = 1", None)
        return self.refreshToken(clientInfo["clientId"][0], clientInfo["clientSecret"][0], clientInfo["refreshToken"][0])

    def getTokens(self, clientId, clientSecret, code, redirectUri):
        success = False
        msg = ''

        encodedSecrets = base64.b64encode((clientId + ":" + clientSecret).encode("utf8"))

        headers = { 'Authorization': 'Basic ' + str(encodedSecrets,"utf8") }
        params = {"grant_type": "authorization_code", "code": code, "client_id" : clientId, "redirect_uri" : redirectUri }

        response = requests.post("https://api.fitbit.com/oauth2/token", headers=headers, data=params)
        success = self.isResponseOk(response)

        if not success:
            msg = json.loads(response.text)["errors"][0]["message"]
        else:
            msg = "Tokens saved"
            tokens = json.loads(response.text)
            self.dbMan.saveTokens(tokens["access_token"], tokens["refresh_token"])

        return success, msg

    def getErrorFromResponse(self, response):
        return json.loads(response.text)["errors"][0]["message"]

    def isResponseOk(self, response):
       return response.status_code == 200

    def saveToFile(self, date, contents):
        file = open(date + '.json', 'w')
        file.write(contents)
        file.close()

    def getDayId(self, date):
        existsCheck = self.dbMan.queryOne("select id from days where date == ?", [date])
        if existsCheck == None:
            self.dbMan.execute('insert into days (date) values(?)', [date])
            return self.getDayId(date)

        return existsCheck[0]


    def saveSleepToDatabase(self,date):
        idDay = self.getDayId(date)

        data = json.loads(self.getSleepData(date))

        if not data.get('errors') == None:
            return "Error occured: "+ data['errors'][0]['message']


        if len(data['sleep']) == 0:
            return date + " - no sleep record"


        if not self.dbMan.checkRecordsExists('sleepLog', idDay):
            # return "Record already exists!"
            ds = data['sleep'][0]
            sleepData = (idDay, ds['startTime'], ds['endTime'], ds['duration'], ds['efficiency'], 0, '')

            self.dbMan.putSleepRecordToDatabase(sleepData)
        else:
            return date + " - sleep record already exists"


        sleepLogId = self.dbMan.queryOne('select id from sleepLog where ID_DAY == ?', [idDay])[0]
        levelIds = pd.read_sql_query('select id, name from sleepLevelsDefinitions', self.dbMan.conn)

        if not self.dbMan.checkSleepLevelsRecordsExists(sleepLogId):
            sleepList = []
            for s in data['sleep'][0]['levels']['data']:
                sleepLevel = levelIds[levelIds['name'] == s['level']]['ID']
                if not sleepLevel.empty:
                    sleepList.append((s['dateTime'], s['seconds'], int(sleepLevel), sleepLogId))

            self.dbMan.putSleepLevelsToDatabase(sleepList)

        return date + " - sleep imported"


    def saveHeartrateToDatabase(self, date):
        idDay = self.getDayId(date)

        data = json.loads(self.getHeartrateDataIntraday(date))

        if not data.get('errors') == None:
            return 'Error occured: '+ data['errors'][0]['message']

        if not self.dbMan.checkRecordsExists('heartrate', idDay):
            hrList = []
            for hr in data['activities-heart-intraday']['dataset']:
                dateTime = date + 'T' + hr['time']
                hrList.append((idDay, dateTime, hr['value']))

            self.dbMan.putHrRecordsToDatabase(hrList)

        if not self.dbMan.checkRecordsExists('heartData', idDay):
            self.dbMan.execute('insert into heartData (ID_DAY, restingHr) values (?, ?)', [idDay, data['activities-heart'][0]['value']['restingHeartRate']])

        if not self.dbMan.checkRecordsExists('heartZonesData', idDay):
            hrZones = pd.read_sql_query('select id, name from hrZonesDefinitions', self.dbMan.conn)

            zonesList = []
            for zone in data['activities-heart'][0]['value']['heartRateZones']:
                zonesList.append((idDay, int(hrZones[hrZones['name'] == zone['name']]['ID']), zone['minutes']))

            self.dbMan.executeMany('insert into heartZonesData (ID_DAY, ID_ZONE, minutes) values (?, ?, ?)', zonesList)

        return date + " - heartrate imported"


    def saveStepsToDatabase(self,date):
        idDay = self.getDayId(date)

        if self.dbMan.checkRecordsExists('steps', idDay):
            return date + " - steps record already exists"

        data = json.loads(self.getStepsDataIntraday(date))

        if not data.get('errors') == None:
            return 'Error occured: '+ data['errors'][0]['message']

        stepsList = []
        for s in data['activities-steps-intraday']['dataset']:
            dateTime = date + 'T' + s['time']
            stepsList.append((idDay, dateTime, s['value']))

        self.dbMan.putStepsRecordsToDatabase(stepsList)


        return date + " - steps imported"

    def saveWeightToDatabase(self,date):
        idDay = self.getDayId(date)

        if self.dbMan.checkRecordsExists('weight', idDay):
            return date + " - weight record already exists"

        data = json.loads(self.getWeightData(date))

        if not data.get('errors') == None:
            return 'Error occured: ' + data['errors'][0]['message']

        if len(data['weight']) == 0:
            return  date + " - no weight record"

        self.dbMan.putWeightRecordToDatabase((idDay, data['weight'][0]['weight']))

        return date + " - weight imported"


    def downloadDataRange(self,downloadFunction, dateStart, dateEnd):
        dates = pd.date_range(dateStart, dateEnd, freq = 'D').strftime('%Y-%m-%d')

        for d in dates:
            print('Importing ' + d)
            downloadFunction(d)


    def saveActivitiesToDatabase(self):
        data = json.loads(self.getActivities())
        print('a')




        # dt = datetime.datetime.strptime(date, "%Y-%m-%d").date()
        # dt = dt + datetime.timedelta(days = 1)

        # existsCheck = c.execute("select id from heartrate where date between ? and ?", [date, dt.strftime('%Y-%m-%d')]).fetchone()
        # if not existsCheck == None:
        #     print("Records already exists!")
        #     return