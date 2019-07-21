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

_redraw = tuple('pos size min max'.split())
_redraw_before = tuple('sectors sectorWidth shadowColor'.split())
_redraw_canvas = tuple('tick subtick cadranColor displayFirst displayLast'.split())
_redraw_after = tuple('label labelRadiusRatio labelAngleRatio labelIcon labelIconScale'.split())

from kivy.graphics.instructions import *

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
    sectorWidth = NumericProperty(0, min=0)
    thickness = NumericProperty(1.5, min=0)

    shadowColor = StringProperty('')

    value = NumericProperty(0)

    def __init__(self, **kwargs):
        super(SpeedMeter, self).__init__(**kwargs)
        # In case on_value is called before _update
        self.a = self.b = self.r2 = self.r = self.centerx = self.centery = 0
        self._shadow = None
        self.rotate = _X
        self._labelRectangle = -1

        self.extendedTouch = False
        bind = self.bind
        _draw = self._draw
        for eventList, fn in (
                (_redraw, self._draw), (_redraw_before, self._draw_before),
                (_redraw_canvas, self._draw_canvas), (_redraw_after, self._draw_after)):
            for event in eventList:
                bind(**{ event: fn })
            
    def valueStr(self, n):
        # Override this if you want more control on the tick display
        return str(int(n))

    def _drawSectors(self):
        l = self.sectors[:]
        if not l: return
        r = self.r
        centerx = self.centerx
        centery = self.centery
        d = r + r
        a = self.a
        b = self.b
        v0 = l.pop(0)
        a0 = -(a * v0 + b)
        sw = self.sectorWidth
        if sw:
            r -= sw
        else:
            centerx -= r
            centery -= r
            dd = (d, d)

        while l:
            color = l.pop(0)
            v1 = l.pop(0) if l else self.max
            a1 = -(a * v1 + b)
            Color(rgba=get_color_from_hex(color))
            if sw:
                Line(circle=(centerx, centery, r, a0, a1), width=sw, cap='none')
            else:
                Ellipse(pos=(centerx, centery), size=dd, angle_start=a0, angle_end=a1)
            a0 = a1

    def _drawShadow(self):
        if not self.shadowColor: return
        if not self._shadow:
            Color(rgba=get_color_from_hex(self.shadowColor))            
            self._shadow = Line(width=5, cap='none')

        a0 = -(self.a * self.min + self.b)
        a1 = -(self.a * self.value + self.b)
        self._shadow.circle = (self.centerx, self.centery, self.r-5, a0, a1)

    def _drawOuterCadran(self):
        centerx = self.centerx
        centery = self.centery
        r = self.r
        theta0 = self.startAngle
        theta1 = self.endAngle
        Color(rgba=get_color_from_hex(self.cadranColor))
        if theta0 == theta1:
            Line(circle=(centerx, centery, r), width=1.5)
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
                width=1.5,
                     )
            Line(circle=(centerx, centery, r, theta0, theta1), width=1.5)

    # I'm using theta for the angle, as to not confuse it with transparency (alpha as in in rgba)
    def _drawValues(self):
        centerx = self.centerx
        centery = self.centery
        r = self.r
        valueStr = self.valueStr
        values = [Label(valueStr(i), bold=True)
                      for i in range(self.min, self.max + 1, self.tick)]
        if len(values) <= 1:
            # Tick is bigger than max - min
            return
        for _ in values: _.refresh()

        theta0 = self.startAngle
        theta1 = self.endAngle
        if theta0 == theta1:
            theta1 += 360
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
                for n in range(subtick):
                    subc = cos(subTheta)
                    subs = sin(subTheta)
                    Line(points=(
                        centerx + r * subs, centery + r * subc,
                        centerx + r_10 * subs, centery + r_10 * subc),
                             width=0.75)
                    subTheta += subDeltaTheta
            theta += deltaTheta

    def _drawLabel(self, *t):
        if not self.label and not self.labelIcon:
            return
        theta = self.startAngle + self.labelAngleRatio * (self.endAngle - self.startAngle)
        c = cos(radians(theta))
        s = sin(radians(theta))
        r = self.r
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
            label = Label(text=self.label, markup=True, bold=True)
            label.refresh()
            t = label.texture
            tw, th = t.size
        Rectangle(
            pos=(self.centerx + r1 * s - tw/2, self.centery + r1 * c - th/2), size=(tw, th),
            texture=t)

    def _drawNeedle(self):
        if self.value < self.min: self.value = self.min
        elif self.value > self.max: self.value = self.max
        self.on_value()
        needleSize = self.r
        s = needleSize * 2
        Color(rgba=get_color_from_hex(self.needleColor))
        Rectangle(pos=(self.centerx - needleSize, self.centery - needleSize), size=(s, s),
                      source='needle.png')
        
    def _draw_before(self, *t):
        self.canvas.before.clear()
        self._shadow = None
        with self.canvas.before:
            self._drawSectors()
            self._drawShadow()

    def _draw_canvas(self, *t):
        self.canvas.clear()
        with self.canvas:
            self._drawOuterCadran()
            self._drawValues()

    def _draw_after(self, *t):
        self.canvas.after.clear()
        with self.canvas.after:
            self._drawLabel()
            PushMatrix()
            self.rotate = Rotate(origin=(self.centerx, self.centery))
            self._drawNeedle()
            PopMatrix()

    def _draw(self, *args):
        diameter = min(self.size)
        sa = self.startAngle
        ea = self.endAngle
        
        r = self.r = diameter / 2
        self.r2 = r * r
        x, y = self.pos
        width, height = self.size
        self.centerx = x + width / 2
        self.centery = y + height / 2

        #
        # compute value -> angle mapping
        #

        theta0 = sa
        theta1 = ea
        if theta0 == theta1: theta1 += 360
        self.a = (float(theta0) - theta1) / (self.max - self.min)
        self.b = -theta0 - self.a * self.min

        #
        # Reverse mapping
        #
        self.startTheta = _halfPi - radians(sa)
        self.endTheta = _halfPi - radians(ea)
        self.direct = self.startTheta < self.endTheta

        self.ra = (self.max - self.min) / ((self.endTheta - self.startTheta) 
                                           if sa != ea else _2pi)
        self.rb = self.min - self.ra * self.startTheta

        #
        # Draw
        #
        # A bit overcomplicated here, I should only use my own groups (maybe)
        self._draw_before()
        self._draw_canvas()
        self._draw_after()
            
    def on_value(self, *t):
        self.rotate.angle = self.a * self.value + self.b
        self._drawShadow()

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
        return self.getValue(*(x, y)) is not None

    def on_startAngle(self, *t):
        if self.endAngle - self.startAngle > 360:
            self.startAngle = self.endAngle - 360
        self._draw()

    def on_endAngle(self, *t):
        if self.endAngle - self.startAngle > 360:
            self.endAngle = self.startAngle + 360
        self._draw()

class _X: pass
