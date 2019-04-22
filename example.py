from kivy.app import App
from kivy.clock import Clock
from kivy.lang import Builder

from speedmeter import SpeedMeter

class SpeedMeterExample(App):

    def tick(self, *t, **kw):
        ids = self.root.ids
        sList = (ids.speed, ids.clock, ids.fuel, ids.temperature, ids.rpm, ids.pi)
        for s in sList:
            if s != ids.speed:
                s.value += 0.2
                if s.value >= s.max - 0.001: s.value = s.min

example = SpeedMeterExample()
Clock.schedule_interval(example.tick, 0.5)
example.run()
