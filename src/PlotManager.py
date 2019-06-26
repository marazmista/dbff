#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Apr 13 18:39:05 2019

@author: marazmista
"""

import pandas as pd
import datetime
from bokeh.plotting import figure, show
from bokeh.models import DatetimeTickFormatter
from bokeh.models import HoverTool
from bokeh.models import LinearAxis, Range1d
from bokeh.models import ColumnDataSource


class PlotManager:

    bgColor = '#1a2a3a'
    primaryColor = '#6666ff'
    secondaryColor = '#66ff99'

    colorSleepAwake = "#e73360"
    colorSleepRem = "#7ec4ff"
    colorSleepLight = "#3f8dff"
    colorSleepDeep = "#154ba6"

    colorZoneFatBurn = "#ffb319"
    colorZoneCardio = "#ff8c19"
    colorZonePeak = "#e60013"

    def createFigure(self, title, timeFormat):
        sizeMode = "stretch_both"
        # plot_width = 6000,

        p = figure(title=title ,sizing_mode=sizeMode, x_axis_type='datetime')
        p.xaxis.formatter = DatetimeTickFormatter(hours=[timeFormat])
        p.background_fill_color = self.bgColor
        p.ygrid.grid_line_alpha = 0.25
        p.xgrid.grid_line_alpha = 0.25
        p.yaxis.minor_tick_line_color = None
        p.xaxis[0].ticker.desired_num_ticks = 24
        p.yaxis[0].ticker.desired_num_ticks = 16
        # p.border_fill_color = '#000000'

        p.add_tools(HoverTool(mode = 'vline',
                              tooltips=[("Time", "@x{%F %T}"), ("Value: ", "@y")],
                              formatters={"x": "datetime"}))

        return p


    def plotHrRange(self, hrData):
        hrData['dateTime'] = pd.to_datetime(hrData['dateTime'], format='%Y-%m-%dT%H:%M:%S',errors='ignore')

        # p = figure(title="Heart Rate" , sizing_mode='scale_height', plot_width=6000, x_axis_type='datetime')
        p = self.createFigure("Heart Rate", "%H:%M:%S")
        p.line(hrData["dateTime"], hrData["hr"], legend = "HR", line_width = 2,  line_color=self.primaryColor)

        show(p)


    def plotDailyData(self, data, seriesName, title):
        data['date'] = pd.to_datetime(data['date'], format='%Y-%m-%d',errors='ignore')

        p = self.createFigure(title, "%Y-%m-%d")
        p.line(data["date"], data[seriesName], legend = title, line_width = 2, line_color=self.primaryColor)

        show(p)

    def plotHeartrateZones(self, hrZonesData):
        zones = ['Fat Burn', 'Cardio', 'Peak']
        dates = hrZonesData["date"].tolist()[::-1]
        colors = [ self.colorZoneFatBurn, self.colorZoneCardio, self.colorZonePeak]
        # "#6eff19",

        data = {'date' : dates,
                'Peak': hrZonesData["peak"].tolist()[::-1],
                'Cardio': hrZonesData["cardio"].tolist()[::-1],
                'Fat Burn': hrZonesData["fatBurn"].tolist()[::-1]}

        # p = figure(x_range=dates, title="Sleep stages", width=sleepData.shape[0] * 30, sizing_mode='scale_height', tools="hover", tooltips="@date: $name @$name min")
        p = figure(x_range=dates, title="HR zones", width=2000, sizing_mode='stretch_both', tools="hover", tooltips="@date: $name @$name min")

        p.vbar_stack(zones, x='date', width=0.9 ,color=colors, source=data)

        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.background_fill_color = self.bgColor
        p.ygrid.grid_line_alpha = 0.25
        p.xgrid.grid_line_alpha = 0.25
        p.yaxis.minor_tick_line_color = None

        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"

        show(p)




    def plotSleepStages(self, sleepData):
        # p = self.createFigure("Sleep stages", '%Y-%m-%d')
        # sleepData["date"] = pd.to_datetime(sleepData["date"], format='%Y-%m-%d', errors='ignore')

        stages =['Deep',  "Light" , 'REM','Awake']
        dates = sleepData["date"].tolist()[::-1]
        colors = [  self.colorSleepDeep,self.colorSleepLight , self.colorSleepRem, self.colorSleepAwake ]

        data = {'date': dates,
                'Awake': sleepData["sumAwake"].tolist()[::-1],
                'REM': sleepData["sumRem"].tolist()[::-1],
                'Light': sleepData["sumLight"].tolist()[::-1],
                'Deep': sleepData["sumDeep"].tolist()[::-1]}

        # p = figure(x_range=dates, title="Sleep stages", width=sleepData.shape[0] * 30, sizing_mode='scale_height', tools="hover", tooltips="@date: $name @$name min")
        p = figure(x_range=dates, title="Sleep stages", width=2000, sizing_mode='stretch_both', tools="hover", tooltips="@date: $name @$name min")

        p.vbar_stack(stages, x='date', width=0.9 ,color=colors, source=data)

        p.xgrid.grid_line_color = None
        p.axis.minor_tick_line_color = None
        p.outline_line_color = None
        p.background_fill_color = self.bgColor
        p.ygrid.grid_line_alpha = 0.25
        p.xgrid.grid_line_alpha = 0.25
        p.yaxis.minor_tick_line_color = None

        p.legend.location = "top_left"
        p.legend.orientation = "horizontal"

        show(p)
        #
        #
        # stages = ['Awake', 'REM', "Light" , 'Deep']
        #
        # data = { 'Date' : sleepData["date"].tolist() ,
        #          'Awake:': sleepData["sumAwake"].tolist(),
        #          'REM:' :sleepData["sumRem"].tolist(),
        #          'Ligth:' :sleepData["sumLight"].tolist(),
        #          'Deep:': sleepData["sumDeep"].tolist() }
        #
        # # source = ColumnDataSource(sleepData.groupby('date')['sumAwake', "sumRem", "sumLight", "sumDeep"].sum())
        #
        # p = figure(x_range=sleepData["date"], toolbar_location=None, tools="")
        #
        # p.vbar_stack(stages, x='Date', source=data, width=0.9)
        #
        # show(p)



    def plotWeight(self, weigthData):
        self.plotDailyData(weigthData, "weight", "Weight")

        # weigthData['date'] = pd.to_datetime(weigthData['date'], format='%Y-%m-%d',errors='ignore')
        #
        # p = self.createFigure("Weight", "%Y-%m-%d")
        # p.line(weigthData["date"], weigthData["weight"], legend = "Weight", line_width = 2, line_color=self.primaryColor)
        #
        # show(p)

    def plotSleep(self, sleepData):
        sleepData['dateTime'] = pd.to_datetime(sleepData['dateTime'], format='%Y-%m-%dT%H:%M:%S',errors='ignore')

        # sleepForPlot = pd.DataFrame(columns=['date', 'level'])
        # for item in sleepData.iterrows():
        #     sleepForPlot = sleepForPlot.append([{'date': item[1][0], 'level': item[1][2]*-1}], ignore_index=True)
        #     sleepForPlot = sleepForPlot.append([{'date': item[1][0] + datetime.timedelta(seconds=item[1][1]) , 'level': item[1][2]*-1}], ignore_index=True)

        p = self.createFigure("Sleep", "%H:%M:%S")
        p.step(sleepData["dateTime"], sleepData["levelNum"], legend = "Stage", line_width = 2, mode = 'after',  line_color=self.primaryColor)

        show(p)

    def plotHrAndSleep(self, sleepData, hrData):
        sleepData['dateTime'] = pd.to_datetime(sleepData['dateTime'], format='%Y-%m-%dT%H:%M:%S',errors='ignore')
        hrData['dateTime'] = pd.to_datetime(hrData['dateTime'], format='%Y-%m-%dT%H:%M:%S',errors='ignore')

        p = self.createFigure("Sleep and heartrate", "%H:%M:%S")
        p.extra_y_ranges = {'levelNum': Range1d(start = -1, end = 4)}
        p.add_layout(LinearAxis(y_range_name = 'levelNum'), 'right')

        p.line(hrData['dateTime'], hrData['hr'], legend = "HR", line_width = 2, line_color=self.primaryColor)
        p.step(sleepData['dateTime'], sleepData['levelNum'],  legend = "Stage", line_width = 2, mode = 'after', y_range_name='levelNum', line_color=self.secondaryColor)

        p.y_range = Range1d(start = 35, end = 85)

        # p.ygrid.grid_line_dash = [6, 4]
        # p.xgrid.grid_line_dash = [6, 4]

        show(p)

    def plotSteps(self, stepsData):
        stepsData['dateTime'] = pd.to_datetime(stepsData['dateTime'], format='%Y-%m-%dT%H:%M:%S',errors='ignore')

        p = self.createFigure("Steps", "%H:%M:%S")
        p.vbar(x = stepsData['dateTime'], top = stepsData['steps'], width = 0.5, line_width=7, bottom = 0, line_color=self.primaryColor)

        show(p)

    def plotStepsAndHr(self, stepsData, hrData):

        stepsData['dateTime'] = pd.to_datetime(stepsData['dateTime'], format='%Y-%m-%dT%H:%M:%S',errors='ignore')
        hrData['dateTime'] = hrData['date'] = pd.to_datetime(hrData['dateTime'], format='%Y-%m-%dT%H:%M:%S',errors='ignore')

        p = self.createFigure("Steps and heartrate", "%Y-%m-%d")
        p.extra_y_ranges = {'hrScale': Range1d(start = hrData['hr'].min() - 10, end = hrData['hr'].max() + 10)}
        p.add_layout(LinearAxis(y_range_name = 'hrScale'), 'right')

        p.line(hrData['dateTime'], hrData['hr'], legend = "HR", y_range_name = 'hrScale', line_color=self.primaryColor)
        p.vbar(x = stepsData['dateTime'], top = stepsData['steps'], width = 0.5, bottom = 0, line_color=self.secondaryColor)

        show(p)

# plotHrRange('2019-04-07 17:00:00', '2019-04-07 19:00:00')
# plotSleep('2019-04-15')
# plotHrAndSleep('2019-04-04')


# conn.close()