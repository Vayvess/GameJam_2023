from scenes.imports import *

class Client:
    def __init__(self):
        self.scene = None
        self.running = True

        self.res = pg.Vector2(1280, 720)
        pg.display.set_caption("GAMEJAM 2023")

        self.canvas = pg.surface.Surface(self.res)
        self.window = pg.display.set_mode(self.res)
        pg.display.toggle_fullscreen()

        self.manui = ui.UIManager(tuple(self.res))
        self.font = pg.font.SysFont(pg.font.get_default_font(), 48)
    
    def start(self):
        clock = pg.time.Clock()
        self.scene = StartMenu(self)

        while self.running:
            if self.scene.next is not None:
                self.scene = self.scene.next
            
            # Scene handle
            dt = clock.tick(60)
            for event in pg.event.get():
                self.manui.process_events(event)
                self.scene.process_event(event)
                if event.type == pg.QUIT:
                    self.running = False
            
            self.manui.update(dt / 1000.0)
            self.scene.update(dt)

            self.canvas.fill((0, 0, 0))
            self.scene.render()
            self.window.blit(
                pg.transform.scale(self.canvas, self.res),
                (0, 0)
            )
            self.manui.draw_ui(self.window)
            pg.display.flip()


if __name__ == '__main__':
    pg.init()
    client = Client()
    client.start()
    pg.quit()
