from utilities import load_sprite
import pygame
from pygame.math import Vector2
from random import choice


class Intro:
    def __init__(self, surface):
        self.intro = load_sprite('Intro1', False)
        self.position = (0, 0)
        self.size = pygame.display.get_window_size()
        self.fade_length = 120

        self.black = pygame.Surface(self.size)
        self.black.fill((0, 0, 0))
        surface.blit(self.black, self.position)

    def draw(self, surface):
        self.fade_length -= 1
        if self.fade_length > 0:
            self.intro.set_alpha(-self.fade_length + 120)
            surface.blit(self.intro, self.position)
        elif self.fade_length == 0:
            self.intro.set_alpha(255)
            surface.blit(self.intro, self.position)
        elif -70 < self.fade_length <= 0:
            self.black.set_alpha(-self.fade_length)
            surface.blit(self.black, self.position)
        elif self.fade_length == -70:
            self.black.set_alpha(255)
            surface.blit(self.black, self.position)
            return 'Menu'


class Menu:
    def __init__(self, surface):
        self.menu = load_sprite('Intro2', False)
        self.position = (0, 0)
        self.size = pygame.display.get_window_size()
        self.fade_length = 120

        self.black = pygame.Surface(self.size)
        self.black.fill((0, 0, 0))
        surface.blit(self.black, self.position)

        # Define font and text
        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 22)
        names = ['Dead Baron', 'Jet Lee', 'Yossarian', 'Ace Ventura', 'Maverick',
                 'Little Dick', 'Joan Jet', 'Jet Hrotull', 'Captain Major', 'Kamikaze Girl']
        default_text = choice(names)
        self.text = default_text

        # Create input box
        self.input_sprite = load_sprite('menu_input')
        self.input_sprite_hover = load_sprite('menu_input_hover')
        self.input_box = self.input_sprite
        self.input_box_rect = self.input_box.get_rect(center=(self.size[0] / 2, (self.size[1] / 2) + 80))
        self.active = False
        self.input_counter = 0
        self.input_line = True

        # Create start button
        self.start_button = pygame.Rect(150, 200, 100, 50)
        self.start_sprite = load_sprite('menu_start')
        self.start_sprite_hover = load_sprite('menu_start_hover')
        self.start_button = self.start_sprite
        self.start_button_rect = self.start_button.get_rect(center=(self.size[0] / 2, (self.size[1] / 2) + 150))

    def menu_logic(self):
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEMOTION:
                # Change boxes sprites to indicate if the cursor is over them
                if self.input_box_rect.collidepoint(event.pos):
                    self.input_box = self.input_sprite_hover
                else:
                    self.input_box = self.input_sprite
                if self.start_button_rect.collidepoint(event.pos):
                    self.start_button = self.start_sprite_hover
                else:
                    self.start_button = self.start_sprite
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if user clicked on input box
                if self.input_box_rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
                # Check if user clicked on start button
                if self.start_button_rect.collidepoint(event.pos):
                    if self.text:
                        return 'Game'
                    else:
                        self.text = 'Empty loser'
                        return 'Game'
            if event.type == pygame.KEYDOWN:
                # Check if user typed a key while input box is active
                if self.active:
                    if event.key == pygame.K_RETURN:
                        self.active = False
                    elif event.key == pygame.K_BACKSPACE:
                        self.text = self.text[:-1]
                    elif len(self.text) < 16 and (event.unicode.isalpha() or event.key == pygame.K_SPACE):
                        self.text += event.unicode

    def draw(self, surface):
        # Fade in menu screen
        self.fade_length -= 1
        if self.fade_length > 0:
            self.menu.set_alpha(-self.fade_length + 120)
            surface.blit(self.menu, self.position)
        else:
            self.menu.set_alpha(255)
            surface.blit(self.menu, self.position)

            # Draw the input box and text
            surface.blit(self.input_box, self.input_box_rect)
            prefix = 'Pilot: '
            full_text = prefix + self.text
            if self.active:
                self.input_counter += 1
                if self.input_line:
                    if self.input_counter == 30:
                        self.input_line = False
                        self.input_counter = 0
                        text_surface = self.font.render(full_text, True, (255, 255, 255))
                    else:
                        text_surface = self.font.render(full_text + '|', True, (255, 255, 255))
                else:
                    if self.input_counter == 30:
                        self.input_line = True
                        self.input_counter = 0
                        text_surface = self.font.render(full_text + '|', True, (255, 255, 255))
                    else:
                        text_surface = self.font.render(full_text, True, (255, 255, 255))
            else:
                text_surface = self.font.render(full_text, True, (255, 255, 255))
            surface.blit(text_surface, (self.input_box_rect.x + 15, self.input_box_rect.y + 12))

            # Draw the start button
            surface.blit(self.start_button, self.start_button_rect)


