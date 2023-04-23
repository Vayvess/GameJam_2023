from scenes.imports import *

class StartMenu(Scene):
    def __init__(self, client):
        super().__init__(client)
        self.start_btn = ui.elements.UIButton(pg.rect.Rect(
            client.res.x // 2 - 100,
            client.res.y // 2 + 25,
            200, 50
        ),
            "Start",
            client.manui
        )

    
    def process_event(self, event):
        if event.type == ui.UI_BUTTON_PRESSED:
            if event.ui_element == self.start_btn:
                self.set_next(TheGame)
