from kivy.properties import *
from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Scatter, ScatterPlane
from kivy.uix.widget import Widget
from kivy.factory import Factory
from kivy.graphics import Color, Line, Rectangle
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
    selected_widget = ObjectProperty(None)

    def __init__(self, **kwargs):
        super(IdeaBoard, self).__init__(**kwargs)
        self.storm = Storm()
        # Clock.schedule_once(self.buildstuff)

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
        idea_widget = BoardViewIdea(idea=idea, board=self)
        # if parent is None:
        xx, yy = self.to_local(self.parent.width/2, self.parent.height/2)
        idea_widget.center = xx, yy
        # else:
            # idea_widget.center = parent.center
        self.add_widget(idea_widget)
        self.storm_widgets[idea.key] = idea_widget
        idea_widget.bind(pos=self.background.schedule_redraw)
        self.select_widget(idea_widget)
        return idea_widget

    def add_idea_to_selected(self, idea=None, **kwargs):
        if self.selected_widget is not None:
            self.add_idea(parent=self.selected_widget.idea)
        else:
            self.add_idea()

    def get_idea_widget(self, idea):
        if isinstance(idea, BoardViewIdea):
            return idea
        return self.storm_widgets.get(idea.key, None)

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

    def select_widget(self, widget):
        if self.selected_widget is not None:
            if self.select_widget != widget:
                self.selected_widget.selected = False
        self.selected_widget = widget
        widget.selected = True

    def zoom_to_widget(self, widget=None):
        if widget is None:
            widget = self.selected_widget
        if widget is None:
            return
        print widget, widget.center
        x, y = widget.to_window(widget.width/2, widget.height/2, initial=False)
        print x, y
        x, y = self.to_widget(x, y)
        print x, y
        anim = Animation(center_x=self.width-x, center_y=self.height-y, d=0.3,
                         t='in_out_quad')
        anim.start(self)


class BoardViewIdea(IdeaWidgetBehaviour, Scatter):
    text = StringProperty()
    color = ListProperty([1, 1, 1, 1])
    selected = BooleanProperty()
    board = ObjectProperty(None)
    child_ideas = ListProperty()

    def __init__(self, board, **kwargs):
        super(BoardViewIdea, self).__init__(**kwargs)
        self.scale = 0.1
        self.opacity = 0
        self.title_widget.focus = True
        anim = Animation(opacity=1, scale=1, d=0.5, t='out_elastic')
        anim.start(self)
        self.board = board
        Clock.schedule_once(self.on_selected)

    def on_selected(self, *args):
        if self.selected:
            self.ids.bg.background_color = [0.78, 0.78, 0.95, 1]
            self.title_widget.focus = True
        else:
            self.ids.bg.background_color = [1, 1, 1, 1]

    def on_touch_down(self, *args):
        ok = super(BoardViewIdea, self).on_touch_down(*args)
        if ok:
            self.selected = True
            self.board.select_widget(self)
        return ok

    def move_to(self, x, y):
        anim = Animation(x=x, y=y, d=0.5, t='in_out_cubic')
        anim.start(self)


class IdeaBoardBackground(Widget):
    storm_widgets = ObjectProperty()

    def __init__(self, **kwargs):
        super(IdeaBoardBackground, self).__init__(**kwargs)

    def schedule_redraw(self, *args):
        Clock.unschedule(self._redraw)
        Clock.schedule_once(self._redraw, 0)

    def _redraw(self, *args):
        self.canvas.clear()
        with self.canvas:
            Color(0, 0, 0, 1)
            for w1 in self.storm_widgets.values():
                for p in w1.idea.children:
                    w2 = self.storm_widgets.get(p.key, None)
                    if w2 is not None:
                        x1, y1 = w1.center
                        x2, y2 = w2.center
                        dx, dy = (x2-x1)*0.7, (y2-y1)*0.2
                        xp, yp = x1+dx, y1+dy
                        xq, yq = x2-dx, y2-dy
                        Line(width=1.5, bezier=(x1, y1, xp, yp, xq, yq, x2, y2))
        self.canvas.ask_update()


Factory.register('BoardScreen', cls=BoardScreen)
Factory.register('IdeaBoard', cls=IdeaBoard)
Factory.register('IdeaBoardBackground', cls=IdeaBoardBackground)
Factory.register('BoardViewIdea', cls=BoardViewIdea)
