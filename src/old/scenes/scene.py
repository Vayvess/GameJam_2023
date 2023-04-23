import pygame as pg
import pygame_gui as ui

class Scene:
    def __init__(self, client):
        self.client = client
        self.next = None

    def set_next(self, scene_class, *args):
        self.client.manui.clear_and_reset()
        self.next = scene_class(self.client, *args)
    
    def process_event(self, event):
        pass
    
    def update(self, dt):
        pass
    
    def render(self):
        pass
