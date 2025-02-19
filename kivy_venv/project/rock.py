from kivy.uix.widget import Widget
from kivy.properties import NumericProperty, ObjectProperty, ListProperty
from kivy.uix.image import Image

class Rock(Widget):
    rock_texture = ObjectProperty(None)

#defining a function so that more than one obstacle appears.
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.rock_texture = Image(source='rock.png')
        self.rock_texture.wrap = 'repeat'