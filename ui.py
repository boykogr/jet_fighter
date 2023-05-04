from utilities import load_sprite, load_sound
import pygame
from pygame.math import Vector2


class Fade:
    def __init__(self, surface):
        self.position = (0, 0)
        self.size = surface.get_size()
        self.black = load_sprite('background4')
        self.black_alpha = 255
        self.black.set_alpha(self.black_alpha)
        self.fade_in = True

    def reset(self):
        self.black_alpha = 255
        self.black.set_alpha(self.black_alpha)
        self.fade_in = True

    def fadein(self, surface, length):
        if self.fade_in:
            if self.black_alpha > 0:
                alpha_increment = 255 / length
                surface.blit(self.black, self.position)
                self.black_alpha -= alpha_increment
                self.black.set_alpha(self.black_alpha)
            else:
                self.black_alpha = 0
                self.black.set_alpha(self.black_alpha)
                surface.blit(self.black, self.position)
                self.fade_in = False
                return 'done'

    def fadeout(self, surface, length):
        if self.fade_in:
            self.black_alpha = 0
            self.fade_in = False
        if self.black_alpha < 255:
            alpha_increment = 255 / length
            surface.blit(self.black, self.position)
            self.black_alpha += alpha_increment
            self.black.set_alpha(self.black_alpha)
        else:
            self.black_alpha = 255
            self.black.set_alpha(self.black_alpha)
            surface.blit(self.black, self.position)
            self.reset()
            return 'done'

    def fade_in_out(self, surface, length1, length2):
        if self.fade_in:
            if self.black_alpha > 0:
                alpha_increment = 255 / length1
                surface.blit(self.black, self.position)
                self.black_alpha -= alpha_increment
                self.black.set_alpha(self.black_alpha)
            else:
                self.black_alpha = 0
                surface.blit(self.black, self.position)
                self.fade_in = False
        else:
            if self.black_alpha < 255:
                alpha_increment = 255 / length2
                surface.blit(self.black, self.position)
                self.black_alpha += alpha_increment
                self.black.set_alpha(self.black_alpha)
            else:
                self.black_alpha = 255
                self.black.set_alpha(self.black_alpha)
                surface.blit(self.black, self.position)
                self.fade_in = True
                return 'done'


class Button:
    def __init__(self, symbol_sprite, center, radius, symbol_sprite2=None):
        self.normal_image = pygame.transform.scale(load_sprite('button'), (radius * 2, radius * 2))
        self.hover_image = pygame.transform.scale(load_sprite('button'), (radius * 2.1, radius * 2.1))
        self.click_image = pygame.transform.scale(load_sprite('button_click'), (radius * 2, radius * 2))
        self.symbol1 = pygame.transform.scale(load_sprite(symbol_sprite), (radius * 2, radius * 2))
        if symbol_sprite2:
            self.symbol2 = pygame.transform.scale(load_sprite(symbol_sprite2), (radius * 2, radius * 2))
            self.symbol_state1 = True
        self.symbol = self.symbol1
        self.image = self.normal_image
        self.center = center
        self.button_rect = self.image.get_rect(center=self.center)
        self.radius = radius
        self.hovered = False
        self.clicked = False
        self.clicked_time = 10
        self.symbol_rect = self.symbol.get_rect(center=self.center)
        # Help text
        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 22)
        if 'start' in symbol_sprite:
            self.text = 'Start Game'
        elif 'help' in symbol_sprite:
            self.text = 'Help'
        elif 'sound' in symbol_sprite:
            self.text = 'Toggle sound'
        elif 'back' in symbol_sprite:
            self.text = 'Go back to menu'
        elif 'continue' in symbol_sprite:
            self.text = 'Continue game'
        else:
            self.text = ''
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(center=self.center + Vector2(0, 70))

    def switch_symbol(self):
        if self.symbol_state1:
            self.symbol = self.symbol2
            self.symbol_state1 = False
        else:
            self.symbol = self.symbol1
            self.symbol_state1 = True

    def draw(self, surface):
        if self.hovered:
            surface.blit(self.text_surface, self.text_rect)
            if self.clicked:
                self.clicked_time -= 1
                if self.clicked_time > 0:
                    self.image = self.click_image
                    self.button_rect = self.image.get_rect(center=self.center)
                else:
                    self.clicked = False
                    self.clicked_time = 10
            else:
                self.image = self.hover_image
                self.button_rect = self.image.get_rect(center=self.center)
        else:
            self.image = self.normal_image
            self.button_rect = self.image.get_rect(center=self.center)
            self.hovered = False
            self.clicked = False
        surface.blit(self.image, self.button_rect)
        surface.blit(self.symbol, self.symbol_rect)


