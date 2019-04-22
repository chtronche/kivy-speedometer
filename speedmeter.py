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

class SpeedMeter(Widget):

    min = NumericProperty(0)
    tick = NumericProperty(10)
    max = NumericProperty(100)
    value = NumericProperty(0)
    startAngle = NumericProperty(-110, min=-360,max=360)
    endAngle = NumericProperty(140, min=-360,max=360)
    subtick = NumericProperty(0)
    label = StringProperty('')
    displayFirst = BooleanProperty(True)
    displayLast = BooleanProperty(True)

    def __init__(self, **kwargs):
        super(SpeedMeter, self).__init__(**kwargs)
        self.a = self.b = 0 # In case on_value is called before _update
        self.rotate = _X
        self.bind(pos=self._update, size=self._update)

    def labelStr(self, n):
        # Override this if you want more control on the tick display
        return str(int(n))

    def _update(self, *args):
        d = min(self.size)
        
        labelStr = self.labelStr
        self.labels = [Label(labelStr(i), bold=True)
                           for i in xrange(self.min, self.max + 1, self.tick)]
        for _ in self.labels: _.refresh()
        
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
            #
            # Draw outer cadran
            #
            if alpha0 == alpha1:
                Line(circle=(centerx, centery, r), width=width)
                alpha1 = alpha1_ = alpha0 + 360
            else:
                ra0 = radians(alpha0 + 90)
                ra1 = radians(alpha1 + 90)
                Line(points=(
                    centerx - r * cos(ra0),
                    centery + r * sin(ra0),
                    centerx, centery,
                    centerx - r * cos(ra1),
                    centery + r * sin(ra1),
                    ),
                    width=width,
                        )
                Line(circle=(centerx, centery, r, alpha0, alpha1), width=width)

            #
            # Draw labels
            #
            # For some reason Line(circle=) is rotated 90 degrees ???
            alpha0 += 90
            alpha1 += 90
            deltaAlpha = radians((alpha1 - alpha0) / float(len(self.labels) - 1))
            alpha = radians(alpha0)
            r_10 = r - 10
            r_20 = r - 20
            subtick = int(self.subtick)
            if subtick:
                subDeltaAlpha = deltaAlpha / subtick
            else:
                subDeltaAlpha = None
            for label in self.labels:
                first = label is self.labels[0]
                last = label is self.labels[-1]
                c = cos(alpha)
                s = sin(alpha)
                if not first and not last or first and self.displayFirst or last and self.displayLast:
                    # Draw the big tick
                    Line(points=(
                        centerx - r * c, centery + r * s,
                        centerx - r_10 * c, centery + r_10 * s,
                        ),
                        width=2)
                    # Numerical value
                    t = label.texture
                    tw, th = t.size
                    tw /= 2
                    th /= 2
                    Rectangle(
                        pos=(centerx - r_20 * c - tw, centery + r_20 * s - th),
                        size=t.size,
                        texture=t)
                # Subtick
                if subDeltaAlpha and not last:
                    subAlpha = alpha + subDeltaAlpha
                    for n in xrange(subtick):
                        subc = cos(subAlpha)
                        subs = sin(subAlpha)
                        Line(points=(
                            centerx - r * subc, centery + r * subs,
                            centerx - r_10 * subc, centery + r_10 * subs))
                        subAlpha += subDeltaAlpha
                alpha += deltaAlpha

            #
            # Needle (compute parameters and draw)
            #
            self.a = (alpha0_ - alpha1_) / (self.max - self.min)
            self.b = -alpha0_ - self.a * self.min
            Color(0,0,1)
            PushMatrix()
            if self.value < self.min: self.value = self.min
            elif self.value > self.max: self.value = self.max
            self.rotate = Rotate(origin=(centerx, centery))
            self.on_value()
            needleSize = r
            s = needleSize * 2
            Rectangle(pos=(centerx - needleSize, centery - needleSize), size=(s, s), source='needle.png')
            PopMatrix()

    def on_value(self, *t):
        self.rotate.angle = self.a * self.value + self.b
