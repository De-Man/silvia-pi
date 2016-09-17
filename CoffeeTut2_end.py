# !/usr/bin/kivy
##======================================================================================
# #	This program is free software: you can redistribute it and/or modify
# #	it under the terms of the GNU General Public License as published by
# #	the Free Software Foundation, either version 3 of the License, or
# #	(at your option) any later version.
# #
# #	This program is distributed in the hope that it will be useful,
# #	but WITHOUT ANY WARRANTY; without even the implied warranty of
# #	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# #	GNU General Public License for more details.
# #
# #	You should have received a copy of the GNU General Public License
# #	along with this program.  If not, see <http://www.gnu.org/licenses/>.
##======================================================================================
##======================================================================================
# # You will notice: 
# #
# # 1. "# From Tutorial XX" in the comments, this means this code was explained
# # in the prior LXF tutorial and will not be covered in this tutorial. Also note that all
# # sequence numbering from the previous tutorials have been removed.
# #
# # 2. "# No.'s" in the comments, these comments are there to signify the
# # order of when the code was referenced in the tutorial. 
# # "# Not defined in tut" means I did not explicitly sate the code within the tutorial
# # instead I would have said for example "repeat code for the other buttons"
# #
##======================================================================================
# Size of 7" RPi Screen
# Set windows properties before creating the window.
import kivy
from kivy.config import Config
Config.set('graphics', 'width', '837')
Config.set('graphics', 'height', '464')
Config.set('graphics', 'resizable', '0')
Config.set('graphics', 'show_cursor', '1')
kivy.require('1.9.1')
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.floatlayout import FloatLayout
from kivy.garden.graph import Graph, LinePlot
from kivy.properties import NumericProperty, ObjectProperty, StringProperty		# 2
from kivy.clock import Clock
import datetime, time

from kivy.graphics import Rectangle				# Tutorial 2 step 1
from kivy.uix.image import Image				# Tutorial 2 step 2
from kivy.uix.behaviors import ButtonBehavior	# Tutorial 2 step 2
from kivy.uix.scatter import Scatter			# Tutorial 2 step 2
from kivy.uix.label import Label				# Tutorial 2 Step 4
from kivy.uix.popup import Popup				# Tutorial 2 step 5, BUT not explicitly referenced
import subprocess								# Tutorial 2 step 5, BUT not explicitly referenced

# From Tutorial 1
# import RPi.GPIO as GPIO            # Import RPi GPIO module
# GPIO.setmode(GPIO.BCM)             # BCM or BOARD
# GPIO.setup(20, GPIO.OUT)           # GPIO20 Coffee Button output
# GPIO.setup(23, GPIO.OUT)           # GPIO23 Boiler output
# GPIO.setup(19, GPIO.OUT)           # GPIO19 Water Button output

# From Tutorial 1
SAMPLE_RATE 		= 1  	# Seconds
TIME_DECIMALS 		= 100  	# used for rounding
START_SCROLLING 	= 150  	# (Sec) [time before starting to scroll] = START_SIZE_WINDOW - START_SCROLLING  
START_SIZE_WINDOW 	= 220  	# (Sec) time of X axis 

# From Tutorial 1
# import os, glob, subprocess
# os.system('modprobe w1-gpio')
# os.system('modprobe w1-therm')
# base_dir = '/sys/bus/w1/devices/'
# device_folder = glob.glob(base_dir + '3b-000000191766')[0]
# device_file = device_folder + '/w1_slave'

STEAM_TEMP_SP = 140  	# From Tutorial 1
COFFEE_TEMP_SP = 105	# Not defined in tut

