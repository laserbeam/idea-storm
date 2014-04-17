from kivy.event import EventDispatcher
from kivy.properties import *
from idea import Idea
import json


class Storm(EventDispatcher):
    '''A storm is a collection of ideas.'''
    max_key = 0
    name = StringProperty('')
    ideas = DictProperty()

    def add_idea(self, idea=None, parent=None, **kwargs):
        if idea is None:
            self.max_key = self.max_key + 1
            idea = Idea(self, self.max_key, **kwargs)
        self.ideas[idea.key] = idea
        self.max_key = max(self.max_key, idea.key)
        if parent:
            if not isinstance(parent, Idea):
                parent = self.get_idea(parent)
            if parent:
                parent.add_child(idea)
        return idea

    def remove_idea(self, key):
        if isinstance(key, Idea):
            key = key.key
        if key in self.ideas:
            del self.ideas[key]

    def has_idea(self, key):
        if isinstance(key, Idea):
            key = key.key
        return key in self.ideas

    # root_idea = AliasProperty()

    def get_idea(self, key):
        if isinstance(key, Idea):
            return key
        return self.ideas.get(key)

    def as_json(self):
        return json.dumps({
            'type': 'storm',
            'name': self.name,
            'ideas': [idea.as_dict() for idea in self.ideas.values()],
        })

    def on_ideas(self, *args):
        print 'IDEAS!'

    @staticmethod
    def from_json(self, string):
        obj = json.loads(string)
        storm = Storm()
        storm.name = obj['name']
        idea_list = obj['ideas']
        for templ in idea_list:
            storm.add_idea(Idea.from_dict(temp))
        for idea in self.ideas.values():
            if idea.parent != -1:
                parent = self.get_idea(idea.parent)
                parent.add_child(idea)
        return storm
