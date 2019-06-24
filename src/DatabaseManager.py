#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Created on 15.06.2019

@author: marazmista
"""

import sqlite3
import pandas as pd

class DatabaseManager:

    databasePath = ""

    def __init__(self):
        self.conn = sqlite3.connect(self.databasePath)

    def query(self, query, params):
        return pd.read_sql_query(query, self.conn, params=params)

    def queryOne(self, query, where):
        return self.conn.cursor().execute(query, where).fetchone()

    def execute(self, query, param):
        self.conn.cursor().execute(query, param)
        self.conn.commit()

    def executeMany(self, query, param):
        self.conn.cursor().executemany(query, param)
        self.conn.commit()

    def putHrRecordsToDatabase(self, hrList):
        self.executeMany('insert into heartrate (ID_DAY, dateTime, hr) values(?, ?, ?)', hrList)

    def putWeightRecordToDatabase(self, weightRecord):
        self.execute('insert into weight (ID_DAY, weight) values (?, ?)', weightRecord)

    def putStepsRecordsToDatabase(self, stepsList):
        self.executeMany('insert into steps (ID_DAY, dateTime, steps) values(?,?,?)', stepsList)

    def putSleepRecordToDatabase(self, sleepData):
        self.execute('insert into sleepLog(ID_DAY, startTime, endTime, durationInSec, efficiency, score, note) values(?,?,?,?,?,?,?)' , sleepData)

    def putSleepLevelsToDatabase(self, sleepLevels):
        self.executeMany('insert into sleepLevels(dateTime, durationInSec, ID_LEVEL, ID_SLEEP) values (?,?,?,?)', sleepLevels)
    #
    # def saveAccessTokenToDatabase(self, accessToken):
    #     self.execute('insert into accountSettings (accessToken) values (?)', [accessToken])

    def getWeight(self):
        return self.query("select days.date, weight.weight from weight join days on days.ID = weight.ID_DAY order by days.ID", None)

    def getRestingHr(self):
        return self.query("select days.date, restingHr from heartData join days on days.ID = heartData.ID_DAY order by days.ID", None)

    def getHeartrateDay(self, dateStart, dateEnd):
        return self.query('select dateTime, hr from heartrate join days on days.ID = heartrate.ID_DAY where days.date between ? and ?',
            params=(dateStart, dateEnd))

    def getHeartrateFine(self, dateStart, dateEnd):
        return self.query(
            'select dateTime, hr from heartrate where dateTime between ? and ?',
            params=(dateStart, dateEnd))

    def getStepsDay(self, dateStart, dateEnd):
        return  self.query("select dateTime, steps from steps join days on days.ID = steps.ID_DAY where days.date between ? and ?", params = (dateStart, dateEnd))

    def getStepsFine(self, dateStart, dateEnd):
        return  self.query("select dateTime, steps from steps where dateTime between ? and ?", params = (dateStart, dateEnd))

    def getSleepStagesSummary(self):
        return self.query("select sumAwake, sumRem, sumLight, sumDeep, days.date from sleepLevelsLengths "
                          "join sleepLog on sleepLog.ID = sleepLevelsLengths.ID_SLEEP "
                          "join days on days.ID = sleepLog.ID_DAY order by sleepLevelsLengths.ID_SLEEP desc limit 30", None)

    def getSleep(self, date):
        return self.query("select dateTime, levelNum from sleepLog "
                             "join sleepLevels on sleepLevels.ID_SLEEP = sleepLog.ID join sleepLevelsDefinitions on sleepLevels.ID_LEVEL = sleepLevelsDefinitions.ID "
                             "join days on days.ID = sleepLog.ID_DAY "
                             "where days.date == ?", params=[date])

    def getMainListData(self):
        return pd.read_sql_query("select days.ID, sleepHeartStats.ID_SLEEP, days.date, heartData.restingHr, sleepHeartStats.averageHr, sleepHeartStats.minHr, sleepHeartStats.maxHr, "
                                 "sumAwake, sumRem, sumLight, sumDeep, sleepLog.efficiency from days "
                                 "join heartData on days.ID = heartData.ID_DAY "
                                 "join sleepHeartStats on sleepHeartStats.ID_DAY = days.ID "
                                 "join sleepLevelsLengths on sleepLevelsLengths.ID_SLEEP = sleepHeartStats.ID_SLEEP "
                                 "join sleepLog on days.ID = sleepLog.ID_DAY "
                                 "order by days.date desc", self.conn)
    #
    def getMainListSleepData(self):
        return pd.read_sql_query("SELECT sleepLevels.ID_SLEEP, sleepLevels.ID, sleepLevels.dateTime, sleepLevels.durationInSec "
                                "from sleepLevels where sleepLevels.ID_LEVEL > 1 and sleepLevels.durationInSec > 360", self.conn)


    def getAccessToken(self):
        token = self.conn.cursor().execute('select accessToken from accountSettings where ID == 1').fetchone()

        if token[0] == None:
            return ''

        return token[0]

    def getRefreshToken(self):
        token = self.conn.cursor().execute('select refreshToken from accountSettings where ID == 1').fetchone()

        if token[0] == None:
            return ''

        return token[0]

    def getFitbitId(self):
        fitibtId = self.conn.cursor().execute('select fitbitId from accountSettings where ID == 1').fetchone()

        if fitibtId == None:
            return ''

        return fitibtId[0]


    def saveAccountSettings(self, settings):
        self.execute("update accountSettings set fitbitId=?, clientId = ?, clientSecret = ?, redirectUri = ? where ID == 1", settings)

    def saveTokens(self, accessToken, refreshToken):
        self.execute("update accountSettings set accessToken = ?, refreshToken = ? where ID == 1", [accessToken, refreshToken])

    def getSettings(self):
       return self.query("select fitbitId, clientId, clientSecret, redirectUri from accountSettings where ID == 1", None)


    def checkRecordsExists(self, table, idDay):
        existsCheck = self.queryOne("select id from " + table + " where ID_DAY = ?", [idDay])
        if existsCheck == None:
            return False

        return True

    def checkSleepLevelsRecordsExists(self, idSleep):
        existsCheck = self.queryOne("select id from sleepLevels where ID_SLEEP = ?", [idSleep])
        if existsCheck == None:
            return False

        return True