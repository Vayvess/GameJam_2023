import os
import json
import pygame as pg
import pygame_gui as ui
from random import randint

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

class ScoreMenu(Scene):
    def __init__(self, client, score):
        super().__init__(client)
        noob = pg.mixer.Sound("ress/Noob.wav")
        noob.set_volume(2)
        if score < 1000:
            noob.play()
        
        best_so_far = client.db.get(client.usern)
        if best_so_far is None:
            best_so_far = -5
        display_txt = f"You achieved a personal best: {score}" if score > best_so_far else f"You scored: {score}"
        with open("scores.db", "w") as f:
            client.db[client.usern] = score
            f.write(json.dumps(client.db))
        
        ui.elements.UITextBox(
            display_txt,
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

class Logo:
    def __init__(self, sprite):
        self.sprite = sprite
        self.pos = pg.Vector2(randint(400, 800), 100)

        self.falling = False
        self.grav_timer = 0
        self.gravity = 0.00002
        self.velocity = pg.Vector2(0, 0)

    def update(self, dt, scroll):
        if self.falling:
            self.grav_timer += dt
            self.velocity.y += self.grav_timer * self.gravity
            self.pos += self.velocity * dt
        
        self.pos.y += scroll
        return self.pos.y < 720
    
    def render(self, client):
        client.canvas.blit(self.sprite, self.pos)
        

class Player:
    def __init__(self):
        self.sprite = pg.image.load("ress/tux.png").convert_alpha()
        self.hammeron = pg.image.load("ress/hammeron.png").convert_alpha()
        self.hammeroff = pg.image.load("ress/hammeroff.png").convert_alpha()

        self.apple_sprite = pg.image.load("ress/apple.png").convert_alpha()
        self.windaub_sprite = pg.image.load("ress/windaub.png").convert_alpha()
        self.linux_sprite = pg.image.load("ress/linux_logo.png").convert_alpha()

        self.sounds = (
            pg.mixer.Sound("ress/s1.wav"),
            pg.mixer.Sound("ress/s2.wav"),
            pg.mixer.Sound("ress/s3.wav"),
            pg.mixer.Sound("ress/s4.wav"),
            pg.mixer.Sound("ress/s5.wav"),
            pg.mixer.Sound("ress/s6.wav")
        )

        self.bonus = 0

        self.pos = pg.Vector2(640, 500)
        self.velocity = pg.Vector2(0, 0)

        self.gravity = 0.00002
        self.grav_timer = 0

        self.grappling = False
        self.grapple_pos = None

        self.dash_timer = 1500
        self.dash_toward = pg.Vector2(0, 0)

        self.hammer_timer = 100

        self.logos = []
        self.logos_timer = 0
    
    def handle_grapple(self, down, egg):
        if down:
            mp = pg.Vector2(pg.mouse.get_pos())
            if mp.x < 340 or mp.x > 940:
                self.grav_timer = 0
                self.grappling = True
                self.grapple_pos = mp
                tmp = self.pos - self.grapple_pos
                self.velocity = -tmp.normalize() * 0.6
            
            tmp = egg.pos + pg.Vector2(48, 48)
            if mp.distance_to(tmp) < 96:
                self.grappling = True
                self.grapple_pos = tmp
                tmp = self.pos - egg.pos
                egg.velocity = tmp.normalize() * 0.25
                egg.grav_timer = 0
        else:
            self.grappling = False
    
    def handle_dash(self, toward):
        if self.dash_timer > 1500:
            self.dash_timer = 0
            self.toward = toward
            self.velocity += toward
    
    def handle_hammer(self, egg):
        if self.hammer_timer > 300:
            self.hammer_timer = 0
            offset = self.pos + pg.Vector2(32, 32)
            tmp = egg.pos + pg.Vector2(48, 48)
            if offset.distance_to(tmp) < 96:
                egg.velocity += pg.Vector2(0, -0.5)
                egg.grav_timer = 0
            
            for logo in self.logos:
                tmp = logo.pos + pg.Vector2(48, 48)
                if offset.distance_to(tmp) < 96:
                    logo.falling = True
                    self.bonus += 500
                    logo.sprite = self.linux_sprite
                    pg.mixer.Sound.play(self.sounds[randint(0, len(self.sounds) - 1)])
            
            
    def update(self, dt):
        scroll = 0

        # GRAVITY
        self.grav_timer += dt
        self.velocity.y += self.grav_timer * self.gravity

        # DASH
        self.dash_timer += dt
        if self.dash_timer > 300:
            self.velocity -= self.dash_toward
            self.dash_toward = pg.Vector2(0, 0)
        npos = self.pos + self.velocity * dt

        # HAMMER
        self.hammer_timer += dt
        self.logos_timer += randint(0, 10)
        if self.logos_timer > 2000:
            self.logos_timer = 0
            self.logos.append(
                Logo(self.apple_sprite if randint(0, 1) else self.windaub_sprite)
            )
        
        if npos.x < 340:
            npos.x = 340
            self.velocity.x = 0
        if npos.x > 876:
            npos.x = 876
            self.velocity.x = 0
        
        
        if npos.y > 200:
            self.pos.y = npos.y
        else:
            scroll = int(self.pos.y - npos.y)
        
        tmp_logo = []
        for logo in self.logos:
            alive = logo.update(dt, scroll)
            if alive:
                tmp_logo.append(logo)
        self.logos = tmp_logo

        
        self.pos.x = npos.x
        return scroll


    def render(self, client):
        client.canvas.blit(self.sprite, self.pos)

        if self.grappling:
            pg.draw.line(client.canvas, (0, 255, 255), self.pos + pg.Vector2(32, 32), self.grapple_pos, 4)
            pg.draw.circle(client.canvas, (125, 64, 64), self.grapple_pos, 16)
        
        if self.dash_timer > 1500:
            pg.draw.circle(client.canvas, (255, 215, 0), self.pos + pg.Vector2(32, 32), 72, 8)
        
        if self.hammer_timer < 300:
            client.canvas.blit(self.hammeroff, self.pos)
        else:
            client.canvas.blit(self.hammeron, self.pos)
        
        for logo in self.logos:
            logo.render(client)

class Egg:
    def __init__(self):
        self.sprite = pg.image.load("ress/linux_usb.png").convert_alpha()
        self.pos = pg.Vector2(500, 250)
        self.velocity = pg.Vector2(0, 0)

        self.gravity = 0.000005
        self.grav_timer = 0
    
    def update(self, dt, scroll):
        # GRAVITY
        self.grav_timer += dt
        self.velocity.y += self.grav_timer * self.gravity

        npos = self.pos + self.velocity * dt
        
        if npos.x < 340:
            npos.x = 340
            self.velocity.x = 0
        if npos.x > 860:
            npos.x = 860
            self.velocity.x = 0
        
        self.pos = npos
        self.pos.y += scroll
        return self.pos.y > 720

    def render(self, client):
        client.canvas.blit(self.sprite, self.pos)

class TheGame(Scene):
    def __init__(self, client):
        super().__init__(client)

        self.scored = 0
        self.scroll = 0

        self.egg = Egg()
        self.player = Player()
        self.backg = pg.image.load("ress/iced.png").convert()
    
    def process_event(self, event):
        if event.type == pg.MOUSEBUTTONDOWN:
            self.player.handle_grapple(True, self.egg)
        if event.type == pg.MOUSEBUTTONUP:
            self.player.handle_grapple(False, self.egg)
        
        if event.type == pg.KEYDOWN:
            if event.key == pg.K_q:
                self.player.handle_dash(pg.Vector2(-0.5, 0))
            if event.key == pg.K_d:
                self.player.handle_dash(pg.Vector2(0.5, 0))
            
            if event.key == pg.K_SPACE:
                self.player.handle_hammer(self.egg)
    
    def update(self, dt):
        # GAMEOVER
        scroll = self.player.update(dt)
        if self.egg.update(dt, scroll):
            self.set_next(ScoreMenu, self.scored // 30 + self.player.bonus)
        self.scroll = (self.scroll + scroll) % 720
        self.scored += scroll
    
    def render(self):
        self.client.canvas.blit(self.backg, (0, self.scroll))
        self.client.canvas.blit(self.backg, (0, self.scroll - 720))

        self.egg.render(self.client)
        self.player.render(self.client)

        scored_txt = self.client.font.render(
            f"score: {self.scored // 30 + self.player.bonus}", True, (0, 0, 0))
        self.client.canvas.blit(scored_txt, (24, 24))

        usern_txt = self.client.font.render(self.client.usern, True, (255, 255, 255))
        self.client.canvas.blit(usern_txt, self.player.pos - pg.Vector2(len(self.client.usern) * 6, 32))

class LeaderBoard(Scene):
    def __init__(self, client):
        super().__init__(client)

        self.ranks = []
        for item in client.db.items():
            self.ranks.append(item)
        self.ranks.sort(key=lambda k: k[1], reverse=True)
        
        self.leave_btn = ui.elements.UIButton(pg.rect.Rect(
            client.res.x // 2 - 100,
            600,
            200, 50
        ),
            "Back",
            client.manui
        )
    
    def process_event(self, event):
        if event.type == ui.UI_BUTTON_PRESSED:
            if event.ui_element == self.leave_btn:
                self.set_next(StartMenu)
    
    def render(self):
        size = len(client.db) if len(client.db) < 10 else 10
        for x in range(size):
            txt = f"{x + 1} - {self.ranks[x][0]}: {self.ranks[x][1]}"
            rank_txt = client.font.render(txt, True, (255, 255, 255))
            client.canvas.blit(rank_txt, (640 - len(txt) * 8, (x + 1) * 60))

class StartMenu(Scene):
    def __init__(self, client):
        super().__init__(client)
        self.muted = False
        self.backg = pg.image.load("ress/iced.png").convert()
        self.notcool = pg.mixer.Sound("ress/PasSympas.wav")
        self.title = client.font.render("Install Party", True, (255, 255, 255))

        self.usern_tf = ui.elements.UITextEntryLine(pg.rect.Rect(
            client.res.x // 2 - 100,
            client.res.y // 2 - 50,
            200, 50
        ),
            client.manui, initial_text=self.client.usern
        )

        self.play_btn = ui.elements.UIButton(pg.rect.Rect(
            client.res.x // 2 - 100,
            client.res.y // 2 + 25,
            200, 50
        ),
            "Play",
            client.manui
        )

        self.leaderboard = ui.elements.UIButton(pg.rect.Rect(
            client.res.x // 2 - 100,
            client.res.y // 2 + 100,
            200, 50
        ),
            "Leaderboard",
            client.manui
        )

        self.mute = ui.elements.UIButton(pg.rect.Rect(
            client.res.x // 2 - 100,
            client.res.y // 2 + 175,
            200, 50
        ),
            "Mute",
            client.manui
        )

        self.quit_btn = ui.elements.UIButton(pg.rect.Rect(
            client.res.x // 2 - 100,
            client.res.y // 2 + 250,
            200, 50
        ),
            "Quit",
            client.manui
        )

        self.scroll = 0
    
    def process_event(self, event):
        if event.type == ui.UI_BUTTON_PRESSED:
            if event.ui_element == self.play_btn:
                usern = self.usern_tf.get_text()
                if not 1 < len(usern) < 12:
                    self.client.usern = f"Anon_{randint(0, 666)}"
                else:
                    self.client.usern = usern
                self.set_next(TheGame)
            
            if event.ui_element == self.leaderboard:
                self.set_next(LeaderBoard)
            
            if event.ui_element == self.mute:
                self.muted = not self.muted
                if self.muted:
                    self.mute.set_text("Music")
                    pg.mixer.music.pause()
                    self.notcool.play()
                else:
                    self.mute.set_text("Mute")
                    pg.mixer.music.play(-1)
            
            if event.ui_element == self.quit_btn:
                self.client.running = False
    
    def update(self, dt):
        self.scroll = (self.scroll + dt * 0.2) % 720
    
    def render(self):
        self.client.canvas.blit(self.backg, (0, self.scroll))
        self.client.canvas.blit(self.backg, (0, -720 + self.scroll))
        self.client.canvas.blit(self.title, (540, 180))

class Client:
    def __init__(self):
        self.scene = None
        self.running = True
        self.usern = f"Anon{randint(0, 666)}"

        self.res = pg.Vector2(1280, 720)
        pg.display.set_caption("GAMEJAM 2023")

        self.canvas = pg.surface.Surface(self.res)
        self.window = pg.display.set_mode(self.res)
        pg.display.toggle_fullscreen()

        self.manui = ui.UIManager(tuple(self.res))
        self.font = pg.font.SysFont(pg.font.get_default_font(), 48)

        pg.mixer.music.load("ress/Funky.wav")
        pg.mixer.music.set_volume(0.2)
        pg.mixer.music.play(-1)

        try:
            with open("scores.db", "r") as f:
                self.db = json.loads(f.read())
        except Exception as err:
            with open("scores.db", "w+") as f:
                self.db = {}
                f.write(json.dumps(self.db))
            print(err)
    
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
