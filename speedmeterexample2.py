from kivy.config import Config
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 650)
Config.set('input', 'mouse', 'mouse,multitouch_on_demand')

from kivy.app import App
from kivy.factory import Factory
from kivy.properties import *

from speedmeter import SpeedMeter

class SpeedMeterExample2(App):

    currentColor = StringProperty('')

    def on_start(self):
        self.sm = self.root.ids['sm']
        self.sm.bind(on_touch_down=self._touch_down)

    def _setVectorColor(self, hex_color):
        sm = self.sm
        if not sm.sectors:
            sm.sectors = [sm.min]
        if self.lastPick <= sm.sectors[-1]: return
        sm.sectors = sm.sectors + [hex_color, self.lastPick]
        self.root.ids['sectorWidth'].disabled = False

    def _setCadranColor(self, hex_color):
        self.sm.cadranColor = hex_color

    def _touch_down(self, sm, motionEvent):
        if motionEvent.button == 'left':
            v = sm.getValue(motionEvent.pos)
            if v is None: return
            sm.value = v
        else:
            self.lastPick = sm.getValue(motionEvent.pos)
            if self.sm.sectors and self.lastPick <= self.sm.sectors[-1]: return
            self.colorPicker = Factory.ColorPickerDialog()
            self.colorPicker._exampleCallback = self._setVectorColor
            self.colorPicker.open()

    def setLabelControlState(self):
        w = self.root.ids
        w['labelIconScale'].disabled = not self.sm.labelIcon
        sm = self.sm
        disabled = not sm.label and not sm.labelIcon
        w['labelRadiusRatio'].disabled = disabled
        w['labelAngleRatio'].disabled = disabled

SpeedMeterExample2().run()
