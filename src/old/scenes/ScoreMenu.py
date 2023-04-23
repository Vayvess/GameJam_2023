from scenes.imports import *

class ScoreMenu(Scene):
    def __init__(self, client, score):
        super().__init__(client)
        ui.elements.UITextBox(
            f"You scored: {score}",
            pg.rect.Rect(
                client.res.x // 2 - 250,
                client.res.y // 2 - 100,
                500, 50
            ),
            client.manui
        )

        self.leave = ui.elements.UIButton(pg.rect.Rect(
            client.res.x // 2 - 100,
            client.res.y // 2 + 75,
            200, 50
        ),
            "Leave",
            client.manui
        )

    
    def process_event(self, event):
        if event.type == ui.UI_BUTTON_PRESSED:
            if event.ui_element == self.leave:
                self.set_next(StartMenu)
