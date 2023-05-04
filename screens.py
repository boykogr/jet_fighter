from utilities import load_sprite, load_sound
import pygame
from pygame.math import Vector2
from ui import Button
import text_data
import random


class Intro:
    def __init__(self, surface):
        self.intro = load_sprite('Intro1', False)
        self.position = (0, 0)
        self.size = surface.get_size()

    def draw(self, surface, fade):
        surface.blit(self.intro, self.position)
        # Fade in/out
        if fade.fade_in_out(surface, 120, 60) == 'done':
            fade.reset()
            return 'Menu'


class Menu:
    def __init__(self, surface, plane_start):
        self.menu = load_sprite('Intro2', False)
        self.help_image = load_sprite('help', False)
        self.help = False
        self.plane_start = plane_start
        self.position = (0, 0)
        self.size = surface.get_size()
        self.start = False

        # Define font and text
        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 22)
        self.text = random.choice(text_data.default_names)
        # Chosen name
        self.font_size = 2
        self.font_name = pygame.font.Font('assets/fonts/SaucerBB.ttf', self.font_size)
        self.name = self.text
        self.name_chosen = False
        self.name_appeared = False
        # Create input box
        self.input_sprite = load_sprite('menu_input')
        self.input_sprite_hover = load_sprite('menu_input_hover')
        self.input_box = self.input_sprite
        self.input_box_rect = self.input_box.get_rect(center=(self.size[0] / 2, (self.size[1] / 2) + 70))
        self.active = False
        self.input_counter = 0
        self.input_line = True

        # Create start button
        self.start_button = Button('button_start', (400, 460), 52)
        self.help_button = Button('button_help', (250, 460), 40)
        self.sound_button = Button('button_sound2', (550, 460), 40, 'button_sound')

    def reset(self):
        self.help = False
        self.start = False
        self.text = random.choice(text_data.default_names)
        self.name = self.text
        self.name_chosen = False
        self.name_appeared = False
        self.font_size = 2
        self.active = False
        self.input_counter = 0
        self.input_line = True

    def check_text(self, text):
        forbidden = ['putin', 'hitler', 'stalin', 'boyko', 'gramenov']
        user_input = text.lower()
        # Convert user input to lowercase
        for word in forbidden:
            if word.lower() in user_input:
                user_input = user_input.replace(word, '*' * len(word))
        self.text = user_input

    def menu_logic(self, event):
        # Check for events
        if event.type == pygame.MOUSEMOTION and not self.help:
            # Change sprites to indicate if the cursor is over them
            if self.input_box_rect.collidepoint(event.pos):
                self.input_box = self.input_sprite_hover
            else:
                self.input_box = self.input_sprite

            if Vector2(self.start_button.center).distance_to(event.pos) <= self.start_button.radius:
                self.start_button.hovered = True
            else:
                self.start_button.hovered = False
            if Vector2(self.help_button.center).distance_to(event.pos) <= self.help_button.radius:
                self.help_button.hovered = True
            else:
                self.help_button.hovered = False
            if Vector2(self.sound_button.center).distance_to(event.pos) <= self.sound_button.radius:
                self.sound_button.hovered = True
            else:
                self.sound_button.hovered = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if not self.name_chosen:
                # Check if user clicked on input box
                if self.input_box_rect.collidepoint(event.pos):
                    self.active = True
                else:
                    self.active = False
            if self.help:
                self.help = False
                return
            if Vector2(self.start_button.center).distance_to(event.pos) <= self.start_button.radius:
                self.start_button.clicked = True
                self.start = True
                # Check if user emptied the name
                if not self.text:
                    self.text = random.choice(text_data.empty_names)
                self.check_text(self.text)
                self.name = self.text
                self.name_chosen = True
                return self.name
            else:
                self.start_button.clicked = False
            if Vector2(self.help_button.center).distance_to(event.pos) <= self.help_button.radius:
                self.help_button.clicked = True
                self.help = True
            else:
                self.help_button.clicked = False
            if Vector2(self.sound_button.center).distance_to(event.pos) <= self.sound_button.radius:
                self.sound_button.clicked = True
                self.sound_button.switch_symbol()
                return 'switch_sound'
            else:
                self.sound_button.clicked = False
        if event.type == pygame.KEYDOWN and self.help:
            self.help = False
        # Check if user typed a key while input box is active    
        if event.type == pygame.KEYDOWN and self.active:
            if event.key == pygame.K_RETURN:
                if not self.text:
                    self.text = random.choice(text_data.empty_names)
                self.check_text(self.text)
                self.name = self.text
                self.name_chosen = True
                self.active = False
                return self.name
            elif event.key == pygame.K_BACKSPACE:
                self.text = self.text[:-1]
            elif len(self.text) < 17 and (event.unicode.isalpha() or event.key == pygame.K_SPACE):
                self.text += event.unicode

    def draw(self, surface, fade, sound):
        if self.help:
            surface.blit(self.help_image, self.position)
            return
        surface.blit(self.menu, self.position)
        self.plane_start.draw(surface, 1, sound, 'intro')
        # self.plane_start.draw(surface)

        # Draw the start button
        self.start_button.draw(surface)
        self.help_button.draw(surface)
        self.sound_button.draw(surface)

        # Draw the input box and text
        if not self.name_chosen:
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
        else:
            self.font_name = pygame.font.Font('assets/fonts/SaucerBB.ttf', self.font_size)
            name_surface = self.font_name.render(self.name, True, (255, 255, 255))
            name_rect = name_surface.get_rect(center=(400, 365))
            surface.blit(name_surface, name_rect)
            if self.font_size < 44:
                self.font_size += 1
                if self.font_size == 44:
                    self.name_appeared = True
        
        # Fade in
        fade.fadein(surface, 60)

        if self.start:
            if self.name_appeared:
                if fade.fadeout(surface, 60) == 'done':
                    self.start = False
                    self.plane_start.draw(surface, 1, sound, 'intro')
                    fade.reset()
                    self.reset()
                    return 'Mission'

        self.plane_start.draw(surface, 1, sound, 'intro')


