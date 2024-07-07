import pygame, random
from pygame.locals import *

class Game:
    def __init__(self) -> None:
        pygame.init()
        pygame.font.init()
        self.screen_size = pygame.math.Vector2(1280, 640)
        self.screen = pygame.display.set_mode(self.screen_size, SCALED)
        pygame.display.set_caption('Pong')
        self.event_map = set()
        self.clock = pygame.time.Clock()
        self.fps = 60
        self.delta = 1 / self.fps

    def update_event_map(self):
        self.event_map.clear()
        for event in pygame.event.get():
            if event.type == QUIT: self.event_map.add(QUIT)

    def run(self):
        players = pygame.sprite.Group()
        ball = pygame.sprite.GroupSingle(Ball(self, players))
        players.add(Player(self, 1, (K_w, K_s)))
        players.add(Player(self, 2, (K_UP, K_DOWN)))
        start_button = Button(self.screen_size)

        self.state = 'start'
        self.time = 1
        while True:
            self.update_event_map()
            if QUIT in self.event_map: break

            self.delta = self.clock.tick(self.fps) / 1000

            self.screen.fill('#222222')

            if self.state in ['playing', 'timer']:
                self.playing(players, ball)
                
            elif self.state == 'start':
                self.started(start_button)

            pygame.display.update()

        pygame.quit()

    def started(self, start_button):
        if start_button.clicked(): self.state = 'timer'
        start_button.draw(self.screen)

    def update(self, *args):
        for arg in args:
            arg.update()

    def draw(self, *args):
        for arg in args:
            arg.draw(self.screen)

    def playing(self, players, ball):
        pygame.draw.rect(self.screen, 'white', pygame.rect.Rect(self.screen_size.x // 2 - 2, 0, 4, self.screen_size.y))
        if self.state == 'timer':
            self.timer()
            self.draw(players, ball)
            for player in players.sprites(): player.draw_score()
        else:
            self.update(players, ball)
            self.draw(players, ball)

    def timer(self):
        f_surf = pygame.font.Font(None, 50).render(f'{self.time: .2f}', False, 'pink', '#222222')
        f_font = f_surf.get_rect(centerx=self.screen_size.x // 2, y = 200)
        self.screen.blit(f_surf, f_font)
        self.time -= self.delta
        if self.time < 0:
            self.time = .33
            self.state = 'playing'

class Ball(pygame.sprite.Sprite):
    def __init__(self, game: Game, players: pygame.sprite.Group, speed: int = 500, radius: int = 30) -> None:
        super().__init__()
        self.game = game
        self.players = players
        self.image = pygame.Surface((radius * 2, radius * 2), flags=SRCALPHA)
        self.image.fill((0,0,0,0))
        pygame.draw.circle(self.image, '#F6517A', (radius, radius), radius)
        self.rect = self.image.get_rect(center = (self.game.screen_size.x // 2, self.game.screen_size.y // 2))

        self.velocity = pygame.math.Vector2(random.choice([-1, 1]), random.choice([-.4, .4]))
        self.velocity.x *= speed
        self.velocity.y *= speed

    def move(self):
        self.rect.x += self.velocity.x * self.game.delta
        self.rect.y += self.velocity.y * self.game.delta

    def collision(self):
        if self.rect.y <= 0: # top
            self.rect.y = 1
            self.velocity.y *= -1

        elif self.rect.bottom >= self.game.screen_size.y: # bottom
            self.rect.bottom = self.game.screen_size.y - 1
            self.velocity.y *= -1 

        elif self.rect.x <= -50 or self.rect.right >= self.game.screen_size.x + 50:
            for sprite in self.players.sprites(): sprite.rect.centery = self.game.screen_size.y // 2
            self.players.sprites()[1 if self.rect.x <= -50 else 0].score += 1
            self.game.state = 'timer'
            self.reset()

        for player in self.players.sprites():
            if self.rect.colliderect(player.rect):
                if self.velocity.x < 0 and abs(self.rect.x - player.rect.right) < 10 \
                or self.velocity.x > 0 and abs(self.rect.right - player.rect.x) < 10:
                    self.velocity.x *= -1
                if self.velocity.y > 0 and abs(self.rect.bottom - player.rect.y) < 10 \
                or self.velocity.y < 0 and abs(self.rect.y - player.rect.bottom) < 10:
                    self.velocity.y *= -1

    def reset(self):
        self.rect.center = self.game.screen_size.x // 2, self.game.screen_size.y // 2
        self.velocity.x *= random.choice([-1, 1])
        self.velocity.y *= random.choice([-1, 1])

    def update(self):
        self.collision()
        self.move()

class Player(pygame.sprite.Sprite):
    def __init__(self, game: Game, player: int, keys: tuple, speed: int = 400, size: tuple = (25, 100)) -> None:
        super().__init__()
        self.game = game
        self.player = player
        self.key_up, self.key_down = keys
        self.speed = speed
        self.score = 0
        self.image = pygame.Surface(size)
        self.image.fill('white')
        self.rect = self.image.get_rect(centerx = 50 if self.player == 1 else self.game.screen_size.x - 50, 
                                        centery = self.game.screen_size.y // 2)

    def move(self):
        keys = pygame.key.get_pressed()
        speed = self.speed * self.game.delta
        if keys[self.key_up] and self.rect.y - speed > 10:
            self.rect.y -= speed
        elif keys[self.key_down] and self.rect.bottom + speed < self.game.screen_size.y - 10:
            self.rect.y += speed

    def draw_score(self):
        f_surf = pygame.font.Font(None, size=50).render(f'{self.score}', False, 'white')
        f_rect = f_surf.get_rect(centerx = 100 if self.rect.centerx < self.game.screen_size.x // 2 else self.game.screen_size.x - 100,
                                 y = 25)
        self.game.screen.blit(f_surf, f_rect)
        
    def update(self) -> None:
        self.move()
        self.draw_score()

class Button:
    def __init__(self, screen_size: pygame.math.Vector2, text: str = 'Start', size: tuple = (400, 150)) -> None:
        self.image = pygame.Surface(size, SRCALPHA)
        self.image.fill((0,0,0,0))
        pygame.draw.rect(self.image, 'white', self.image.get_rect(), 10)
        f_surf = pygame.font.Font(None, 150).render(text, True, 'white')
        f_rect = f_surf.get_rect(center=(size[0] // 2, size[1] // 2))
        self.image.blit(f_surf, f_rect)
        self.rect = self.image.get_rect(center=(screen_size.x//2, screen_size.y // 2))

    def hovered(self) -> bool:
        return self.rect.collidepoint(pygame.mouse.get_pos())

    def clicked(self) -> bool:
        return pygame.mouse.get_pressed()[0] and self.hovered()

    def draw(self, surface: pygame.Surface):
        surface.blit(self.image, self.rect)

if __name__ == '__main__':
    Game().run()