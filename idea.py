from kivy.event import EventDispatcher
from kivy.properties import *
import json


class Idea(EventDispatcher):
    id_count = 0
    key_id = NumericProperty(0)
    title = StringProperty('')
    color = ObjectProperty(None)
    description = StringProperty('')
    x = NumericProperty(0)
    y = NumericProperty(0)
    pos = ReferenceListProperty(x, y)
    children = ListProperty()
    parent_idea = NumericProperty(-1)

    def __init__(self, **kwargs):
        super(Idea, self).__init__(**kwargs)
        self.key_id = Idea.id_count + 1
        Idea.id_count = Idea.id_count + 1

    def add_child(self, idea):
        children.append(idea)
        idea.parent_idea = self

    def remove_child(self, idea):
        children.remove(idea)
        idea.parent_idea = -1

    def as_json(self):
        parent_num = -1
        if self.parent_idea:
            parent_num = self.parent_num.key_id
        return json.dumps({
            'id': self.key_id,
            'title': self.title,
            'color': self.color,
            'desc': self.description,
            'x': self.x,
            'y': self.y,
            'parent': parent_num
        })


class IdeaWidgetBehaviour(object):
    idea = ObjectProperty(None)
    _old_idea = ObjectProperty(None)
    title_widget = ObjectProperty(None)
    _old_title_widget = ObjectProperty(None)
    description_widget = ObjectProperty(None)
    _old_description_widget = ObjectProperty(None)

    def __init__(self, idea=None, **kwargs):
        super(IdeaWidgetBehaviour, self).__init__(**kwargs)
        if idea is None:
            idea = Idea()
        self.idea = idea

    def on_idea(self, obj, value):
        if self._old_idea:
            self._unbind_editors(idea=self._old_idea)
        self._bind_editors()
        self._old_idea = value

    def on_title_widget(self, obj, value):
        if self._old_title_widget:
            self._unbind_editors(title=self._old_title_widget)
        self._bind_editors()
        self._old_title_widget = value

    def on_description_widget(self, obj, value):
        if self._old_description_widget:
            self._unbind_editors(desc=self._old_description_widget)
        self._bind_editors()
        self._old_description_widget = value

    def _bind_editors(self, idea=None, title=None, desc=None):
        if idea is None:
            idea = self.idea
        if title is None:
            title = self.title_widget
        if desc is None:
            desc = self.description_widget
        if idea:
            if title:
                idea.bind(title=title.setter('text'))
                title.bind(text=idea.setter('title'))
            if desc:
                idea.bind(description=desc.setter('text'))
                desc.bind(text=idea.setter('description'))

    def _unbind_editors(self, idea=None, title=None, desc=None):
        if idea is None:
            idea = self.idea
        if title is None:
            title = self.title_widget
        if desc is None:
            desc = self.description_widget
        if idea:
            if title:
                idea.unbind(title=title.setter('text'))
                title.unbind(text=idea.setter('title'))
            if desc:
                idea.unbind(description=desc.setter('text'))
                desc.unbind(text=idea.setter('description'))
