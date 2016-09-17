#!/usr/bin/kivy
##======================================================================================
##	This program is free software: you can redistribute it and/or modify
##	it under the terms of the GNU General Public License as published by
##	the Free Software Foundation, either version 3 of the License, or
##	(at your option) any later version.
##
##	This program is distributed in the hope that it will be useful,
##	but WITHOUT ANY WARRANTY; without even the implied warranty of
##	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##	GNU General Public License for more details.
##
##	You should have received a copy of the GNU General Public License
##	along with this program.  If not, see <http://www.gnu.org/licenses/>.
##======================================================================================
##======================================================================================
## You will notice "# No.'s" in the comments, these comments are there to signify the
## order of when the code was referenced in the tutorial. 
## "# Not defined in tut" means I did not explicitly sate the code within the tutorial
## instead I would have said for example "repeat code for the other buttons"
##
##======================================================================================
# Size of 7" RPi Screen
# Set windows properties before creating the window.
import kivy									# Not defined in tut
from kivy.config import Config				# Not defined in tut
Config.set('graphics', 'width', '837')		# Not defined in tut
Config.set('graphics', 'height', '464')		# Not defined in tut
Config.set('graphics', 'resizable', '0')	# Not defined in tut
Config.set('graphics', 'show_cursor', '1')	# Not defined in tut
kivy.require('1.9.1')						# Not defined in tut
from kivy.app import App 					# 1
from kivy.uix.boxlayout import BoxLayout 	# 1
from kivy.uix.button import Button 			# 1
from kivy.uix.floatlayout import FloatLayout 	# Not defined in tut
from kivy.garden.graph import Graph, LinePlot	# 7
from kivy.properties import NumericProperty, ObjectProperty	# Not defined in tut

from kivy.clock import Clock	# 8
import datetime, time			# 8

# 4
import RPi.GPIO as GPIO            # 4 Import RPi GPIO module
GPIO.setmode(GPIO.BCM)             # 4 BCM or BOARD
GPIO.setup(20, GPIO.OUT)           # 4 GPIO20 Coffee Button output
GPIO.setup(23, GPIO.OUT)           # 4 GPIO23 Boiler output
GPIO.setup(19, GPIO.OUT)           # 4 GPIO19 Water Button output

# 8
SAMPLE_RATE 		= 1		# Seconds
TIME_DECIMALS       = 100	# used for rounding
START_SCROLLING     = 150	# (Sec) [time before starting to scroll] = START_SIZE_WINDOW - START_SCROLLING  
START_SIZE_WINDOW   = 300	# (Sec) time of X axis 

# 10
import os, glob, subprocess
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '3b-000000191766')[0]
device_file = device_folder + '/w1_slave'

STEAM_TEMP_SP = 140		# Not defined in tut

