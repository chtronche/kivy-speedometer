# SpeedMeter widget for Kivy
# Inspired by Andrea Gavana's SpeedMeter for wxPython
# 
# MIT License (see MIT-LICENSE.TXT file, basically no warranty of any kind,
# use it as you want for any purpose, commercial or not)
# Copyright Ch. Tronche 2019, ch@tronche.com

import sys

from math import atan2, cos, pi, radians, sin

from kivy.core.text import Label
from kivy.graphics import *
from kivy.properties import *
from kivy.uix.image import CoreImage, Image
from kivy.uix.widget import Widget
from kivy.utils import get_color_from_hex

_redraw = 'pos size min max tick subtick cadranColor displayFirst displayLast sectors'.split()
_redrawLabel = 'label labelRadiusRatio labelAngleRatio labelIcon labelIconScale'.split()

from kivy.graphics.instructions import *

_n = 0
def _toto(*t, **k):
    global _n
    #print 'toto>>', _n
    _n += 1

_2pi = 2 * pi # I trust multiplication by 2 even for floating points !
_halfPi = pi / 2

class SpeedMeter(Widget):

    min = NumericProperty(0)
    max = NumericProperty(100)
    
    tick = NumericProperty(10)
    subtick = NumericProperty(0)

    displayFirst = BooleanProperty(True)
    displayLast = BooleanProperty(True)

    startAngle = NumericProperty(-90, min=-360,max=360)
    endAngle = NumericProperty(135, min=-360,max=360)

    cadranColor = StringProperty('#ffffff')
    cadranThickness = NumericProperty

    label = StringProperty('')
    labelIcon = StringProperty('')
    labelIconScale = NumericProperty(0.5, min=0, max=1)

    labelRadiusRatio = NumericProperty(0.3, min=-1, max=1)
    labelAngleRatio = NumericProperty(0.5, min=0, max=1)

    needleColor = StringProperty('#6bf2ff')
    needleImage = StringProperty('needle.png')

    sectors = ListProperty()

    value = NumericProperty(0)

    def __init__(self, **kwargs):
        super(SpeedMeter, self).__init__(**kwargs)
        self.a = self.b = self.r2 = 0 # In case on_value is called before _update
        self.rotate = _X
        self._labelRectangle = -1
        self.extendedTouch = False
        bind = self.bind
        _draw = self._draw
        for eventList, fn in ((_redraw, self._draw), (_redrawLabel, self._drawLabel)):
            for event in eventList:
                bind(**{ event: fn })
            
    def valueStr(self, n):
        # Override this if you want more control on the tick display
        return str(int(n))

    def _drawSectors(self, centerx, centery, r):
        l = self.sectors[:]
        if not l: return
        d = r + r
        a = self.a
        b = self.b
        v0 = l.pop(0)
        a0 = -(a * v0 + b)
        while l:
            color = l.pop(0)
            v1 = l.pop(0) if l else self.max
            a1 = -(a * v1 + b)
            Color(rgba=get_color_from_hex(color))
            Ellipse(pos=(centerx-r, centery-r), size=(d, d), angle_start=a0, angle_end=a1)
            a0 = a1

    # I'm using theta for the angle, as to not confuse it with transparency (alpha as in in rgba)
    def _drawValues(self, centerx, centery, r, theta0, theta1):
        valueStr = self.valueStr
        values = [Label(valueStr(i), bold=True)
                      for i in xrange(self.min, self.max + 1, self.tick)]
        if len(values) <= 1:
            # Tick is bigger than max - min
            return
        for _ in values: _.refresh()

        deltaTheta = radians((theta1 - theta0) / float(len(values) - 1))
        theta = radians(theta0)
        r_10 = r - 10
        r_20 = r - 20
        subtick = int(self.subtick)
        if subtick:
            subDeltaTheta = deltaTheta / subtick
        else:
            subDeltaTheta = None
        for value in values:
            first = value is values[0]
            last = value is values[-1]
            c = cos(theta)
            s = sin(theta)
            r_1 = r - 1
            if not first and not last or first and self.displayFirst or last and self.displayLast:
                # Draw the big tick
                Line(points=(
                    centerx + r_1 * s, centery + r_1 * c,
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
            if subDeltaTheta and not last:
                subTheta = theta + subDeltaTheta
                for n in xrange(subtick):
                    subc = cos(subTheta)
                    subs = sin(subTheta)
                    Line(points=(
                        centerx + r * subs, centery + r * subc,
                        centerx + r_10 * subs, centery + r_10 * subc),
                             width=0.75)
                    subTheta += subDeltaTheta
            theta += deltaTheta

    def _drawNeedle(self, centerx, centery, r):
        Color(rgba=get_color_from_hex(self.needleColor))
        if self.value < self.min: self.value = self.min
        elif self.value > self.max: self.value = self.max
        self.on_value()
        needleSize = r
        s = needleSize * 2
        Rectangle(pos=(centerx - needleSize, centery - needleSize), size=(s, s),
                      source='needle.png')
        
    def _drawLabel(self, *t):
        self.canvas.clear()
        if not self.label and not self.labelIcon:
            return
        theta = self.startAngle + self.labelAngleRatio * (self.endAngle - self.startAngle)
        c = cos(radians(theta))
        s = sin(radians(theta))
        x, y = self.pos
        width, height = self.size
        centerx = x + width / 2
        centery = y + height / 2
        r = min(width, height) / 2
        r1 = r * self.labelRadiusRatio
        if self.labelIcon:
            label = CoreImage(self.labelIcon)
            t = label.texture
            iconSize = max(t.size)
            scale = r * self.labelIconScale / float(iconSize)
            tw, th = t.size
            tw *= scale
            th *= scale
        else:
            label = Label(text=self.label, markup=True)
            label.refresh()
            t = label.texture
            tw, th = t.size
        self.canvas.clear()
        self.canvas.add(Rectangle(
            pos=(centerx + r1 * s - tw/2, centery + r1 * c - th/2), size=(tw, th),
            texture=t))

    def _draw(self, *args):
        d = min(self.size)
        sa = self.startAngle
        se = self.endAngle
        
        self.canvas.before.clear()
        self.canvas.after.clear()
        with self.canvas.before:
            Callback(_toto)
            r = d / 2
            self.r2 = r * r
            x, y = self.pos
            width, height = self.size
            centerx = x + width / 2
            centery = y + height / 2
            theta0 = theta0_ = float(sa)
            theta1 = theta1_ = float(se)
            
            width = 1.5

            self._drawSectors(centerx, centery, r)
            Color(rgba=get_color_from_hex(self.cadranColor))
            _drawOuterCadran(centerx, centery, r, theta0, theta1, width)

            if sa == se:
                theta1 = theta1_ = theta0 + 360
            self._drawValues(centerx, centery, r, theta0, theta1)
            
        with self.canvas:
            self._drawLabel()

            #
            # Needle (compute parameters and draw)
            #
            self.a = (theta0_ - theta1_) / (self.max - self.min)
            self.b = -theta0_ - self.a * self.min

            #
            # Reverse mapping
            #
            self.startTheta = _halfPi - radians(self.startAngle)
            self.endTheta = _halfPi - radians(self.endAngle)
            self.direct = self.startTheta < self.endTheta

            self.ra = (self.max - self.min) / ((self.endTheta - self.startTheta) 
                                               if sa != se else _2pi)
            self.rb = self.min - self.ra * self.startTheta
            
        with self.canvas.after:
            PushMatrix()
            self.rotate = Rotate(origin=(centerx, centery))
            self._drawNeedle(centerx, centery, r)
            PopMatrix()

    def on_value(self, *t):
        self.rotate.angle = self.a * self.value + self.b

    def getValue(self, pos):
        c = self.center
        x = pos[0] - c[0]
        y = pos[1] - c[1]
        r2 = x * x + y * y
        if r2 > self.r2: return
        theta = atan2(y, x)
        theta_ = theta

        min_, max_ = (self.startTheta, self.endTheta) if self.direct else (self.endTheta, self.startTheta)
        if theta < min_: theta += _2pi
        elif theta > max_: theta -= _2pi
            
        v = self.ra * theta + self.rb
        if v >= self.min and v <= self.max: return v
        if not self.extendedTouch: return
        # Should make distinction between min and max here
        
    def collide_point(self, x, y):
        return self.getValueFromEV(*(x, y)) is not None

    def on_startAngle(self, *t):
        if self.endAngle - self.startAngle > 360:
            self.startAngle = self.endAngle - 360
        self._draw()

    def on_endAngle(self, *t):
        if self.endAngle - self.startAngle > 360:
            self.endAngle = self.startAngle + 360
        self._draw()

class _X: pass

def _drawOuterCadran(centerx, centery, r, theta0, theta1, width):
    if theta0 == theta1:
        Line(circle=(centerx, centery, r), width=width)
    else:
        rt0 = radians(theta0)
        rt1 = radians(theta1)
        Line(points=(
            centerx + r * sin(rt0),
            centery + r * cos(rt0),
            centerx, centery,
            centerx + r * sin(rt1),
            centery + r * cos(rt1),
            ),
            width=width,
                 )
        Line(circle=(centerx, centery, r, theta0, theta1), width=width)