class Pause:
    def __init__(self):
        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 26)
        self.position = (0, 0)
        self.size = pygame.display.get_window_size()

        self.continue_button = pygame.Rect(150, 200, 100, 50)
        self.continue_sprite = load_sprite('menu_button')
        self.continue_sprite_hover = load_sprite('menu_button_hover')
        self.continue_button = self.continue_sprite
        self.continue_button_rect = self.continue_button.get_rect(center=(self.size[0] / 2, (self.size[1] / 2) - 100))
        self.continue_text = 'Continue'

        self.menu_button = pygame.Rect(150, 200, 100, 50)
        self.menu_sprite = load_sprite('menu_button')
        self.menu_sprite_hover = load_sprite('menu_button_hover')
        self.menu_button = self.menu_sprite
        self.menu_button_rect = self.menu_button.get_rect(center=(self.size[0] / 2, (self.size[1] / 2)))
        self.menu_text = 'Menu'

        self.exit_button = pygame.Rect(150, 200, 100, 50)
        self.exit_sprite = load_sprite('menu_button')
        self.exit_sprite_hover = load_sprite('menu_button_hover')
        self.exit_button = self.exit_sprite
        self.exit_button_rect = self.exit_button.get_rect(center=(self.size[0] / 2, (self.size[1] / 2) + 100))
        self.exit_text = 'Exit'

    def pause_logic(self):
        # Check for events
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()
            if event.type == pygame.MOUSEMOTION:
                # Change boxes sprites to indicate if the cursor is over them
                if self.continue_button_rect.collidepoint(event.pos):
                    self.continue_button = self.continue_sprite_hover
                else:
                    self.continue_button = self.continue_sprite
                if self.menu_button_rect.collidepoint(event.pos):
                    self.menu_button = self.menu_sprite_hover
                else:
                    self.menu_button = self.menu_sprite
                if self.exit_button_rect.collidepoint(event.pos):
                    self.exit_button = self.exit_sprite_hover
                else:
                    self.exit_button = self.exit_sprite
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check if user clicked on start button
                if self.continue_button_rect.collidepoint(event.pos):
                    return 'Game'
                if self.menu_button_rect.collidepoint(event.pos):
                    return 'Menu'
                if self.exit_button_rect.collidepoint(event.pos):
                    quit()

    def draw(self, surface):
        # Draw the buttons
        surface.blit(self.continue_button, self.continue_button_rect)
        text_surface = self.font.render(self.continue_text, True, (0, 0, 0))
        text_center = (self.continue_button_rect.centerx - text_surface.get_size()[0] // 2,
                       self.continue_button_rect.centery - text_surface.get_size()[1] // 2)
        surface.blit(text_surface, text_center)

        surface.blit(self.menu_button, self.menu_button_rect)
        text_surface = self.font.render(self.menu_text, True, (0, 0, 0))
        text_center = (self.menu_button_rect.centerx - text_surface.get_size()[0] // 2,
                       self.menu_button_rect.centery - text_surface.get_size()[1] // 2)
        surface.blit(text_surface, text_center)

        surface.blit(self.exit_button, self.exit_button_rect)
        text_surface = self.font.render(self.exit_text, True, (0, 0, 0))
        text_center = (self.exit_button_rect.centerx - text_surface.get_size()[0] // 2,
                       self.exit_button_rect.centery - text_surface.get_size()[1] // 2)
        surface.blit(text_surface, text_center)


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
        self.points = 0
        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 24)
        self.score_gained = 0
        self.score_gained_timer = 90

    def calculate(self, score_type):
        if score_type == 'time':
            self.second -= 1
            if self.second == 0:
                self.points += 1
                self.second = 60
        if score_type == 'bullet':
            self.score_gained = 10
            self.points += self.score_gained
        elif score_type == 'missile':
            self.score_gained = 20
            self.points += self.score_gained
        elif score_type == 'dodge':
            self.score_gained = 30
            self.points += self.score_gained
        elif score_type == 'balloon':
            self.score_gained = 20
            self.points += self.score_gained
        if score_type == 'Penalty':
            self.score_gained = -20
            self.points += self.score_gained

    def draw(self, surface):
        if self.score_gained != 0:
            self.score_gained_timer -= 1
            if self.score_gained_timer > 0:
                if self.score_gained > 0:
                    text = f'SCORE: {self.points} +{self.score_gained}'
                else:
                    text = f'SCORE: {self.points} {self.score_gained}'
            else:
                self.score_gained_timer = 90
                self.score_gained = 0
                text = f'SCORE: {self.points}'
        else:
            text = f'SCORE: {self.points}'
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
        elif plane_hit == 4:
            self.text = 'You are dead'

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

    def draw(self, surface, clock):
        text = f'FPS: {round(clock)}'
        text_surface = self.font.render(text, True, (255, 255, 255))
        surface.blit(text_surface, self.position)


class Timer:
    def __init__(self, seconds):
        self.position = (385, 575)
        self.font = pygame.font.Font("assets/fonts/the unseen.ttf", 20)
        self.seconds = seconds
        self.second = 60
        self.start = True
        self.start_benchmark = 0
        self.benchmark = True

    def calculate(self):
        if self.start:
            self.start_benchmark = pygame.time.get_ticks()
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
            if self.benchmark:
                end_benchmark = pygame.time.get_ticks()
                benchmark = (end_benchmark - self.start_benchmark)
                print(f'Time: {benchmark}')
                self.benchmark = False
            text = '0:00'
        text_surface = self.font.render(text, True, (255, 255, 255))
        surface.blit(text_surface, self.position)

'''
Benchmark results (real time for 1 in-game minute):
Nothing: ~2300 ms.
3 balloons: ~2500 ms.
1 drone: ~4000 ms.
2 missile: ~7500 ms.
2 cruise: ~7500 ms.
3 missile: ~9500 ms.
3 missile, 3 balloons: ~10000 ms.
All 3 missile, 2 cruise, 1 drone, 3 balloons: ~17000 ms.
All/No screen shake: ~15000 ms.
All/No explosion draw: ~15500 ms.
All/No trails: ~5800 ms. !!!
'''