class PlotterWidget(Graph):  # From Tutorial 1
	# From Tutorial 1
	SPplot = ObjectProperty(None)  # Set Point, will either be 105 or 140
	PVplot = ObjectProperty(None)  # Process Value, will be temperature
	
	# From Tutorial 1
	index = 	ObjectProperty(0)  # Time
	startTime = ObjectProperty(0)
	currentTemp = ObjectProperty(23)
	currentSignal = ObjectProperty(105)
	
	def __init__(self, **kwargs):
		# From Tutorial 1
		self.startTime = self.getCurrentTime()
		
		# From Tutorial 1
		kwargs = dict(
				label_options=dict(color=(0, 0, 0, 0), bold=False),
				background_color=(0, 0, 0, 0),  	# Tutorial 2 step 1
				tick_color=(0, 0, 0, 0),  			# Tutorial 2 step 1
				border_color=(0, 0, 0, 0),  		# Tutorial 2 step 1
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
				# From Tutorial 1
				xmin=int(self.getCurrentTime() * TIME_DECIMALS) / TIME_DECIMALS,
				xmax=int((self.getCurrentTime() + START_SIZE_WINDOW) * TIME_DECIMALS) / TIME_DECIMALS
				)
		# From Tutorial 1
		super(PlotterWidget, self).__init__(**kwargs)
		
		# From Tutorial 1
		self.SPplot = LinePlot(color=(1, 0, 0, 1))
		self.add_plot(self.SPplot)
		self.PVplot = LinePlot(color=(0, 1, 0, 1))
		self.add_plot(self.PVplot)
		
	# From Tutorial 1; At dt update the plot
	def update(self, dt):
		
		self.addPlott()
		if self.startScrolling() == True:
			self.scrollXaxis()  # Commence scrolling axis.
			self.cutLinesNotInWindow()  # Remove data not seen from array. Smoothes the graphics
	
	# From Tutorial 1; Get current run time by subtracting start time
	def getCurrentTime(self):
		# Obtains time stamp as an float from epoch (1/1/1970)
		ts = time.time()
		# Take start time away from the epoch time to min the label size. 
		ts = ts - self.startTime 
		return ts

	# From Tutorial 1; Add plots to the graph at current run time
	def addPlott(self):
		self.index = self.getCurrentTime()
		self.SPplot.points.append([self.index, self.currentSignal])
		self.SPplot.draw()
		self.PVplot.points.append([self.index, self.currentTemp])
		self.PVplot.draw()
		
	# From Tutorial 1; Returns a true value if the plot has reached the START_SCROLLING point on the window.
	def startScrolling(self):
		if self.index >= self.xmax - START_SCROLLING:
			return True
		else: return False
		
	# From Tutorial 1; Commences Scroll of xAxis
	def scrollXaxis(self):
		# Round time stamp to 2DP
		self.xmax = float((self.index + START_SCROLLING) * TIME_DECIMALS) / TIME_DECIMALS
		self.xmin = float((self.xmax - START_SIZE_WINDOW) * TIME_DECIMALS) / TIME_DECIMALS
	
	# From Tutorial 1; Remove lines that are no longer on the graph
	def cutLinesNotInWindow(self):
		del self.SPplot.points[0]
		del self.PVplot.points[0]
