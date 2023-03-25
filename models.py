from pygame.math import Vector2
from pygame.transform import rotozoom
from utilities import load_sprite
import random

DIRECTION_UP = Vector2(0, -1)


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)

    def draw(self, surface):
        position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, position)

    def move(self, surface):
        self.position = self.position + self.velocity

    def collides_with(self, other):
        distance = self.position.distance_to(other.position)
        return distance < self.radius + other.radius


class Plane(GameObject):
    ROTATION_SPEED = 10
    ACCELERATION = 5

    def __init__(self, position):
        self.direction = Vector2(DIRECTION_UP)
        super().__init__(position, load_sprite('plane'), Vector2(0))
        self.trail_sprites = []
        self.trail_counter = 0

    def trail(self):
        # Create a new trail sprite
        trail_sprite = load_sprite('trail')
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_sprite = rotozoom(trail_sprite, angle, 1.0)
        rotated_sprite_size = Vector2(rotated_sprite.get_size())
        position = round(self.position - rotated_sprite_size * 0.5)

        # Add the new trail sprite
        self.trail_sprites.append((position, rotated_sprite))

        # Remove the oldest sprite if the list is too long
        if len(self.trail_sprites) > 30:
            self.trail_sprites.pop(0)

    def rotate(self, mouse_position):
        # Get the vector from the plane position to the mouse position
        target_direction = Vector2(mouse_position) - self.position
        # Get the angle between the current direction and target direction
        rotation_angle = round(self.direction.angle_to(target_direction))
        # Convert the angles
        if -180 > rotation_angle > -360:
            rotation_angle += 360
        elif 180 < rotation_angle < 360:
            rotation_angle -= 360
        # Rotate the plane towards the target direction
        if 0 < rotation_angle < 180:
            self.direction.rotate_ip(min(rotation_angle, self.ROTATION_SPEED))
        if 0 > rotation_angle > -180:
            self.direction.rotate_ip(max(rotation_angle, -self.ROTATION_SPEED))
        # Check if plane is outside the screen and rotate it:
        if self.position.x < 0 or self.position.x > 800 or self.position.y < 0 or self.position.y > 600:
            if rotation_angle == 0 or rotation_angle == 180 or rotation_angle == -180:
                self.direction.rotate_ip(self.ROTATION_SPEED)

    def accelerate(self):
        self.velocity = self.direction * self.ACCELERATION

    def draw(self, surface):
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        for position, sprite in self.trail_sprites:
            surface.blit(sprite, position)

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class Missile(GameObject):
    MIN_START_GAP = 250
    ROTATION_SPEED = 6
    ACCELERATION = 4

    def __init__(self, surface, plane_position):

        # Brute force creating a random position until we have one:
        while True:
            position = Vector2(random.randrange(surface.get_width()), random.randrange(surface.get_height()))
            if position.distance_to(plane_position) > self.MIN_START_GAP:
                break
        self.direction = Vector2(DIRECTION_UP)
        super().__init__(position, load_sprite('missile1'), Vector2(0))
        self.trail_sprites = []
        self.trail_counter = 0

    def trail(self):
        # Create a new trail sprite
        trail_sprite = load_sprite('trail1')
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_sprite = rotozoom(trail_sprite, angle, 1.0)
        rotated_sprite_size = Vector2(rotated_sprite.get_size())
        position = round(self.position - rotated_sprite_size * 0.5)

        # Add the new trail sprite
        self.trail_sprites.append((position, rotated_sprite))

        # Remove the oldest sprite if the list is too long
        if len(self.trail_sprites) > 30:
            self.trail_sprites.pop(0)

    def rotate(self, plane_position):
        # Get the vector from the missile position to the plane position
        target_direction = Vector2(plane_position) - self.position
        # Get the angle between the current direction and target direction
        rotation_angle = round(self.direction.angle_to(target_direction))
        # Convert the angles
        if -180 > rotation_angle > -360:
            rotation_angle += 360
        elif 180 < rotation_angle < 360:
            rotation_angle -= 360
        # Rotate the missile towards the target direction
        if 0 < rotation_angle < 180:
            self.direction.rotate_ip(min(rotation_angle, self.ROTATION_SPEED))
        if 0 > rotation_angle > -180:
            self.direction.rotate_ip(max(rotation_angle, -self.ROTATION_SPEED))
        # Check if missile is outside the screen and rotate it:
        if self.position.x < 0 or self.position.x > 800 or self.position.y < 0 or self.position.y > 600:
            if rotation_angle == 0 or rotation_angle == 180 or rotation_angle == -180:
                self.direction.rotate_ip(self.ROTATION_SPEED)

    def accelerate(self):
        self.velocity = self.direction * self.ACCELERATION

    def draw(self, surface):
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        for position, sprite in self.trail_sprites:
            surface.blit(sprite, position)

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class Explosion(GameObject):
    ACCELERATION = 0.5
    exists = 60

    def __init__(self, surface, object_position):
        self.direction = Vector2(DIRECTION_UP)
        super().__init__(object_position, load_sprite('explosion'), Vector2(0))

    def rotate(self, mouse_position):
        self.direction.rotate_ip(1)

    def accelerate(self):
        self.velocity = self.direction * self.ACCELERATION

    def draw(self, surface):
        self.exists -= 1
        if self.exists <= 0:
            return -1
        angle = 1
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