class Pause:
    def __init__(self, surface):
        self.position = (0, 0)
        self.size = pygame.display.get_window_size()
        self.resume = False
        self.back = False
        self.pause = surface.copy()
        self.background = False
        self.black = load_sprite('background4')
        self.black.set_alpha(120)
        self.back_image = load_sprite('help', False)
        self.timer = 30

        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 42)
        self.text = 'PAUSED'
        self.text_surface = self.font.render(self.text, True, (255, 255, 255))
        self.text_rect = self.text_surface.get_rect(center=(400, 300))
        
        self.resume_button = Button('button_start', (400, 420), 52)
        self.back_button = Button('button_help', (250, 420), 40)
        self.sound_button = Button('button_sound2', (550, 420), 40, 'button_sound')

    def screenshot(self, surface):
        self.pause = surface.copy()

    def pause_logic(self, event):
        # Check for events
        if event.type == pygame.MOUSEMOTION and not self.back:
            if Vector2(self.resume_button.center).distance_to(event.pos) <= self.resume_button.radius:
                self.resume_button.hovered = True
            else:
                self.resume_button.hovered = False
            if Vector2(self.back_button.center).distance_to(event.pos) <= self.back_button.radius:
                self.back_button.hovered = True
            else:
                self.back_button.hovered = False
            if Vector2(self.sound_button.center).distance_to(event.pos) <= self.sound_button.radius:
                self.sound_button.hovered = True
            else:
                self.sound_button.hovered = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if self.back:
                self.back = False
                return
            if Vector2(self.resume_button.center).distance_to(event.pos) <= self.resume_button.radius:
                self.resume_button.clicked = True
                self.resume = True
            else:
                self.resume_button.clicked = False
            if Vector2(self.back_button.center).distance_to(event.pos) <= self.back_button.radius:
                self.back_button.clicked = True
                self.back = True
            else:
                self.back_button.clicked = False
            if Vector2(self.sound_button.center).distance_to(event.pos) <= self.sound_button.radius:
                self.sound_button.clicked = True
                self.sound_button.switch_symbol()
                return 'switch_sound'
            else:
                self.sound_button.clicked = False
        if event.type == pygame.KEYDOWN and self.back:
            self.back = False

    def draw(self, surface):
        if self.back:
            surface.blit(self.back_image, self.position)
            return
        # Background
        surface.blit(self.pause, self.position)
        surface.blit(self.black, self.position)
        # Text
        surface.blit(self.text_surface, self.text_rect)
        # Buttons
        self.resume_button.draw(surface)
        self.back_button.draw(surface)
        self.sound_button.draw(surface)
        if self.resume:
            surface.blit(self.pause, self.position)
            self.timer -= 1
            if self.timer == 0:
                self.resume = False
                self.back = False
                self.timer = 30
                return 'Game'
        # if self.back:
        #     self.back = False
        #     self.timer = 30
        #     return 'Menu'


