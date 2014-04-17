from kivy.event import EventDispatcher
from kivy.properties import *
import json


class Idea(EventDispatcher):
    '''A single idea, inside a massive storm.'''
    id_count = 0
    storm = ObjectProperty(None)
    key = NumericProperty(0)
    title = StringProperty('')
    color = ListProperty([0, 0, 0, 1])
    description = StringProperty('')
    x = NumericProperty(0)
    y = NumericProperty(0)
    pos = ReferenceListProperty(x, y)
    scale = NumericProperty(1)
    children = ListProperty()
    parent = ObjectProperty(None)

    def __init__(self, storm=None, key=None, **kwargs):
        super(Idea, self).__init__(**kwargs)
        self.storm = storm
        if key is not None:
            self.key = key
        else:
            self.key = Idea.id_count + 1
            Idea.id_count = Idea.id_count + 1
        self.title = kwargs.get('title', '')
        self.description = kwargs.get('description', '')
        self.color = kwargs.get('color', [0, 0, 0, 1])

    def add_child(self, idea):
        if idea.parent:
            idea.parent.remove_child(idea)
        self.children.append(idea)
        idea.parent = self

    def remove_child(self, idea):
        self.children.remove(idea)
        idea.parent = None

    def as_dict(self):
        parent_num = -1
        if self.parent:
            parent_num = self.parent.key
        return {
            'id': self.key,
            'title': self.title,
            'color': self.color,
            'desc': self.description,
            'x': self.x,
            'y': self.y,
            'scale': self.scale,
            'parent': parent_num
        }

    @staticmethod
    def from_dict(obj):
        idea = Idea(obj['id'])
        idea.title = obj['title']
        idea.color = obj['color']
        idea.desc = obj['desc']
        idea.x = obj['x']
        idea.y = obj['y']
        idea.scale = obj['scale']
        return idea

    @staticmethod
    def from_json(string):
        obj = json.loads(string)
        return Idea.from_dict(obj)


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
                title.text = idea.title
                idea.bind(title=title.setter('text'))
                title.bind(text=idea.setter('title'))
            if desc:
                desc.text = idea.description
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
