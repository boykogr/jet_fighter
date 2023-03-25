import pygame
from models import Plane, Missile, Explosion
from utilities import load_sprite


class JetFighter:
    def __init__(self):
        # Initialize pygame
        pygame.init()
        pygame.display.set_caption("Jet Fighter")
        self.clock = pygame.time.Clock()
        # Set up the screen
        self.screen = pygame.display.set_mode((800, 600))
        self.background = load_sprite('background1', False)
        # hide OS cursor
        pygame.mouse.set_visible(False)

        self.plane = Plane((400, 300))

        self.missiles = [Missile(self.screen, self.plane.position) for _ in range(10)]

        self.explosions = []

        self.hit = 0

    def main_loop(self):
        while True:
            self._handle_input()
            self._game_logic()
            self._draw()

    def _handle_input(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                quit()

        is_key_pressed = pygame.key.get_pressed()
        if is_key_pressed[pygame.K_ESCAPE]:
            quit()

    @property
    def game_objects(self):
        return [*self.missiles, self.plane, *self.explosions]

    def _game_logic(self):
        if len(self.missiles) < 3:
            [self.missiles.append(Missile(self.screen, self.plane.position)) for _ in range(10)]
        for obj in self.game_objects:
            obj.move(self.screen)
            if obj == self.plane:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                mouse_position = pygame.math.Vector2(mouse_x, mouse_y)
                obj.rotate(mouse_position)
            else:
                obj.rotate(self.plane.position)
            obj.accelerate()
            if obj not in self.explosions:
                obj.trail()
        for missile in self.missiles:
            if missile.collides_with(self.plane):
                print(f'Hit {self.hit}')
                self.hit += 1
                self.missiles.remove(missile)
                self.explosions.append(Explosion(self.screen, missile.position))
                break
            for other in self.missiles:
                if missile != other:
                    if missile.collides_with(other):
                        self.missiles.remove(missile)
                        self.missiles.remove(other)
                        self.explosions.append(Explosion(self.screen, missile.position))
                        break

    def _draw(self):
        self.screen.blit(self.background, (0, 0))
        # Draw custom mouse cursor
        pygame.draw.circle(self.screen, (0, 0, 0), pygame.mouse.get_pos(), 5)

        for obj in self.game_objects:
            obj.draw(self.screen)
            if obj.draw(self.screen) == -1:
                self.explosions.remove(obj)
        # self.plane.draw(self.screen)
        # # self.missile.draw(self.screen)

        pygame.display.flip()
        self.clock.tick(30)

        # if self.plane.collides_with(self.missile):
        #     self.collision_counter += 1
        #     print(f'Collision #{self.collision_counter}')
