from kivy.config import Config
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 600)

from kivy.app import App

from speedmeter import SpeedMeter

class SpeedMeterExample2(App): pass

SpeedMeterExample2().run()
