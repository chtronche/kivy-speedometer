from kivy.config import Config
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from math import exp

from kivy.app import App
from kivy.clock import Clock
from kivy.factory import Factory

from speedmeter import SpeedMeter

class NoValueSpeedMeter(SpeedMeter):

    def valueStr(self, n): return ''

class Demo1(App):

    def __init__(self):
        App.__init__(self)
        self.clockRunning = True

    def tick(self, *t, **kw):
        ids = self.root.ids

        if self.clockRunning:
            clock = ids.clock
            clock.value += 0.2
            if clock.value > clock.max - 0.001: clock.value = clock.min

        fuel = ids.fuel
        fuel.value -= 0.02 * ids.rpm.value
        if fuel.value < fuel.min: fuel.value = fuel.min

        speed_value = ids.speed_value
        if fuel.value <= fuel.min and speed_value.value > speed_value.min:
            speed_value.value = speed_value.value * 0.9 - 3
            if speed_value.value <= speed_value.min:
                speed_value.value = speed_value.min
                speed_value.disabled = True
        
    def set_speed(self):
        ids = self.root.ids
        fuel = ids.fuel
        ids.rpm.value = exp(ids.speed_value.value / 200.0) * 4.5 - 4.5

    def set_temp(self, temperature, motion):
        v = temperature.getValue(motion.pos)
        if not v: return
        temperature.value = v
        self.root.ids.temperature_display.text = '%.2f' % v

example = Demo1()
Clock.schedule_interval(example.tick, 0.5)
example.run()
