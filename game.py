import pygame
import random
import asyncio
from models import Plane, Missile, CruiseMissile, Drone, Explosion, Bullets, Balloon
from ui import Fade, Cursor, Hud, Points, Message, FPS, Timer, PlaneStart
from screens import Intro, Menu, Pause, Mission, MissionOutcome, End, Leaderboard
import leaderboard
from utilities import load_sprite, load_sound


class JetFighter:
    def __init__(self):

        # Seed the random number generator with the random data
        rng = random.SystemRandom()
        seed = rng.randint(0, 2 ** 32 - 1)
        random.seed(seed)

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
        # Game state
        self.game_state = 'Intro'
        self.level = 1
        # Set bools and counters
        self.dodge = False
        self.dodge_counter = 60
        self.hit = 0
        self.hit_slow_time = 0
        self.screen_shake = 0
        self.end_state = False
        self.end_time = 10
        # Name
        self.name = ''
        # Set fps
        self.fps = 60
        self.fps_display = FPS()
        # Initialize objects
        self.fade = Fade(self.screen)
        self.intro = Intro(self.screen)
        self.plane_start = PlaneStart(self.screen)
        self.menu = Menu(self.screen, self.plane_start)
        self.mission = Mission(self.screen, self.plane_start)
        self.end = End(self.screen)
        self.mission_outcome = MissionOutcome(self.screen, self.plane_start)
        self.leaderboard = Leaderboard(self.screen)
        self.pause = Pause(self.screen)
        self.plane = Plane((400, 300))
        self.cursor = Cursor()
        self.hud = Hud((400, 530))
        self.points = Points()
        self.timer = Timer(30)
        self.message = Message()
        # Music and sounds
        pygame.mixer.set_num_channels(12)
        self.end_music = load_sound('game_over')
        self.background_music = load_sound('music')
        self.sound = False
        self.sound_playing = False
        self.background_music.set_volume(0)
        self.end_music.set_volume(0.2)
        # self.background_music.set_volume(0.1)
        # self.music = False
        self.background_music.play(-1)
        self.sounds = False
        # pygame.mixer.pause()
        # Pre-initialize all the enemy objects and add them to the inactive pool
        # max 3 missiles, max 2 cruise missiles, max 1 drone
        self.enemy_pool = [Missile(self.screen, self.plane.position) for _ in range(3)]
        self.enemy_pool += [CruiseMissile(self.screen, self.plane.position) for _ in range(2)]
        self.enemy_pool.append(Drone(self.screen, self.plane.position))
        self.active_enemies = []
        # Pre-initialize all the balloon objects and add them to the inactive pool - max 3 balloons
        self.balloons_pool = [Balloon(self.screen) for _ in range(3)]
        self.active_balloons = []
        # Pre-initialize all the bullet objects and add them to the inactive pool - max 1 bullets
        self.bullets_pool = [Bullets(self.plane.position, self.plane.direction)]
        self.active_bullets = []
        # Pre-initialize all the explosion objects and add them to the inactive pool - max 10 explosions
        self.explosions_pool = [Explosion((0, 0)) for _ in range(10)]
        self.active_explosions = []

    async def main_loop(self):
        while True:
            self._handle_input()
            self._game_logic()
            self._draw()
            await asyncio.sleep(0)

    def _handle_input(self):
        is_key_pressed = pygame.key.get_pressed()
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                quit()
            # Sound toggle
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_1:
                self.menu.sound_button.switch_symbol()
                self.pause.sound_button.switch_symbol()
                if self.sounds:
                    self.sounds = False
                    self.background_music.set_volume(0)
                    self.plane.fly_sound.set_volume(0)
                    # pygame.mixer.pause()
                else:
                    self.sounds = True
                    # pygame.mixer.unpause()
                    self.background_music.set_volume(0.1)
                    self.plane.fly_sound.set_volume(0.2)

            # FPS toggle
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_2:
                self.fps_display.switch()
            if self.game_state == 'Intro':
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.game_state = 'Menu'
                    self.fade.reset()
                    return
            elif self.game_state == 'Menu':
                self.fps = 60
                menu_command = self.menu.menu_logic(event)
                if menu_command == 'switch_sound':
                    if self.sounds:
                        # pygame.mixer.pause()
                        self.sounds = False
                        self.background_music.set_volume(0)
                        self.plane.fly_sound.set_volume(0)
                    else:
                        # pygame.mixer.unpause()
                        self.sounds = True
                        self.background_music.set_volume(0.1)
                        self.plane.fly_sound.set_volume(0.2)
                elif menu_command:
                    self.name = menu_command
                    return
            elif self.game_state == 'Mission':
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.mission.done = True
                    return
            elif self.game_state == 'Mission outcome':
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.mission_outcome.done = True
                    return
            elif self.game_state == 'End':
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.end.done = True
                    return
            elif self.game_state == 'Leaderboard':
                if event.type == pygame.KEYDOWN or event.type == pygame.MOUSEBUTTONDOWN:
                    self.leaderboard.done = True
                    return
            elif self.game_state == 'Game':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    self.game_state = 'Pause'
                    self.fps = 60
                    self.pause.screenshot(self.screen)
                    return
                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1 \
                        and self.hit < 1 and len(self.active_bullets) < 1:
                    self.get_inactive_bullets(self.sounds, self.plane.position, self.plane.direction)
            elif self.game_state == 'Pause':
                self.fps = 60
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE and not self.pause.back:
                    self.game_state = 'Game'
                    return
                menu_command = self.pause.pause_logic(event)
                if menu_command == 'switch_sound':
                    if self.sounds:
                        # pygame.mixer.pause()
                        self.sounds = False
                        self.background_music.set_volume(0)
                        self.plane.fly_sound.set_volume(0)
                    else:
                        # pygame.mixer.unpause()
                        self.sounds = True
                        self.background_music.set_volume(0.1)
                        self.plane.fly_sound.set_volume(0.2)

        # Keypress in game            
        if self.game_state == 'Game': 
            if is_key_pressed[pygame.K_SPACE] and self.hit < 2:
                if self.sounds:
                    self.plane.thrust(True, True)
                else:
                    self.plane.thrust(True, False)
            elif is_key_pressed[pygame.K_SPACE] and self.hit >= 2:
                if self.sounds:
                    self.plane.thrust(False, True)
                else:
                    self.plane.thrust(False, False)
            else:
                self.plane.refuel()
            if is_key_pressed[pygame.K_LSHIFT] and self.plane.slow_motion():
                pygame.mixer.pause()
                self.fps = 30
                # if self.sounds:
                #     self.plane.swoosh(self.sounds)
            else:
                pygame.mixer.unpause()
                self.plane.refocus()
                self.fps = 60

    @property
    def game_objects(self):
        return [*self.active_enemies, self.plane, *self.active_explosions, *self.active_bullets, *self.active_balloons]

    def _game_logic(self):
        if self.game_state == 'Game':
            # Plane sound
            if self.sounds:
                self.plane.fly_sound.set_volume(0.2)
            else:
                self.plane.fly_sound.set_volume(0)
            if self.hit == 3:
                self.plane.heartbeat(self.sounds)
            # Add new objects
            if self.level == 1:
                self.get_inactive_objects(missiles=0, cruise=0, drones=1, balloons=3)
            elif self.level == 2:
                self.get_inactive_objects(missiles=1, cruise=0, drones=1, balloons=3)
            elif self.level == 3:
                self.get_inactive_objects(missiles=1, cruise=1, drones=1, balloons=3)
            elif self.level == 4:
                self.get_inactive_objects(missiles=3, cruise=1, drones=1, balloons=3)
            elif self.level == 5:
                self.get_inactive_objects(missiles=3, cruise=2, drones=1, balloons=3)
            for obj in self.game_objects:
                obj.move(self.screen)
                if obj == self.plane:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    mouse_position = pygame.math.Vector2(mouse_x, mouse_y)
                    obj.rotate(mouse_position)
                else:
                    obj.rotate(self.plane.position)
                if obj.has_trail:
                    obj.trail()
            for bullet in self.active_bullets:
                if bullet.outside():
                    self.active_bullets.remove(bullet)
                    bullet.active = False
                for missile in self.active_enemies:
                    if bullet.collides_with(missile):
                        self.active_enemies.remove(missile)
                        missile.active = False
                        self.active_bullets.remove(bullet)
                        bullet.active = False
                        self.get_inactive_explosion(missile.position, self.sounds)
                        # self.explosions.append(Explosion(missile.position, self.sounds))
                        self.points.calculate('bullet')
                        break
                for balloon in self.active_balloons:
                    if bullet.collides_with(balloon):
                        self.active_balloons.remove(balloon)
                        balloon.active = False
                        self.active_bullets.remove(bullet)
                        bullet.active = False
                        self.get_inactive_explosion(balloon.position, self.sounds)
                        # self.explosions.append(Explosion(balloon.position, self.sounds))
                        self.points.calculate('bullet')
                        break
            for balloon in self.active_balloons:
                if balloon.collides_with(self.plane):
                    self.active_balloons.remove(balloon)
                    balloon.active = False
                    self.get_inactive_explosion(self.plane.position, self.sounds)
                    # self.explosions.append(Explosion(balloon.position, self.sounds))
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
                    self.get_inactive_explosion(missile.position, self.sounds)
                    # self.explosions.append(Explosion(missile.position, self.sounds))
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
                            self.get_inactive_explosion(missile.position, self.sounds)
                            # self.explosions.append(Explosion(missile.position, self.sounds))
                            self.points.calculate('missile')
                            break
            if self.hit == 4:
                self.end_state = True
            if self.hit_slow_time:
                self.hit_slow_time -= 1
                self.fps = 30
            if self.level == 5:
                self.points.calculate('time')
            self.timer.calculate()

    def _draw(self):
        if self.game_state == 'Intro':
            # show OS cursor
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            if self.intro.draw(self.screen, self.fade) == 'Menu':
                self.game_state = 'Menu'
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
            return
        elif self.game_state == 'Menu':
            if self.menu.draw(self.screen, self.fade, self.sounds) == 'Mission':
                self.game_state = 'Mission'
            # show OS cursor
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
            return
        elif self.game_state == 'Mission':
            if self.mission.draw(self.screen, self.fade, self.plane.position, self.sounds, self.level) == 'Game':
                self.game_state = 'Game'
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
        elif self.game_state == 'Mission outcome':
            if self.mission_outcome.draw(self.screen, self.fade, self.plane.position, self.sounds) == 'Mission':
                self.game_state = 'Mission'
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
        elif self.game_state == 'End':
            # show OS cursor
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            self.background_music.stop()
            if self.end.draw(self.screen, self.fade, self.points.total_points) == 'Leaderboard':
                self.game_state = 'Leaderboard'
                self.leaderboard.update_leaderboard(self.name, self.points.total_points, leaderboard.leaderboard)
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
        elif self.game_state == 'Leaderboard':
            # show OS cursor
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            if self.leaderboard.draw(self.screen, self.fade) == 'Menu':
                self.reset()
                self.game_state = 'Menu'
            # if self.leaderboard.draw(self.screen, self.fade, self.points.total_points) == 'Leaderboard':
            #     self.game_state = 'Leaderboard'
            # FPS
            self.fps_display.draw(self.screen, self.clock.get_fps())
            pygame.display.flip()
            self.clock.tick(self.fps)
        elif self.game_state == 'Pause':
            # show OS cursor
            if not pygame.mouse.get_visible():
                pygame.mouse.set_visible(True)
            pause_result = self.pause.draw(self.screen)
            if pause_result == 'Game':
                self.game_state = 'Game'
            elif pause_result == 'Menu':
                self.game_state = 'Menu'
                self.reset()
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
                    self.active_explosions.remove(obj)
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
            if self.level < 5:
                if self.timer.draw(self.screen) == 'done':
                    self.level += 1
                    self.game_state = 'Mission outcome'
                    if self.hit == 0:
                        self.points.calculate('Intact bonus')
                    self.mission_outcome.set(self.hit, self.points.total_points, self.points.mission_points)
                    self.reset('GameObjects')
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
            # self.clock.tick(0)
            if self.end_state:
                self.fps = 2
                self.end_time -= 1
                self.background_music.fadeout(1000)
                if self.sounds:
                    self.end_music.play()
                if self.end_time == 0:
                    self.game_state = 'End'
                    self.fps = 60
                    self.end_time = 10
                    self.end_state = False
            self.clock.tick(self.fps)

    def get_inactive_objects(self, missiles, cruise, drones, balloons):
        for missile in self.enemy_pool:
            if not missile.active:
                if sum(type(obj) == Missile for obj in self.active_enemies) < missiles and type(missile) == Missile:
                    self.active_enemies.append(missile)
                    new_missile = missile
                    if new_missile:
                        new_missile.set(self.screen, self.plane.position)
                if sum(type(obj) == CruiseMissile for obj in self.active_enemies) < cruise \
                        and type(missile) == CruiseMissile:
                    self.active_enemies.append(missile)
                    new_missile = missile
                    if new_missile:
                        new_missile.set(self.screen, self.plane.position)
                if sum(type(obj) == Drone for obj in self.active_enemies) < drones and type(missile) == Drone:
                    self.active_enemies.append(missile)
                    new_missile = missile
                    if new_missile:
                        new_missile.set(self.screen, self.plane.position)
        if len(self.active_balloons) < balloons:
            for balloon in self.balloons_pool:
                if not balloon.active:
                    self.active_balloons.append(balloon)
                    new_balloon = balloon
                    if new_balloon:
                        new_balloon.reset(self.screen)
                    break

    def get_inactive_explosion(self, position, sound):
        for explosion in self.explosions_pool:
            if not explosion.active:
                self.active_explosions.append(explosion)
                new_explosion = explosion
                if new_explosion:
                    new_explosion.reset(position, sound)
                    break

    def get_inactive_bullets(self, sound, position, direction):
        for bullet in self.bullets_pool:
            if not bullet.active:
                self.active_bullets.append(bullet)
                new_bullet = bullet
                if new_bullet:
                    new_bullet.reset(sound, position, direction)
                    break

    def reset(self, objects='All'):
        for enemy in self.enemy_pool:
            if enemy in self.active_enemies:
                self.active_enemies.remove(enemy)
            enemy.reset(self.screen, self.plane.position)
        for balloon in self.balloons_pool:
            if balloon in self.active_balloons:
                self.active_balloons.remove(balloon)
            balloon.active = False
        for explosion in self.explosions_pool:
            if explosion in self.active_explosions:
                self.active_explosions.remove(explosion)
            explosion.active = False
        self.plane.reset()
        self.dodge = False
        self.dodge_counter = 60
        self.hit = 0
        self.hit_slow_time = 0
        self.screen_shake = 0
        self.fps = 60
        self.hud.reset()
        if self.level == 2:
            self.timer.set_time(30)
        elif self.level == 3:
            self.timer.set_time(45)
        else:
            self.timer.set_time(60)
        self.points.mission_points = 0
        self.fade.reset()
        if objects == 'All':
            self.timer.set_time(30)
            self.level = 1
            self.name = ''
            self.points.total_points = 0
            self.background_music.play(-1)

    def sound_toggle(self):
        if self.sounds:
            pass