class PlotterWidget(Graph): # 7
	# 7
	SPplot = ObjectProperty(None) # Set Point, will either be 105 or 140
	PVplot = ObjectProperty(None) # Process Value, will be temperature
	
	# 8
	index =	ObjectProperty(0) # Time
	startTime = ObjectProperty(0)
	currentTemp =  ObjectProperty(23)
	currentSignal = ObjectProperty(105)
	
	def __init__(self, **kwargs):
		# 8
		self.startTime = self.getCurrentTime()
		
		# 7
		kwargs = dict(
				label_options=dict(color=(1,1,1,1), bold=False),
				background_color=(0,0,0,1),
				tick_color=(1,1,1,1),
				border_color=(1,1,1,1),
				padding=2,
				xlabel='On Time (Seconds):',
				ylabel='Temperature',
				x_ticks_minor=2,
				x_ticks_major=10,
				y_ticks_minor=2,
				y_ticks_major=10,
				y_grid_label=False,
				x_grid_label=False,
				xlog=False,
				ylog=False,
				x_grid=False,
				y_grid=False,
				ymin=0,
				ymax=170,
				# 8
				xmin= int(self.getCurrentTime()*TIME_DECIMALS)/TIME_DECIMALS,
				xmax= int((self.getCurrentTime() + START_SIZE_WINDOW)*TIME_DECIMALS)/TIME_DECIMALS
				)
		# 7
		super(PlotterWidget, self).__init__(**kwargs)
		
		# 8
		self.SPplot = LinePlot(color=(1,0,0,1))
		self.add_plot(self.SPplot)
		self.PVplot = LinePlot(color=(0,1,0,1))
		self.add_plot(self.PVplot)
		
	# 8; At dt update the plot
	def update(self, dt):
		self.addPlott()
		if self.startScrolling() == True:
			self.scrollXaxis()		  	# Commence scrolling axis.
			self.cutLinesNotInWindow()  # Remove data not seen from array. Smoothes the graphics
	
	# 8; Get current run time by subtracting start time
	def getCurrentTime(self):
		# Obtains time stamp as an float from epoch (1/1/1970)
		ts = time.time()
		# Take start time away from the epoch time to min the label size. 
		ts = ts - self.startTime 
		return ts

	# 8; Add plots to the graph at current run time
	def addPlott(self):
		self.index = self.getCurrentTime()
		self.SPplot.points.append([self.index, self.currentSignal])
		self.SPplot.draw()
		self.PVplot.points.append([self.index, self.currentTemp])
		self.PVplot.draw()
		
	# 8; Returns a true value if the plot has reached the START_SCROLLING point on the window.
	def startScrolling(self):
		if self.index >= self.xmax - START_SCROLLING:
			return True
		else: return False
		
	# 8; Commences Scroll of xAxis
	def scrollXaxis(self):
		# Round time stamp to 2DP
		self.xmax=float((self.index+START_SCROLLING)*TIME_DECIMALS)/TIME_DECIMALS
		self.xmin=float((self.xmax-START_SIZE_WINDOW)*TIME_DECIMALS)/TIME_DECIMALS
	
	# 8; Remove lines that are no longer on the graph
	def cutLinesNotInWindow(self):
		del self.SPplot.points[0]
		del self.PVplot.points[0]