class Cursor:
    def __init__(self):
        self.sprite = load_sprite('cursor1')
        self.radius = 20.5
        self.position = pygame.mouse.get_pos()

    def draw(self, surface):
        self.position = pygame.mouse.get_pos()
        position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, position)


class Hud:
    def __init__(self, position):
        self.thrust_images = {0: 'thrust0', 1: 'thrust10', 2: 'thrust20', 3: 'thrust30',
                              4: 'thrust40', 5: 'thrust50', 6: 'thrust60', 7: 'thrust70',
                              8: 'thrust80', 9: 'thrust90', 10: 'thrust100', 11: 'thrust_out'}
        # Load all the sprites and store them in a dictionary
        self.thrust_sprites = {percent: load_sprite(filename) for percent, filename in self.thrust_images.items()}

        self.focus_images = {0: 'focus0', 1: 'focus10', 2: 'focus20', 3: 'focus30',
                             4: 'focus40', 5: 'focus50', 6: 'focus60', 7: 'focus70',
                             8: 'focus80', 9: 'focus90', 10: 'focus100'}
        # Load all the sprites and store them in a dictionary
        self.focus_sprites = {percent: load_sprite(filename) for percent, filename in self.focus_images.items()}

        self.plane_sprite1 = load_sprite('hud_plane1')
        self.plane_sprite2 = load_sprite('hud_plane2')
        self.plane_sprite3 = load_sprite('hud_plane3')
        self.plane_sprite4 = load_sprite('hud_plane4')

        self.position = Vector2(position)
        self.offset = Vector2(60, 40)
        self.focus = 60
        self.thrust = 60
        self.hits = 0
        self.blink_counter = 0
        self.blink0 = True

    def reset(self):
        self.focus = 60
        self.thrust = 60
        self.hits = 0
        self.blink_counter = 0
        self.blink0 = True

    def hit(self):
        self.hits += 1
        self.blink_counter = 0
        self.blink0 = True

    def draw(self, surface, plane):
        if self.hits == 0:
            self.thrust = plane.fuel
            t_percent = int(self.thrust / 60 * 100) // 10
            thrust_image = self.thrust_sprites[t_percent]

            self.focus = plane.focus
            t_percent = int(self.focus / 60 * 100) // 10
            focus_image = self.focus_sprites[t_percent]

            position = self.position - Vector2(self.offset)
            surface.blit(thrust_image, position)
            surface.blit(focus_image, position)

            surface.blit(self.plane_sprite1, position)
        elif self.hits == 1:
            self.thrust = plane.fuel
            t_percent = int(self.thrust / 60 * 100) // 10
            thrust_image = self.thrust_sprites[t_percent]

            self.focus = plane.focus
            t_percent = int(self.focus / 60 * 100) // 10
            focus_image = self.focus_sprites[t_percent]

            position = self.position - Vector2(self.offset)
            surface.blit(thrust_image, position)
            surface.blit(focus_image, position)

            self.blink_counter += 1
            if self.blink_counter == 30:
                if self.blink0:
                    surface.blit(self.plane_sprite2, position)
                    self.blink0 = False
                else:
                    surface.blit(self.plane_sprite1, position)
                    self.blink0 = True
                self.blink_counter = 0
            else:
                if self.blink0:
                    surface.blit(self.plane_sprite1, position)
                else:
                    surface.blit(self.plane_sprite2, position)

        elif self.hits == 2:
            # thrust_image = self.thrust_sprites[11]
            self.thrust = plane.fuel
            t_percent = int(self.thrust / 60 * 100) // 100
            thrust_image = self.thrust_sprites[t_percent]

            self.focus = plane.focus
            t_percent = int(self.focus / 60 * 100) // 10
            focus_image = self.focus_sprites[t_percent]

            position = self.position - Vector2(self.offset)
            surface.blit(thrust_image, position)
            surface.blit(focus_image, position)

            self.blink_counter += 1
            if self.blink_counter == 30:
                if self.blink0:
                    surface.blit(self.plane_sprite3, position)
                    self.blink0 = False
                else:
                    surface.blit(self.plane_sprite1, position)
                    self.blink0 = True
                self.blink_counter = 0
            else:
                if self.blink0:
                    surface.blit(self.plane_sprite1, position)
                else:
                    surface.blit(self.plane_sprite3, position)
        elif self.hits == 3:
            # thrust_image = self.thrust_sprites[11]
            self.thrust = plane.fuel
            t_percent = int(self.thrust / 60 * 100) // 100
            thrust_image = self.thrust_sprites[t_percent]

            self.focus = plane.focus
            t_percent = int(self.focus / 120 * 100) // 10
            focus_image = self.focus_sprites[t_percent]

            position = self.position - Vector2(self.offset)
            surface.blit(thrust_image, position)
            surface.blit(focus_image, position)
            self.blink_counter += 1
            if self.blink_counter == 30:
                if self.blink0:
                    surface.blit(self.plane_sprite4, position)
                    self.blink0 = False
                else:
                    surface.blit(self.plane_sprite1, position)
                    self.blink0 = True
                self.blink_counter = 0
            else:
                if self.blink0:
                    surface.blit(self.plane_sprite1, position)
                else:
                    surface.blit(self.plane_sprite4, position)


