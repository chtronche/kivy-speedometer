# SpeedMeter widget for Kivy
# Inspired by Andrea Gavana's SpeedMeter for wxPython
# 
# MIT License (see MIT-LICENSE.TXT file, basically no warranty of any kind,
# use it as you want for any purpose, commercial or not)
# Copyright Ch. Tronche 2019, ch@tronche.com
#

from kivy.core.text import Label
from kivy.graphics import *
from kivy.properties import *
from kivy.uix.image import Image
from kivy.uix.scatter import Scatter
from kivy.uix.widget import Widget
from math import cos, radians, sin

class _X: pass

def _drawOuterCadran(centerx, centery, r, alpha0, alpha1, width):
    if alpha0 == alpha1:
        Line(circle=(centerx, centery, r), width=width)
    else:
        ra0 = radians(alpha0)
        ra1 = radians(alpha1)
        Line(points=(
            centerx + r * sin(ra0),
            centery + r * cos(ra0),
            centerx, centery,
            centerx + r * sin(ra1),
            centery + r * cos(ra1),
            ),
            width=width,
                 )
        Line(circle=(centerx, centery, r, alpha0, alpha1), width=width)

class SpeedMeter(Widget):

    min = NumericProperty(0)
    max = NumericProperty(100)
    
    startAngle = NumericProperty(-90, min=-360,max=360)
    endAngle = NumericProperty(135, min=-360,max=360)

    tick = NumericProperty(10)
    subtick = NumericProperty(0)
    displayFirst = BooleanProperty(True)
    displayLast = BooleanProperty(True)

    label = StringProperty('')
    labelRadiusRatio = NumericProperty(0.3)
    labelAngleRatio = NumericProperty(0.5)

    value = NumericProperty(0)

    def __init__(self, **kwargs):
        super(SpeedMeter, self).__init__(**kwargs)
        self.a = self.b = 0 # In case on_value is called before _update
        self.rotate = _X
        self.bind(pos=self._draw, size=self._draw)

    def valueStr(self, n):
        # Override this if you want more control on the tick display
        return str(int(n))

    def _drawValues(self, centerx, centery, r, alpha0, alpha1):
        valueStr = self.valueStr
        values = [Label(valueStr(i), bold=True)
                      for i in xrange(self.min, self.max + 1, self.tick)]
        for _ in values: _.refresh()

        deltaAlpha = radians((alpha1 - alpha0) / float(len(values) - 1))
        alpha = radians(alpha0)
        r_10 = r - 10
        r_20 = r - 20
        subtick = int(self.subtick)
        if subtick:
            subDeltaAlpha = deltaAlpha / subtick
        else:
            subDeltaAlpha = None
        for value in values:
            first = value is values[0]
            last = value is values[-1]
            c = cos(alpha)
            s = sin(alpha)
            if not first and not last or first and self.displayFirst or last and self.displayLast:
                # Draw the big tick
                Line(points=(
                    centerx + r * s, centery + r * c,
                    centerx + r_10 * s, centery + r_10 * c,
                    ),
                    width=2)
                # Numerical value
                t = value.texture
                tw, th = t.size
                Rectangle(
                    pos=(centerx + r_20 * s - tw / 2, centery + r_20 * c - th / 2),
                    size=t.size,
                    texture=t)
            # Subtick
            if subDeltaAlpha and not last:
                subAlpha = alpha + subDeltaAlpha
                for n in xrange(subtick):
                    subc = cos(subAlpha)
                    subs = sin(subAlpha)
                    Line(points=(
                        centerx + r * subs, centery + r * subc,
                        centerx + r_10 * subs, centery + r_10 * subc))
                    subAlpha += subDeltaAlpha
            alpha += deltaAlpha

    def _drawNeedle(self, centerx, centery, r):
        Color(0,0,1)
        if self.value < self.min: self.value = self.min
        elif self.value > self.max: self.value = self.max
        self.on_value()
        needleSize = r
        s = needleSize * 2
        Rectangle(pos=(centerx - needleSize, centery - needleSize), size=(s, s),
                      source='needle.png')
        
    def _drawLabel(self, centerx, centery, r, alpha0, alpha1):
        if not self.label: return
        l = Label(self.label)
        l.refresh()
        t = l.texture
        tw, th = t.size
        alpha = self.startAngle + self.labelAngleRatio * (self.endAngle - self.startAngle)
        c = cos(radians(alpha))
        s = sin(radians(alpha))
        r *= self.labelRadiusRatio
        Rectangle(pos=(centerx + r * s - tw/2, centery + r * c - th/2), size=t.size, texture=t)

    def _draw(self, *args):
        d = min(self.size)
        
        self.canvas.clear()
        with self.canvas:
            Color(1,0,0)
            r = d / 2
            x, y = self.pos
            width, height = self.size
            centerx = x + width / 2
            centery = y + height / 2
            alpha0 = alpha0_ = float(self.startAngle)
            alpha1 = alpha1_ = float(self.endAngle)
            
            width = 1.5

            _drawOuterCadran(centerx, centery, r, alpha0, alpha1, width)

            if alpha0 == alpha1:
                alpha1 = alpha1_ = alpha0 + 360
            self._drawValues(centerx, centery, r, alpha0, alpha1)
            #
            # Needle (compute parameters and draw)
            #
            self.a = (alpha0_ - alpha1_) / (self.max - self.min)
            self.b = -alpha0_ - self.a * self.min
            
            PushMatrix()
            self.rotate = Rotate(origin=(centerx, centery))
            self._drawNeedle(centerx, centery, r)
            PopMatrix()

            self._drawLabel(centerx, centery, r, alpha0, alpha1)

    def on_value(self, *t):
        self.rotate.angle = self.a * self.value + self.b