class End:
    def __init__(self, surface):
        self.background = load_sprite('background4')
        self.end = load_sprite('end')
        self.screenshot = surface.copy()
        self.end_size = self.end.get_size()
        self.end_center = self.end.get_rect().center
        self.screen_center = (surface.get_size()[0] // 2, surface.get_size()[1] // 2)
        self.end_position = self.screen_center - Vector2(self.end_center) + Vector2(0, -180)
        self.done = False
        self.fadeout_done = False
        self.text = random.choice(text_data.end_texts)
        # Define font and text
        self.font1 = pygame.font.Font('assets/fonts/the unseen.ttf', 24)

    def print_text(self, surface):
        next_line = 50
        for line in self.text:
            if 'Press' in line:
                text_surface = self.font1.render(line, True, (100, 100, 100))
            else:
                text_surface = self.font1.render(line, True, (255, 255, 255))
            rect = text_surface.get_rect()
            rect.center = (self.screen_center - Vector2(0, next_line))
            surface.blit(text_surface, rect)
            next_line -= 35

    def draw(self, surface, fade, points):
        text = f'Final fame achieved: {points}'
        if not self.done:
            # Background
            surface.blit(self.background, (0, 0))
            # mission
            surface.blit(self.end, self.end_position)
            # texts
            text_surface = self.font1.render(text, True, (255, 255, 255))
            rect = text_surface.get_rect()
            rect.center = (self.screen_center - Vector2(0, 100))
            surface.blit(text_surface, rect)
            self.print_text(surface)
            # Fade in
            fade.fadein(surface, 60)
            # Plane
        else:
            # Background
            surface.blit(self.background, (0, 0))
            if not self.fadeout_done:
                # mission
                surface.blit(self.end, self.end_position)
                # texts
                text_surface = self.font1.render(text, True, (255, 255, 255))
                rect = text_surface.get_rect()
                rect.center = (self.screen_center - Vector2(0, 100))
                surface.blit(text_surface, rect)
                self.print_text(surface)
                # Fade out
                if fade.fadeout(surface, 60) == 'done':
                    self.done = False
                    self.fadeout_done = False
                    self.text = random.choice(text_data.end_texts)
                    fade.reset()
                    return 'Leaderboard'


class Leaderboard:
    def __init__(self, surface):
        self.background = load_sprite('background4')
        self.leaderboard = load_sprite('leaderboard')
        self.leaderboard_size = self.leaderboard.get_size()
        self.leaderboard_center = self.leaderboard.get_rect().center
        self.screen_center = (surface.get_size()[0] // 2, surface.get_size()[1] // 2)
        self.leaderboard_position = self.screen_center - Vector2(self.leaderboard_center) + Vector2(0, -180)
        self.done = False
        self.fadeout_done = False
        self.text = []
        self.made_leaderboard = False
        # Define font and text
        self.font1 = pygame.font.Font('assets/fonts/the unseen.ttf', 24)
        self.font2 = pygame.font.Font('assets/fonts/SaucerBB.ttf', 24)

    def print_text(self, surface):
        if not self.made_leaderboard:
            text1 = f"You didn't make it to the leaderboard."
        else:
            text1 = f'Congratulations, you made it to the leaderboard.'
        text2 = 'Press any key to continue'
        self.text.append('')
        self.text.append(text1)
        self.text.append(text2)

        next_line = 120
        for line in self.text:
            if 'Press' in line:
                text_surface = self.font1.render(line, True, (100, 100, 100))
            elif 'to the leaderboard.' in line:
                text_surface = self.font1.render(line, True, (255, 255, 255))
            else:
                text_surface = self.font2.render(line, True, (255, 255, 255))
            rect_position = (self.screen_center - Vector2(200, next_line))
            surface.blit(text_surface, rect_position)
            next_line -= 30

    def update_leaderboard(self, name, score, leaderboard):
        lowest_score = min(i[1] for i in leaderboard)
        if score > lowest_score:
            self.made_leaderboard = True
            leaderboard.pop()
            leaderboard.append([name, score])
            leaderboard.sort(key=lambda x: x[1], reverse=True)

            # write the updated leaderboard to a file
            with open("leaderboard.py", "w") as file:
                file.write("leaderboard = [\n")
                for li in leaderboard:
                    file.write(f"{li},\n")
                file.write("]\n")

        for i in range(len(leaderboard)):
            text = f"{i + 1}. {leaderboard[i][0]} : {leaderboard[i][1]}"
            self.text.append(text)

    def draw(self, surface, fade):
        if not self.done:
            # Background
            surface.blit(self.background, (0, 0))
            # Header
            surface.blit(self.leaderboard, self.leaderboard_position)
            # Leaderboard
            self.print_text(surface)
            # Fade in
            fade.fadein(surface, 60)
        else:
            # Background
            surface.blit(self.background, (0, 0))
            if not self.fadeout_done:
                # Background
                surface.blit(self.background, (0, 0))
                # Header
                surface.blit(self.leaderboard, self.leaderboard_position)
                # Leaderboard
                self.print_text(surface)
                # Fade out
                if fade.fadeout(surface, 60) == 'done':
                    self.done = False
                    self.fadeout_done = False
                    self.text = []
                    self.made_leaderboard = False
                    fade.reset()
                    return 'Menu'


class Mission:
    def __init__(self, surface, plane_start):
        self.background = load_sprite('background4')
        self.mission = load_sprite('mission')
        self.mission_size = self.mission.get_size()
        self.mission_center = self.mission.get_rect().center
        self.screen_center = (surface.get_size()[0] // 2, surface.get_size()[1] // 2)
        self.mission_position = self.screen_center - Vector2(self.mission_center)
        self.plane_start = plane_start
        self.done = False
        self.fadeout_done = False

        # Define font and text
        self.font1 = pygame.font.Font('assets/fonts/the unseen.ttf', 24)

    def print_text(self, surface, level):
        next_line = - 50
        text = text_data.mission_texts[level]
        for line in text:
            if 'Press' in line:
                text_surface = self.font1.render(line, True, (100, 100, 100))
            else:
                text_surface = self.font1.render(line, True, (255, 255, 255))
            rect = text_surface.get_rect()
            rect.center = (self.screen_center - Vector2(0, next_line))
            surface.blit(text_surface, rect)
            next_line -= 35

    def draw(self, surface, fade, plane_position, sound, level):
        if not self.done:
            # Background
            surface.blit(self.background, (0, 0))
            # mission
            surface.blit(self.mission, self.mission_position)
            # texts
            self.print_text(surface, level)
            # Fade in
            fade.fadein(surface, 60)
            # Plane
            self.plane_start.draw(surface, plane_position, sound)
        else:
            # Background
            surface.blit(self.background, (0, 0))
            if not self.fadeout_done:
                # mission
                surface.blit(self.mission, self.mission_position)
                # texts
                self.print_text(surface, level)
                # screen plane
                if fade.fadeout(surface, 30) == 'done':
                    self.fadeout_done = True
            if self.plane_start.draw(surface, plane_position, sound, 'start') == 'done':
                self.done = False
                self.fadeout_done = False
                fade.reset()
                return 'Game'


class MissionOutcome:
    def __init__(self, surface, plane_start):
        self.background = load_sprite('background4')
        self.mission_outcome = load_sprite('mission_done')
        self.mission_outcome_size = self.mission_outcome.get_size()
        self.mission_outcome_center = self.mission_outcome.get_rect().center
        self.screen_center = (surface.get_size()[0] // 2, surface.get_size()[1] // 2)
        self.mission_outcome_position = self.screen_center - Vector2(self.mission_outcome_center)
        self.plane_start = plane_start
        self.done = False
        self.fadeout_done = False
        self.total_points = 0
        self.mission_points = 0
        self.intact = True
        self.text = ''
        self.success_sound = load_sound('success')
        self.success_sound.set_volume(0.5)
        self.sound = False
        self.sound_playing = False

        # Define font and text
        self.font1 = pygame.font.Font('assets/fonts/the unseen.ttf', 24)

    def set(self, hit, total_points, mission_points):
        self.total_points = total_points
        self.mission_points = mission_points
        if hit > 0:
            self.intact = False
        else:
            self.intact = True

    def print_text(self, surface):
        next_line = - 50
        if not self.text:
            self.text = text_data.mission_outcome(self.intact, self.total_points, self.mission_points)
        for line in self.text:
            if 'Press' in line:
                text_surface = self.font1.render(line, True, (100, 100, 100))
            else:
                text_surface = self.font1.render(line, True, (255, 255, 255))
            rect = text_surface.get_rect()
            rect.center = (self.screen_center - Vector2(0, next_line))
            surface.blit(text_surface, rect)
            next_line -= 35

    def draw(self, surface, fade, plane_position, sound):
        if not self.done:
            # Background
            surface.blit(self.background, (0, 0))
            # mission
            surface.blit(self.mission_outcome, self.mission_outcome_position)
            # texts
            self.print_text(surface)
            # Fade in
            fade.fadein(surface, 60)
            # Plane
            self.plane_start.draw(surface, plane_position, sound, 'intro')
            self.sound = sound
            if self.sound and not self.sound_playing:
                self.success_sound.play()
                self.sound_playing = True
        else:
            # Background
            surface.blit(self.background, (0, 0))
            # mission
            surface.blit(self.mission_outcome, self.mission_outcome_position)
            # texts
            self.print_text(surface)
            # screen plane
            if fade.fadeout(surface, 60) == 'done':
                self.done = False
                self.text = ''
                fade.reset()
                self.plane_start.draw(surface, plane_position, sound)
                self.sound_playing = False
                return 'Mission'
            self.plane_start.draw(surface, plane_position, sound)


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

New All 3 missile, 2 cruise, 1 drone, 3 balloons: ~8000 ms.
New All 3 missile, 2 cruise, 1 drone, 3 balloons: ~7500 ms.
'''