class Points:
    def __init__(self):
        self.position = (10, 10)
        self.second = 60
        self.total_points = 0
        self.mission_points = 0
        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 24)
        self.score_gained = 0
        self.score_gained_timer = 90

    def calculate(self, score_type):
        if score_type == 'time':
            self.second -= 1
            if self.second == 0:
                self.score_gained = 1
                self.total_points += self.score_gained
                self.mission_points += self.score_gained
                self.second = 60
        if score_type == 'bullet':
            self.score_gained = 10
        elif score_type == 'missile':
            self.score_gained = 20
        elif score_type == 'dodge':
            self.score_gained = 30
        elif score_type == 'balloon':
            self.score_gained = 20
        elif score_type == 'Penalty':
            self.score_gained = -20
        elif score_type == 'Intact bonus':
            self.score_gained = 200
        else:
            self.score_gained = 0
        self.total_points += self.score_gained
        self.mission_points += self.score_gained

    def draw(self, surface):
        if self.score_gained != 0:
            self.score_gained_timer -= 1
            if self.score_gained_timer > 0:
                if self.score_gained > 0:
                    text = f'SCORE: {self.total_points} +{self.score_gained}'
                else:
                    text = f'SCORE: {self.total_points} {self.score_gained}'
            else:
                self.score_gained_timer = 90
                self.score_gained = 0
                text = f'SCORE: {self.total_points}'
        else:
            text = f'SCORE: {self.total_points}'
        text_surface = self.font.render(text, True, (255, 255, 255))
        surface.blit(text_surface, self.position)


class Message:
    color1 = (255, 255, 255)
    color2 = (255, 0, 0)

    def __init__(self):
        self.time = 180
        self.blink = 20
        self.font1 = pygame.font.Font('assets/fonts/the unseen.ttf', 24)
        self.font2 = pygame.font.Font('assets/fonts/the unseen.ttf', 28)
        self.text = ''
        self.font = self.font1
        self.color = self.color1

    def take(self, plane_hit):
        if plane_hit == -1:
            self.text = 'Perfect dodge!'
        elif plane_hit == 1:
            self.text = 'You got hit. Weapons failure!'
        elif plane_hit == 2:
            self.text = 'You got hit. Thrusters failure!'
        elif plane_hit == 3:
            self.text = 'Systems failure! Last chance!'

    def draw(self, surface):
        if self.text:
            self.time -= 1
            self.blink -= 1
            if self.time == 0:
                self.time = 180
                self.blink = 20
                self.text = ''
            elif self.blink == 0:
                self.blink = 20
                self.font = self.font2 if self.font == self.font1 else self.font1
                self.color = self.color2 if self.color == self.color1 else self.color1

            text_surface = self.font.render(self.text, True, self.color)
            rect = text_surface.get_rect()
            rect.center = (400, 30)
            surface.blit(text_surface, rect)


