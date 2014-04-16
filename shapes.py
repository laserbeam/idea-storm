from kivy.properties import *
from kivy.uix.widget import Widget
from kivy.graphics import Color, Line, Ellipse, Rectangle
from kivy.factory import Factory
from kivy.clock import Clock
from math import sqrt


class RoundedRectangle(Widget):
    radius = NumericProperty(20)
    thinkness = NumericProperty(2)
    line_color = ListProperty([0, 0, 0, 1])
    background_color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):

        super(RoundedRectangle, self).__init__(**kwargs)
        self.bind(line_color=self._schedule_draw, thinkness=self._schedule_draw,
                  background_color=self._schedule_draw)
        self.draw()

    def _schedule_draw(self, *args):
        Clock.unschedule(self.draw)
        Clock.schedule_once(self.draw, 0)

    def draw(self, *args):
        x, y = self.pos
        w, h = self.size
        xx = self.right
        yy = self.top
        r = self.radius
        p = (sqrt(2.)-1)*r
        t = self.thinkness

        self.canvas.clear()
        with self.canvas:
            Color(*self.background_color)
            Ellipse(pos=[x, y], size=[2*r, 2*r])
            Ellipse(pos=[xx-2*r, y], size=[2*r, 2*r])
            Ellipse(pos=[x, yy-2*r], size=[2*r, 2*r])
            Ellipse(pos=[xx-2*r, yy-2*r], size=[2*r, 2*r])
            Rectangle(pos=[x+r, y], size=[w-2*r, h])
            Rectangle(pos=[x, y+r], size=[w, h-2*r])
            Color(*self.line_color)
            Line(width=t, points=(x, y+r, x, yy-r))
            Line(width=t, points=(xx, y+r, xx, yy-r))
            Line(width=t, points=(x+r, y, xx-r, y))
            Line(width=t, points=(x+r, yy, xx-r, yy))
            Line(width=t, bezier=(x, y+r, x, y+p, x+p, y, x+r, y))
            Line(width=t, bezier=(x, yy-r, x, yy-p, x+p, yy, x+r, yy))
            Line(width=t, bezier=(xx, y+r, xx, y+p, xx-p, y, xx-r, y))
            Line(width=t, bezier=(xx, yy-r, xx, yy-p, xx-p, yy, xx-r, yy))

    def on_size(self, *arg):
        if self.radius > self.width/2. or self.radius > self.height/2.:
            self.radius = min(self.width/2., self.height/2.)
        self._schedule_draw()

    def on_radius(self, obj, val):
        if self.radius > self.width/2. or self.radius > self.height/2.:
            self.radius = min(self.width/2., self.height/2.)
        self._schedule_draw()

Factory.register('RoundedRectangle', cls=RoundedRectangle)
