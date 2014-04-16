from kivy.properties import *
from kivy.uix.screenmanager import Screen
from kivy.uix.scatter import Scatter
from idea import IdeaWidgetBehaviour


class BoardView(Screen):
    pass


class BoardViewIdea(IdeaWidgetBehaviour, Scatter):
    text = StringProperty()