class FPS:
    def __init__(self):
        self.position = (10, 570)
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font("assets/fonts/the unseen.ttf", 20)
        self.visible = False

    def draw(self, surface, clock):
        if self.visible:
            text = f'FPS: {round(clock)}'
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, self.position)

    def switch(self):
        if self.visible:
            self.visible = False
        else:
            self.visible = True


class Timer:
    def __init__(self, seconds):
        self.position = (385, 575)
        self.font = pygame.font.Font("assets/fonts/the unseen.ttf", 20)
        self.seconds = seconds
        self.second = 60
        self.start = True
        self.start_benchmark = 0
        self.benchmark = False

    def set_time(self, seconds):
        self.seconds = seconds

    def calculate(self):
        if self.start:
            # self.start_benchmark = pygame.time.get_ticks()
            self.start = False
        self.second -= 1
        if self.second == 0:
            self.seconds -= 1
            self.second = 60

    def draw(self, surface):
        if self.seconds > 0:
            minutes = self.seconds // 60
            seconds = self.seconds % 60
            text = f'{minutes}:{seconds:02d}'
        else:
            # if self.benchmark:
            #     end_benchmark = pygame.time.get_ticks()
            #     benchmark = (end_benchmark - self.start_benchmark)
            #     print(f'Time: {benchmark}')
            #     self.benchmark = False
            text = '0:00'
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, self.position)
            self.set_time(30)
            return 'done'
        text_surface = self.font.render(text, True, (255, 255, 255))
        surface.blit(text_surface, self.position)


class PlaneStart:
    def __init__(self, surface):
        self.direction = Vector2(0, -1)
        self.sprite = load_sprite('plane_start')
        self.size = self.sprite.get_size()
        self.center = self.sprite.get_rect().center
        self.start_position = (surface.get_size()[0] // 2, surface.get_size()[1] // 2 - 100)
        self.position = self.start_position
        self.start_sound = load_sound('start')
        self.start_sound.set_volume(0.5)
        self.sound = False
        self.sound_playing = False
        self.decrement = 2
        self.percent_start = 100
        self.percent_end = 5
        self.appear = True
        self.start = True
        self.end = True
        self.speed = 1.1
        self.velocity = self.direction * self.speed

    def draw(self, surface, plane_position, sound, plane_state='static'):
        if plane_state == 'intro':
            if self.appear:
                if self.decrement < 100:
                    self.decrement += 1
                    new_width = self.sprite.get_width() * self.decrement/100
                    new_height = self.sprite.get_height() * self.decrement/100
                    new_sprite = pygame.transform.scale(self.sprite, (new_width, new_height))
                    new_center = new_sprite.get_rect().center
                    new_position = self.position - Vector2(new_center)
                    surface.blit(new_sprite, new_position)
                else:
                    surface.blit(self.sprite, self.position - Vector2(self.center))
                    self.appear = False
                    self.start = True
                    self.decrement = 2
            else:
                surface.blit(self.sprite, self.position - Vector2(self.center))
        elif plane_state == 'start':
            if self.start:
                self.sound = sound
                if self.sound and not self.sound_playing:
                    self.start_sound.play()
                    self.sound_playing = True
                # Rotate
                # Get the vector from the plane position to the mouse position
                target_direction = Vector2(plane_position) - self.position
                # Get the angle between the current direction and target direction
                rotation_angle = round(self.direction.angle_to(target_direction))
                self.direction.rotate_ip(rotation_angle)
                # Move
                self.velocity = self.direction * self.speed
                self.position = self.position + self.velocity
                
                if self.percent_start > 6:
                    self.percent_start -= 1
                    new_width = self.sprite.get_width() * self.percent_start / 100
                    new_height = self.sprite.get_height() * self.percent_start / 100
                    new_sprite = pygame.transform.scale(self.sprite, (new_width, new_height))
                    self.center = new_sprite.get_rect().center
                    new_position = self.position - Vector2(self.center)
                    surface.blit(new_sprite, new_position)
                else:
                    self.start = False
                    self.appear = True
                    self.percent_start = 100
                    self.position = self.start_position
                    self.center = self.sprite.get_rect().center
                    self.sound_playing = False
                    return 'done'
        if plane_state == 'static':
            self.appear = True
            self.start = True
            surface.blit(self.sprite, self.position - Vector2(self.center))