# 10
class readTemp():
	def readTempRaw(self):
		cat = subprocess.Popen(['cat',device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out,err = cat.communicate()
		out_decode = out.decode('utf-8')
		lines = out_decode.split('\n')
		return lines
	def read_temp(self):
		lines = self.readTempRaw()
		while lines[0].strip()[-3:] != 'YES':
			time.sleep(0.2)
			lines = self.readTempRaw()
		equalsPos = lines[1].find('t=')
		if equalsPos != -1:
			tempString = lines[1][equalsPos+2:]
			temp_c = float(tempString) / 1000.0
			return temp_c
# 12
class PIDcontroller(FloatLayout):
	error 			= ObjectProperty(0)
	lastError 		= ObjectProperty(0)
	integralTot		= ObjectProperty(0)
	SP 				= ObjectProperty(0)
	PV			 	= ObjectProperty(0)
	tempClass 		= ObjectProperty(0)
	PID 			= ObjectProperty(0)
	def __init__(self, **kwargs):
		super(FloatLayout, self).__init__(**kwargs)
		GPIO.output(23, 0)
		self.error = 0
		self.lastError = 0
		self.SP = 105
		self.PID = 0
		self.tempClass = readTemp()
	# This needs to be multi-threaded. 
	# Currently is not and will be laggy until multi-threaded.
	# Incorporating a daemon thread will be covered in the next tut.
	def updatePID(self, dt):
		# PID coefficient 
		Kp = 1
		Ki = 0
		Kd = 25
		dt = 0.0

		ts = int(time.time()*1000)/1000
			
		self.PV = self.tempClass.read_temp()
		time.sleep(1)

		if self.PV < self.SP:
			self.error = self.SP - self.PV
			dt = (int(time.time()*1000)/1000) - ts
			self.integralTot = self.integralTot + self.error*dt
			diff = (self.error - self.lastError)/dt
			self.PID = Kp*self.error + Ki*self.integralTot + Kd*diff
			self.PWM(self.PID, self.SP, self.PV)
			self.lastError = self.error
		else:
			self.integralTot = 0
			self.turnOff()

	def PWM(self, PID, SP, PV):
		# if steam is pressed just heat up to SP as fast as possible.
		if SP != STEAM_TEMP_SP:
			if PID > 0:
				roomTemp = 20
				pwmDuty = ((SP-roomTemp)-(PV-roomTemp))/(SP-roomTemp)+0.5
				#Turn On
				self.turnOff()
				self.turnOn()
				time.sleep(pwmDuty)
				self.turnOff()
				#if less than 0: means already 100% duty.
				if pwmDuty < 1.0:
					time.sleep(1-pwmDuty)
				else:
					#turn Off
					self.turnOff()
		else: self.turnOn()
	def turnOn(self):
		#Turn On
		GPIO.output(23, 1)
	def turnOff(self):
		#Turn Off
		GPIO.output(23, 0)
# 1
class CoffeeApp(App):
	
	SP = NumericProperty(105)
	# 3
	def coffeePress_callback(self, *args):		# 3
		print "coffee has been pressed"			# 3
		GPIO.output(20, 1)						# 5
	def coffeeRelease_callback(self, *args):	# 3
		print "coffee has been released\n"		# 3
		GPIO.output(20, 0)						# 5
	def steamPress_callback(self, *args):		# Not defined in tut
		print "steam has been pressed"			# Not defined in tut
		self.SP = STEAM_TEMP_SP
	def steamRelease_callback(self, *args):		# Not defined in tut
		print "steam has been released\n",		# Not defined in tut
		self.SP = 105
	def waterPress_callback(self, *args):		# Not defined in tut
		print "water has been pressed"			# Not defined in tut
		GPIO.output(19, 1)						# 6
	def waterRelease_callback(self, *args):		# Not defined in tut
		print "water has been released\n"		# Not defined in tut
		GPIO.output(19, 0)						# 6

	def build(self): # 1
		root = BoxLayout(orientation='horizontal') # 1
		verticalBtns = BoxLayout(orientation='vertical', size_hint_x = 0.25) # 1
		PID = PIDcontroller()	# 12
		plotter = PlotterWidget()	# 7
		Clock.schedule_interval(plotter.update, SAMPLE_RATE)	# 8
		
		# 1 adding our buttons to the interface
		coffeeButton = Button(text='coffee') 	# 2
		steamButton = Button(text='steam') 		# Not defined in tut
		waterButton = Button(text='water') 		# Not defined in tut
				
		# 3
		coffeeButton.bind(on_press=self.coffeePress_callback)		# 3
		coffeeButton.bind(on_release=self.coffeeRelease_callback)	# 3
		steamButton.bind(on_press=self.steamPress_callback)			# Not defined in tut
		steamButton.bind(on_release=self.steamRelease_callback)		# Not defined in tut
		waterButton.bind(on_press=self.waterPress_callback)			# Not defined in tut
		waterButton.bind(on_release=self.waterRelease_callback)		# Not defined in tut
		
		# 9; Link up SP from steam button to the currentSignal on plotter object.
		self.bind(SP=plotter.setter('currentSignal'))
		# 12; Link up the temperature read the PID thread and set currentTemp from this.
		# Uncomment to activate Controller. 
		# Will need daemon thread to stop lag once activated. Won't cover this, in this tut.
		#Clock.schedule_interval(PID.updatePID, SAMPLE_RATE)
		#PID.bind(PV = plotter.setter('currentTemp'))
		
		# 1 Add to the RootWidget child widgets:
		root.add_widget(plotter)				# 7
		verticalBtns.add_widget(coffeeButton) 	# 2
		verticalBtns.add_widget(steamButton) 	# Not defined in tut
		verticalBtns.add_widget(waterButton) 	# Not defined in tut
		root.add_widget(verticalBtns)			# 2
		return root # 1

if __name__=='__main__': # 1
	CoffeeApp().run() # 1
	
	