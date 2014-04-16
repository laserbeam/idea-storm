# -*- coding: utf-8 -*-
# Author: Catalin Balan
from __future__ import division, unicode_literals
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, FadeTransition
from kivy.config import Config
from kivy.properties import *
from boardview import BoardView
import shapes
import resizingtextinput

Config.set('graphics', 'width', '1024')
Config.set('graphics', 'height', '768')
__version__ = '0.0.1'


class IdeaStormApp(App):

    def build(self):
        sm = ScreenManager(transition=FadeTransition(duration=.1))
        sm.add_widget(BoardView(name='boardview'))
        return sm

if __name__ == '__main__':
    IdeaStormApp().run()