# From Tutorial 1
class readTemp():
	def readTempRaw(self):
		cat = subprocess.Popen(['cat', device_file], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
		out, err = cat.communicate()
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
			tempString = lines[1][equalsPos + 2:]
			temp_c = float(tempString) / 1000.0
			return temp_c
# From Tutorial 1
class PIDcontroller(FloatLayout):
	error 			 = ObjectProperty(0)
	lastError 		 = ObjectProperty(0)
	integralTot		 = ObjectProperty(0)
	SP 				 = ObjectProperty(0)
	PV			 	 = ObjectProperty(0)
	tempClass 		 = ObjectProperty(0)
	PID 			 = ObjectProperty(0)
	def __init__(self, **kwargs):
		super(FloatLayout, self).__init__(**kwargs)
		# GPIO.output(23, 0)
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

		ts = int(time.time() * 1000) / 1000
			
		self.PV = self.tempClass.read_temp()
		time.sleep(1)

		if self.PV < self.SP:
			self.error = self.SP - self.PV
			dt = (int(time.time() * 1000) / 1000) - ts
			self.integralTot = self.integralTot + self.error * dt
			diff = (self.error - self.lastError) / dt
			self.PID = Kp * self.error + Ki * self.integralTot + Kd * diff
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
				pwmDuty = ((SP - roomTemp) - (PV - roomTemp)) / (SP - roomTemp) + 0.5
				# Turn On
				self.turnOff()
				self.turnOn()
				time.sleep(pwmDuty)
				self.turnOff()
				# if less than 0: means already 100% duty.
				if pwmDuty < 1.0:
					time.sleep(1 - pwmDuty)
				else:
					# turn Off
					self.turnOff()
		else: self.turnOn()
	def turnOn(self):
		# Turn On
		# GPIO.output(23, 1)
		pass
	def turnOff(self):
		# Turn Off
		# GPIO.output(23, 0)
		pass

# Tutorial 2 step 2
class CustomButton(ButtonBehavior, Image):
	depressed = StringProperty('')
	pressed = StringProperty('')
	SP = ObjectProperty(0)

	def __init__(self, **kwargs):
		super(CustomButton, self).__init__(**kwargs)

	# Used for buttons that need to stay pressed until touched again.
	def onhold_callback(self, imagePath):
		if self.source == self.pressed:
			self.source = self.depressed
			# Depressed steam therefore default back to coffee temp
			if self.source == 'SteamButtonDE.png':
				self.SP = COFFEE_TEMP_SP
		else:
			self.source = self.pressed
			# Steam temp will always overwrite coffee temp. Coffee temp is default.
			if self.source == 'SteamButtonPR.png':
				self.SP = STEAM_TEMP_SP
			else:
				self.SP = COFFEE_TEMP_SP
				
	# Tutorial 2 step 5, BUT not explicitly referenced
	def onpress_callback(self, imagePath):
		self.source = self.pressed
		if self.source == 'PowerButtonPR.png':
			self.popUpWindow()
			
	# Tutorial 2 step 5, BUT not explicitly referenced
	def onrelease_callback(self, imagePath):
		self.source = self.depressed

	# Tutorial 2 step 5
	def popUpWindow(self):
		popup = Popup(title='Tap outside window to cancel',
					  size_hint=(None, None), size=(250, 200))
		layout = BoxLayout(orientation='vertical')
		ShutDown = Button(text='Shut down')
		Restart = Button(text='Restart')
		# Add buttons to the boxlayout
		layout.add_widget(ShutDown)
		layout.add_widget(Restart)
		# Popups can only use one widget
		popup.add_widget(layout)
		# Bind the new buttons when activated.
		ShutDown.bind(on_release=powerShutDown)
		Restart.bind(on_release=powerRestart)
		#open the pop-up
		popup.open()

# Tutorial 2 step 5: Power Options
def powerShutDown(self):
	command = "/usr/bin/sudo /sbin/shutdown -hP now"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
# Tutorial 2 step 5: Power Options
def powerRestart(self):
	command = "/usr/bin/sudo /sbin/shutdown -r now"
	process = subprocess.Popen(command.split(), stdout=subprocess.PIPE)
	output = process.communicate()[0]
	
# Tutorial 2 step 4
class CustomLabel(Label):
	currentTempLabel = ObjectProperty(0)
	#at dt update
	def update(self, dt):
		rounded = int(self.currentTempLabel*100)/100
		self.text = str(rounded) + ' c'
	
# From Tutorial 1
class CoffeeApp(App):

	# Tutorial 2 step 1
	def _update_rect(self, instance, value):
		self.rect.pos = instance.pos
		self.rect.size = instance.size					

	def build(self):  # From Tutorial 1
		# Tutorial 2 step 3
		root = FloatLayout()
		
		# Tutorial 2 step 1
		# this ensures on size and position changes the background changes accordingly
		root.bind(size=self._update_rect, pos=self._update_rect)	
		# this ensures on build of the app the backgound is initiated 'before' anything else
		with root.canvas.before:
			self.rect = Rectangle(size=root.size, pos=root.pos, source='Background.png')
			
		# From Tutorial 1
		PID = PIDcontroller()
		plotter = PlotterWidget()
		Clock.schedule_interval(plotter.update, SAMPLE_RATE)

		# Tutorial 2 step 2
		#Coffee button setup
		DE = 'CoffeeButtonDE.png'
		PR = 'CoffeeButtonPR.png'
		coffeeButton = CustomButton(source=DE, size_hint=(None, None), size=(151, 151)) #Get the pixel info off the native file for best precision.
		#Scatter works better for rotating buttons than rotate does. 
		coffeeButtonSc = Scatter()
		coffeeButton.depressed = DE
		coffeeButton.pressed = PR
		coffeeButton.bind(on_release=coffeeButton.onhold_callback)
		coffeeButtonSc.add_widget(coffeeButton)
		#Steam button setup
		DE = 'SteamButtonDE.png'
		PR = 'SteamButtonPR.png'
		steamButton = CustomButton(source=DE, size_hint=(None, None), size=(151, 151)) #Get the pixel info off the native file for best precision.
		#Scatter works better for rotating buttons than rotate does. 
		steamButtonSc = Scatter()
		steamButton.depressed = DE
		steamButton.pressed = PR
		steamButton.bind(on_release=steamButton.onhold_callback)
		steamButtonSc.add_widget(steamButton)
		#Water button setup
		DE = 'WaterButtonDE.png'
		PR = 'WaterButtonPR.png'
		waterButton = CustomButton(source=DE, size_hint=(None, None), size=(151, 151)) #Get the pixel info off the native file for best precision.
		#Scatter works better for rotating buttons than rotate does. 
		waterButtonSc = Scatter()
		waterButton.depressed = DE
		waterButton.pressed = PR
		waterButton.bind(on_release=waterButton.onhold_callback)
		waterButtonSc.add_widget(waterButton)
		# Tutorial 2 step 4
		# Temperature Label
		TempLabel = CustomLabel(text='0'+' c', color=(0,0,0,1))
		TempLabel.y = -122 
		TempLabel.font_size = '30sp'
		TempLabel.texture_update()
		plotter.bind(currentTemp = TempLabel.setter('currentTempLabel'))
		Clock.schedule_interval(TempLabel.update, SAMPLE_RATE)
		# To force a change in temp to show the label bind is working. 
		# Comment out when hooked up to RTD
		plotter.currentTemp = 24
		
		# Tutorial 2 step 2 
		steamButton.bind(SP=plotter.setter('currentSignal'))		
		
		# From Tutorial 1; Link up the temperature read the PID thread and set currentTemp from this.
		# Uncomment to activate Controller. 
		# Will need daemon thread to stop lag once activated. Won't cover this, in this tut.
		# Clock.schedule_interval(PID.updatePID, SAMPLE_RATE)
		# PID.bind(PV = plotter.setter('currentTemp'))
		
		# Tutorial 2 step 5, BUT not explicitly referenced
		DE = 'PowerButtonDE.png'
		PR = 'PowerButtonPR.png'
		powerButton = CustomButton(source = DE, size_hint=(None, None), size = (65, 65), pos=(20,20))
		powerButton.depressed = DE
		powerButton.pressed = PR
		powerButton.bind(on_press=powerButton.onpress_callback)
		powerButton.bind(on_release=powerButton.onrelease_callback)

		# From Tutorial 1; Add to the RootWidget child widgets:
		root.add_widget(plotter)
		# Tutorial 2 step 2
		root.add_widget(coffeeButtonSc)
		root.add_widget(steamButtonSc)
		root.add_widget(waterButtonSc)
		# Tutorial 2 step 4
		root.add_widget(TempLabel)
		# Tutorial 2 step 5, BUT not explicitly referenced
		root.add_widget(powerButton)
		
		# Tutorial 2 step 5, BUT not explicitly referenced
		plotter.x = 75
		
		# Tutorial 2 step 3
		#Orientate buttons
		coffeeButtonSc.rotation = 45
		coffeeButtonSc.x = 620
		coffeeButtonSc.y = 210
		coffeeButtonSc.do_rotation = False
		coffeeButtonSc.do_scale = False
		coffeeButtonSc.do_translation = False
		waterButtonSc.rotation = 45
		waterButtonSc.x = 470
		waterButtonSc.y = 140
		waterButtonSc.do_rotation = False
		waterButtonSc.do_scale = False
		waterButtonSc.do_translation = False
		steamButtonSc.rotation = 45
		steamButtonSc.x = 579
		steamButtonSc.y = 31
		steamButtonSc.do_rotation = False
		steamButtonSc.do_scale = False
		steamButtonSc.do_translation = False
		
		return root
# From Tutorial 1
if __name__ == '__main__':
	CoffeeApp().run()
	
	
