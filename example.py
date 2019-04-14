from kivy.app import App
from kivy.lang import Builder

from speedmeter import SpeedMeter

class SpeedMeterExample(App):

    def build(self):
        return Builder.load_file('example.kv')

example = SpeedMeterExample()
example.run()
