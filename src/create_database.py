#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 17:27:29 2019

@author: marazmista
"""

import sqlite3

def createDatabase(path):
    conn = sqlite3.connect(path)

    c = conn.cursor()


    # Create table
    c.execute('CREATE TABLE heartrate (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, ID_DAY int, dateTime text, hr int, FOREIGN KEY(ID_DAY) REFERENCES days(ID))')
    c.execute('CREATE TABLE sleepLog (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT , ID_DAY int, startTime text, endTime text, durationInSec int, efficiency int, score int DEFAULT 0, note text DEFAULT "", FOREIGN KEY(ID_DAY) REFERENCES days(ID))')
    c.execute('CREATE TABLE sleepLevels (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, dateTime text, durationInSec int, ID_LEVEL INTEGER, ID_SLEEP INTEGER, ' +
                                         'FOREIGN KEY(ID_LEVEL) REFERENCES sleepLevelsDefinitions(ID), FOREIGN KEY(ID_SLEEP) REFERENCES sleepLog(ID))')
    c.execute('CREATE TABLE sleepLevelsDefinitions (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, levelNum int, name text)')
    c.execute('CREATE TABLE steps (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, ID_DAY int, dateTime text, steps int, FOREIGN KEY(ID_DAY) REFERENCES days(ID))')
    c.execute('CREATE TABLE heartrateNotes (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, ID_rangeStart INTEGER, ID_rangeStop INTEGER, note text  DEFAULT "", FOREIGN KEY(ID_rangeStart) REFERENCES heartrate(ID), FOREIGN KEY(ID_rangeStop) REFERENCES heartrate(ID))')
    c.execute('CREATE TABLE weight (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, ID_DAY INTEGER, weight int, FOREIGN KEY(ID_DAY) REFERENCES days(ID))')
    c.execute('CREATE TABLE accountSettings (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, fitbitId text DEFAULT "", clientId text DEFAULT "", clientSecret text DEFAULT "", redirectUri text DEFAULT "", accessToken text DEFAULT "", refreshToken text DEFAULT "")')
    c.execute('CREATE TABLE days (ID INTEGER PRIMARY KEY ASC AUTOINCREMENT, date text DEFAULT "", note text DEFAULT "")')

    c.execute('CREATE TABLE "hrZonesDefinitions" ( "ID" INTEGER PRIMARY KEY AUTOINCREMENT, "name" TEXT DEFAULT "", "max" INTEGER DEFAULT 0, "min" INTEGER DEFAULT 0);')
    c.execute('CREATE TABLE "heartData" ( "ID" INTEGER PRIMARY KEY AUTOINCREMENT, "ID_DAY" INTEGER, "restingHr" INTEGER);')
    c.execute('CREATE TABLE "heartZonesData" ( "ID" INTEGER PRIMARY KEY AUTOINCREMENT, "ID_DAY" INTEGER, "ID_ZONE" INTEGER, "minutes" INTEGER DEFAULT 0, FOREIGN KEY("ID_ZONE") REFERENCES "hrZonesDefinitions"("ID"), FOREIGN KEY("ID_DAY") REFERENCES "days"("ID"));')


    c.execute("insert into sleepLevelsDefinitions (levelNum, name) values(3, 'wake')")
    c.execute("insert into sleepLevelsDefinitions (levelNum, name) values(2, 'rem')")
    c.execute("insert into sleepLevelsDefinitions (levelNum, name) values(1, 'light')")
    c.execute("insert into sleepLevelsDefinitions (levelNum, name) values(0, 'deep')")

    c.execute("insert into accountSettings (fitbitId) values('')")

    c.execute("insert into hrZonesDefinitions (name, min, max) values('Out of Range', 30, 96)")
    c.execute("insert into hrZonesDefinitions (name, min, max) values('Fat Burn', 96, 135)")
    c.execute("insert into hrZonesDefinitions (name, min, max) values('Cardio', 135, 164)")
    c.execute("insert into hrZonesDefinitions (name, min, max) values('Peak', 164, 220)")

    c.execute("CREATE VIEW sleepHeartStats(ID_DAY, ID_SLEEP, averageHr, minHr, maxHr) as "
              "SELECT sleepLog.ID_DAY, sleepLog.id, round(avg(hr)) as averageHr, min(hr) as minHr, max(hr) as maxHr "
              "from sleepLog join heartrate on  sleepLog.ID_DAY = heartrate.ID_DAY "
              "where heartrate.dateTime BETWEEN sleepLog.startTime and sleepLog.endTime GROUP by sleepLog.ID_DAY")

    c.execute("CREATE VIEW sleepLevelsLengths as select ID_SLEEP, "
              "sum(case when ID_LEVEL == 1 then durationInSec else 0 end) / 60 as sumAwake, "
              "sum(case when ID_LEVEL == 2 then durationInSec else 0 end) / 60 as sumRem, "
              "sum(case when ID_LEVEL == 3 then durationInSec else 0 end) / 60 as sumLight, "
              "sum(case when ID_LEVEL == 4 then durationInSec else 0 end) / 60 as sumDeep from sleepLevels GROUP by ID_SLEEP")


    conn.commit()
    conn.close()

