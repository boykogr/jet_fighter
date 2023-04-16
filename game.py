import pygame
import random
import asyncio
from models import Plane, Missile, CruiseMissile, Drone, Explosion, Bullets, Balloon
from screens import Intro, Menu, Pause, Cursor, Hud, Points, Message, FPS, Timer
from utilities import load_sprite, load_sound
import timeit


class JetFighter:
    def __init__(self):
        # Initialize pygame mixer
        pygame.mixer.pre_init(44100, 16, 2, 4096)
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Jet Fighter")
        self.clock = pygame.time.Clock()
        # Set up the screen
        self.screen = pygame.display.set_mode((800, 600))
        self.background = load_sprite('background4', False)
        # Set allowed events
        pygame.event.set_allowed([pygame.QUIT, pygame.KEYDOWN, pygame.KEYUP, pygame.MOUSEBUTTONDOWN])
        # hide OS cursor
        pygame.mouse.set_visible(False)
        # Music
        self.background_music = load_sound('music')
        self.background_music.set_volume(0.1)
        # self.background_music.play(-1)
        self.music = False
        self.sounds = False

        self.game_state = 'Intro'

        self.level = 1

        self.intro = Intro(self.screen)

        self.menu = Menu(self.screen)

        self.pause = Pause()

        self.plane = Plane((400, 300))
        pygame.mixer.pause()

        self.cursor = Cursor()

        self.hud = Hud((400, 530))

        self.points = Points()

        self.timer = Timer(60)

        # Pre-initialize all the enemy objects and add them to the inactive pool
        # max 3 missiles, max 2 cruise missiles, max 1 drone
        self.enemy_pool = [Missile(self.screen, self.plane.position) for _ in range(3)]
        self.enemy_pool += [CruiseMissile(self.screen, self.plane.position) for _ in range(2)]
        self.enemy_pool.append(Drone(self.screen, self.plane.position))

        self.active_enemies = []

        # Pre-initialize all the balloon objects and add them to the inactive pool - max 3 balloons
        self.balloons_pool = [Balloon(self.screen) for _ in range(3)]

        self.active_balloons = []

        # Pre-initialize all the bullet objects and add them to the inactive pool - max 3 bullets
        self.bullets = []

        self.explosions = []

        self.message = Message()

        self.dodge = False
        self.dodge_counter = 60

        self.hit = 0
        self.hit_slow_time = 0
        self.screen_shake = 0

        self.fps = 60

        self.fps_display = FPS()

    async def main_loop(self):
        while True:
            self._handle_input()
            self._game_logic()
            self._draw()
            await asyncio.sleep(0)

    def _handle_input(self):
        is_key_pressed = pygame.key.get_pressed()
        if self.game_state == 'Intro':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN:
                    self.game_state = 'Menu'
                    return
        if self.game_state == 'Menu':
            if self.menu.menu_logic() == 'Game':
                self.game_state = 'Game'
                return
        elif self.game_state == 'Game':
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    quit()
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_state = 'Pause'
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                        and self.hit < 1 and len(self.bullets) < 1:
                    self.bullets.append(Bullets(self.plane.position, self.plane.direction, self.sounds))
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_m:
                    if self.music:
                        self.background_music.fadeout(180)
                        self.music = False
                    else:
                        self.music = True
                        self.background_music.play(-1)
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_s:
                    if self.sounds:
                        pygame.mixer.pause()
                        self.sounds = False
                    else:
                        pygame.mixer.unpause()
                        self.sounds = True
            if is_key_pressed[pygame.K_SPACE] and self.hit < 2:
                if self.sounds:
                    self.plane.thrust()
                else:
                    self.plane.thrust(sound=False)
            elif is_key_pressed[pygame.K_SPACE] and self.hit >= 2:
                if self.sounds:
                    self.plane.thrust(thrusters=False)
                else:
                    self.plane.thrust(thrusters=False, sound=False)
            else:
                self.plane.refuel()
            if is_key_pressed[pygame.K_LSHIFT] and self.plane.slow_motion():
                self.fps = 30
                if self.sounds:
                    pygame.mixer.pause()
                    pygame.mixer.unpause()
            else:
                self.plane.refocus()
                self.fps = 60
        if self.game_state == 'Pause':
            current_state = self.pause.pause_logic()
            if current_state == 'Game':
                self.game_state = 'Game'
            elif current_state == 'Menu':
                self.game_state = 'Menu'
                self.points.points = 0

    @property
    def game_objects(self):
        return [*self.active_enemies, self.plane, *self.explosions, *self.bullets, *self.active_balloons]

    def _game_logic(self):
        if self.game_state == 'Intro' or self.game_state == 'Menu' or self.game_state == 'Pause':
            return
        if self.level == 1:
            # Add new objects
            self.get_inactive_objects(missiles=3, cruise=2, drones=1, balloons=3)
        for obj in self.game_objects:
            obj.move(self.screen)
            if obj == self.plane:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_position = pygame.math.Vector2(mouse_x, mouse_y)
                obj.rotate(mouse_position)
            else:
                obj.rotate(self.plane.position)
            if obj not in self.explosions and obj not in self.active_balloons:
                obj.trail()
        for bullet in self.bullets:
            if bullet.outside():
                self.bullets.remove(bullet)
            for missile in self.active_enemies:
                if bullet.collides_with(missile):
                    self.active_enemies.remove(missile)
                    missile.active = False
                    self.bullets.remove(bullet)
                    self.explosions.append(Explosion(missile.position, self.sounds))
                    self.points.calculate('bullet')
                    break
            for balloon in self.active_balloons:
                if bullet.collides_with(balloon):
                    self.active_balloons.remove(balloon)
                    balloon.active = False
                    self.bullets.remove(bullet)
                    self.explosions.append(Explosion(balloon.position, self.sounds))
                    self.points.calculate('bullet')
                    break
        for balloon in self.active_balloons:
            if balloon.collides_with(self.plane):
                self.active_balloons.remove(balloon)
                balloon.active = False
                self.explosions.append(Explosion(balloon.position, self.sounds))
                self.points.calculate('balloon')
                break
            balloon.calculate()
            if balloon.time <= 0:
                self.active_balloons.remove(balloon)
                self.points.calculate('Penalty')
                balloon.active = False

        for missile in self.active_enemies:
            if missile.collides_with(self.plane):
                self.hit += 1
                self.hud.hit()
                self.plane.hit += 1
                self.message.take(self.plane.hit)
                self.active_enemies.remove(missile)
                missile.active = False
                self.explosions.append(Explosion(missile.position, self.sounds))
                self.hit_slow_time = 60
                self.screen_shake = 30
                self.dodge = False
                self.dodge_counter = 90
                break
            if self.plane.dodge(missile):
                self.dodge = True
            if self.dodge:
                self.dodge_counter -= 1
                if self.dodge_counter == 0:
                    self.points.calculate('dodge')
                    self.message.take(-1)
                    self.dodge = False
                    self.dodge_counter = 90
            for other in self.active_enemies:
                if missile != other:
                    if missile.collides_with(other):
                        self.active_enemies.remove(missile)
                        missile.active = False
                        self.active_enemies.remove(other)
                        other.active = False
                        self.explosions.append(Explosion(missile.position, self.sounds))
                        self.points.calculate('missile')
                        break
        if self.hit_slow_time:
            self.hit_slow_time -= 1
            self.fps = 30

        self.points.calculate('time')
        self.timer.calculate()

    def _draw(self):
        if self.game_state == 'Intro':
            if self.intro.draw(self.screen) == 'Menu':
                self.game_state = 'Menu'
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
            return
        elif self.game_state == 'Menu':
            self.menu.draw(self.screen)
            # show OS cursor
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            # self.cursor.draw(self.screen)
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
            return
        elif self.game_state == 'Pause':
            self.pause.draw(self.screen)
            # show OS cursor
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            pygame.display.flip()
            self.clock.tick(self.fps)
            return
        elif self.game_state == 'Game':
            if pygame.mouse.get_visible():
                pygame.mouse.set_visible(False)
            # Background
            self.screen.blit(self.background, (0, 0))
            # Cursor
            self.cursor.draw(self.screen)
            # Objects
            for obj in self.game_objects:
                # obj.draw(self.screen)
                if obj.draw(self.screen) == -1:
                    self.explosions.remove(obj)
            # HUD
            self.hud.draw(self.screen, self.plane)
            # Balloons
            for balloon in self.active_balloons:
                balloon.draw(self.screen)
            # Score
            self.points.draw(self.screen)
            # Message
            self.message.draw(self.screen)
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            # Timer
            self.timer.draw(self.screen)
            # Screen shake on hit
            if self.screen_shake > 0:
                self.screen_shake -= 1
            render_offset = [0, 0]
            if self.screen_shake:
                render_offset[0] = random.randint(0, 16) - 8
                render_offset[1] = random.randint(0, 16) - 8
                screen_shake = self.screen
                screen_shake.blit(pygame.transform.scale(self.screen, (800, 600)), render_offset)
                pygame.display.flip()
            else:
                pygame.display.flip()
            # For debug
            self.clock.tick(0)
            # self.clock.tick(self.fps)

    def get_inactive_objects(self, missiles, cruise, drones, balloons):
        for missile in self.enemy_pool:
            if not missile.active:
                if sum(type(obj) == Missile for obj in self.active_enemies) < missiles and type(missile) == Missile:
                    self.active_enemies.append(missile)
                    new_missile = missile
                    if new_missile:
                        new_missile.reset(self.screen, self.plane.position)
                if sum(type(obj) == CruiseMissile for obj in self.active_enemies) < cruise \
                        and type(missile) == CruiseMissile:
                    self.active_enemies.append(missile)
                    new_missile = missile
                    if new_missile:
                        new_missile.reset(self.screen, self.plane.position)
                if sum(type(obj) == Drone for obj in self.active_enemies) < drones and type(missile) == Drone:
                    self.active_enemies.append(missile)
                    new_missile = missile
                    if new_missile:
                        new_missile.reset(self.screen, self.plane.position)
        if len(self.active_balloons) < balloons:
            for balloon in self.balloons_pool:
                if not balloon.active:
                    self.active_balloons.append(balloon)
                    new_balloon = balloon
                    if new_balloon:
                        new_balloon.reset(self.screen)
                    break
