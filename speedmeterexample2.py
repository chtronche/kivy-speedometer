from kivy.config import Config
Config.set('graphics', 'width', 1000)
Config.set('graphics', 'height', 600)

from kivy.app import App

from speedmeter import SpeedMeter

class SpeedMeterExample2(App):

    def on_start(self):
        self.root.ids['sm'].bind(on_touch_down=self._touch_down)

    def _touch_down(self, sm, motionEvent):
        if motionEvent.is_double_tap:
            pass
        else:
            v = sm.getValue(motionEvent.pos)
            if v is None: return
            sm.value = v

SpeedMeterExample2().run()
