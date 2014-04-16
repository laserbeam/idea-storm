from kivy.properties import *
from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Scatter, ScatterPlane
from kivy.uix.widget import Widget
from kivy.factory import Factory
from kivy.graphics import Color, Line
from kivy.animation import Animation
from kivy.clock import Clock
from idea import IdeaWidgetBehaviour
from storm import Storm


class BoardScreen(Screen):
    pass


class IdeaBoard(ScatterPlane):
    storm = ObjectProperty()
    storm_widgets = DictProperty()
    background = ObjectProperty()
    toolbar = ObjectProperty()

    def __init__(self, **kwargs):
        super(IdeaBoard, self).__init__(**kwargs)
        self.storm = Storm()
        Clock.schedule_once(self.buildstuff)

    def buildstuff(self, *args):
        w = self.add_idea()
        w.text = 'very long text which should span across several lines \
without problems'
        w2 = self.add_idea(parent=w.idea)
        w2.text = 'dfgskdfhgjskerugbsliehgjkfdhbgyuserbgljkshdfgiusfgjssdfg text\
 containing a very very long word, longer than the maximum length of the widget'
        w = self.add_idea(title='foo', parent=w2.idea)

    def add_idea(self, idea=None, parent=None, **kwargs):
        if idea is None:
            idea = self.storm.add_idea(parent=parent, **kwargs)
        idea_widget = BoardViewIdea(idea=idea)
        xx, yy = self.to_local(self.width/2, self.height/2)
        idea_widget.center = xx, yy
        self.add_widget(idea_widget)
        self.storm_widgets[idea.key] = idea_widget
        idea_widget.bind(pos=self.background.schedule_redraw)
        return idea_widget

    def on_touch_down(self, touch):
        if self.toolbar.on_touch_down(touch):
            return True
        return super(IdeaBoard, self).on_touch_down(touch)

    def on_touch_move(self, touch):
        if self.toolbar.on_touch_move(touch):
            return True
        return super(IdeaBoard, self).on_touch_move(touch)

    def on_touch_up(self, touch):
        if self.toolbar.on_touch_up(touch):
            return True
        return super(IdeaBoard, self).on_touch_up(touch)


class IdeaBoardBackground(Widget):
    storm_widgets = ObjectProperty()

    def __init__(self, **kwargs):
        super(IdeaBoardBackground, self).__init__(**kwargs)

    def schedule_redraw(self, *args):
        Clock.unschedule(self._redraw)
        Clock.schedule_once(self._redraw, 0)

    def _redraw(self, *args):
        with self.canvas:
            Color(0.3, 0.3, 0.3, 1)
            print '-------------------------'
            for w1 in self.storm_widgets.values():
                for p in w1.idea.children:
                    w2 = self.storm_widgets.get(p.key, None)
                    if w2 is not None:
                        print w1, w2, w1.pos, w2.pos
                        Line(width=1.5, poins=(w1.center_x, w1.center_y,
                                               w2.center_x, w2.center_y))
        self.canvas.ask_update()


class BoardViewIdea(IdeaWidgetBehaviour, Scatter):
    text = StringProperty()
    color = ListProperty([1, 1, 1, 1])

    def __init__(self, **kwargs):
        super(BoardViewIdea, self).__init__(**kwargs)
        self.scale = 0.1
        self.opacity = 0.5
        self.title_widget.focus = True
        anim = Animation(opacity=1, scale=1, d=0.3, t='out_elastic')
        anim.start(self)

Factory.register('BoardScreen', cls=BoardScreen)
Factory.register('IdeaBoard', cls=IdeaBoard)
Factory.register('IdeaBoardBackground', cls=IdeaBoardBackground)
Factory.register('BoardViewIdea', cls=BoardViewIdea)
