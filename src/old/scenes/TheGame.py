from scenes.imports import *

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
        self.sprite = pg.image.load("scenes/tux.png").convert_alpha()
        self.hammeron = pg.image.load("scenes/hammeron.png").convert_alpha()
        self.hammeroff = pg.image.load("scenes/hammeroff.png").convert_alpha()

        self.apple_sprite = pg.image.load("scenes/apple.png").convert_alpha()
        self.windaub_sprite = pg.image.load("scenes/windaub.png").convert_alpha()
        self.linux_sprite = pg.image.load("scenes/linux_logo.png").convert_alpha()

        self.sounds = (
            pg.mixer.Sound("scenes/s1.wav"),
            pg.mixer.Sound("scenes/s2.wav"),
            pg.mixer.Sound("scenes/s3.wav"),
            pg.mixer.Sound("scenes/s4.wav"),
            pg.mixer.Sound("scenes/s5.wav"),
            pg.mixer.Sound("scenes/s6.wav")
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
        self.sprite = pg.image.load("scenes/linux_usb.png").convert_alpha()
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
        self.backg = pg.image.load("scenes/iced.png").convert()
    
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
