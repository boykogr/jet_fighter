from pygame.math import Vector2
from pygame.transform import rotozoom
import pygame
from utilities import load_sprite, load_sound
import random

DIRECTION_UP = Vector2(0, -1)


class GameObject:
    def __init__(self, position, sprite, velocity):
        self.position = Vector2(position)
        self.sprite = sprite
        self.radius = sprite.get_width() / 2
        self.velocity = Vector2(velocity)
        self.collision_points = [self.position]

    def draw(self, surface):
        position = self.position - Vector2(self.radius)
        surface.blit(self.sprite, position)

    def move(self, surface):
        self.position = self.position + self.velocity

    def collides_with(self, other):
        distances = [point.distance_to(other_point)
                     for point in self.collision_points
                     for other_point in other.collision_points]
        return any(d < self.radius + other.radius for d in distances)


class Plane(GameObject):
    ROTATION_SPEED = 5
    ACCELERATION = 2.5

    def __init__(self, position):
        self.direction = Vector2(DIRECTION_UP)
        super().__init__(position, load_sprite('plane'), Vector2(0))
        self.trail_sprites = []
        self.trail_counter = 0
        self.sprite_0 = load_sprite('plane')
        self.sprite_thrust = load_sprite('plane_thrust')
        self.sprite_l1 = load_sprite('plane_l1')
        self.sprite_l2 = load_sprite('plane_l2')
        self.sprite_r1 = load_sprite('plane_r1')
        self.sprite_r2 = load_sprite('plane_r2')
        self.trail_sprite = load_sprite('trail')
        self.trail_h1 = load_sprite('trail_h1')
        self.trail_h2 = load_sprite('trail_h2')

        self.fly_sound = load_sound('plane')
        self.fly_sound.set_volume(0.2)
        self.fly_sound.play(-1)
        self.thrust_sound = load_sound('thrust')
        self.thrust_sound.set_volume(0.1)

        self.fuel = 60
        self.speed = self.ACCELERATION
        self.add_trail = True
        self.focus = 60
        self.radius = 13
        self.hit = 0

    def dodge(self, other):
        distances = [point.distance_to(other_point)
                     for point in self.collision_points
                     for other_point in other.collision_points]
        return any(d < self.radius + other.radius + 5 for d in distances)

    def trail(self):
        # Create a new trail sprite
        trail_sprite = self.trail_sprite
        if self.hit == 2:
            trail_sprite = self.trail_h1
        elif self.hit > 2:
            trail_sprite = self.trail_h2

        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_sprite = rotozoom(trail_sprite, angle, 1.0)
        rotated_sprite_size = Vector2(rotated_sprite.get_size())
        position = round(self.position - rotated_sprite_size * 0.5)

        # Add the new trail sprite
        if self.add_trail:
            self.trail_sprites.append((position, rotated_sprite))
            self.add_trail = False
        else:
            self.add_trail = True

        # Remove the oldest sprite if the list is too long
        if len(self.trail_sprites) > 30:
            self.trail_sprites.pop(0)

    def rotate(self, mouse_position):
        if not self.speed == self.ACCELERATION * 2:
            self.sprite = self.sprite_0
        if self.hit > 3:
            self.ROTATION_SPEED = 8
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
        # Switch sprites if plane is turning
        if 5 < rotation_angle <= 15:
            self.sprite = self.sprite_r1
        elif rotation_angle > 15:
            self.sprite = self.sprite_r2
        elif -5 > rotation_angle >= -15:
            self.sprite = self.sprite_l1
        elif rotation_angle < -15:
            self.sprite = self.sprite_l2
        # Update collision points
        self.collision_points = [self.position]

    def move(self, surface):
        self.velocity = self.direction * self.speed
        self.position = self.position + self.velocity

    def thrust(self, thrusters=True, sound=True):
        if sound:
            self.thrust_sound.play()
        self.fuel -= 1
        if thrusters:
            if self.fuel > 0:
                self.speed = self.ACCELERATION * 2
                self.sprite = self.sprite_thrust
            elif self.fuel <= 0:
                self.fuel = 0
                self.speed = self.ACCELERATION
                self.sprite = self.sprite_0
        else:
            if self.fuel > 45:
                self.speed = self.ACCELERATION * 2
                self.sprite = self.sprite_thrust
            elif self.fuel <= 45:
                self.fuel = 0
                self.speed = self.ACCELERATION
                self.sprite = self.sprite_0

    def refuel(self):
        if self.fuel < 60:
            self.speed = self.ACCELERATION
            self.fuel += 0.5
            self.sprite = self.sprite_0

    def slow_motion(self):
        self.focus -= 1
        if self.focus > 0:
            return True
        else:
            self.focus = 0
            return False

    def refocus(self):
        if self.hit < 3:
            if self.focus < 60:
                self.focus += 0.5
        else:
            if self.focus < 120:
                self.focus += 1

    def draw(self, surface):
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        for position, sprite in self.trail_sprites:
            surface.blit(sprite, position)

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class Missile(GameObject):
    ROTATION_SPEED = 2
    ACCELERATION = 3

    def __init__(self, surface, plane_position):
        self.direction = Vector2(DIRECTION_UP)
        super().__init__(self.random_spawn_position(surface, plane_position), load_sprite('missile1'), Vector2(0))
        self.trail_sprites = []
        self.trail_counter = 0
        self.add_trail = True
        self.collision_points = [self.position + self.direction * 9, self.position + self.direction * -9]
        self.radius = 6
        self.active = False

    def random_spawn_position(self, surface, plane_position):
        if plane_position[0] >= 400:
            position = Vector2(-40, random.randrange(surface.get_height()))
        else:
            position = Vector2(840, random.randrange(surface.get_height()))
        return position

    def reset(self, surface, plane_position):
        self.direction = Vector2(DIRECTION_UP)
        self.position = Vector2(self.random_spawn_position(surface, plane_position))
        self.active = True

    def trail(self):
        # Create a new trail sprite
        trail_sprite = load_sprite('trail1')
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_sprite = rotozoom(trail_sprite, angle, 1.0)
        rotated_sprite_size = Vector2(rotated_sprite.get_size())
        position = round(self.position - rotated_sprite_size * 0.5)

        # Add the new trail sprite
        if self.add_trail:
            self.trail_sprites.append((position, rotated_sprite))
            self.add_trail = False
        else:
            self.add_trail = True

        # Remove the oldest sprite if the list is too long
        if len(self.trail_sprites) > 30:
            self.trail_sprites.pop(0)

    def move(self, surface):
        self.velocity = self.direction * self.ACCELERATION
        self.position = self.position + self.velocity

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
        # Update collision points
        self.collision_points = [self.position + self.direction * 9, self.position + self.direction * -9]

    def draw(self, surface):
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        for position, sprite in self.trail_sprites:
            surface.blit(sprite, position)

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class CruiseMissile(Missile):
    ROTATION_SPEED = 1
    ACCELERATION = 7

    def __init__(self, surface, plane_position):
        self.direction = Vector2(DIRECTION_UP)
        super(Missile, self).__init__(self.random_spawn_position(surface, plane_position),
                                      load_sprite('missile2'), Vector2(0))
        self.trail_sprites = []
        self.trail_counter = 0
        self.add_trail = True
        self.collision_points = [self.position]
        # self.collision_points = [self.position + self.direction * 9, self.position + self.direction * -9]
        self.radius = 6
        # self.sprite = load_sprite('missile2')
        self.warning_sprite = load_sprite('warning')
        self.warning_counter = 0
        self.warning = True
        self.active = False

    def random_spawn_position(self, surface, plane_position):
        if plane_position[0] >= 400:
            position = Vector2(-120, random.randrange(surface.get_height()))
        else:
            position = Vector2(920, random.randrange(surface.get_height()))
        return position

    def draw(self, surface):
        if self.position.x < -15 or self.position.x > 815 or self.position.y < -15 or self.position.y > 615:
            self.ACCELERATION = 3
            self.ROTATION_SPEED = 6
            self.warning_counter += 1
            if self.warning_counter == 15:
                self.warning_counter = 0
                if self.warning:
                    self.warning = False
                else:
                    self.warning = True
            if self.warning:
                x, y = self.position
                if x + 15 < 0:
                    x = 0
                elif x - 15 > 800:
                    x = 770
                if y + 15 < 0:
                    y = 0
                elif y - 15 > 600:
                    y = 570
                blit_position = Vector2(x, y)
                surface.blit(self.warning_sprite, blit_position)
        else:
            self.ACCELERATION = 7
            self.ROTATION_SPEED = 1
            angle = self.direction.angle_to(DIRECTION_UP)
            rotated_surface = rotozoom(self.sprite, angle, 1.0)
            rotated_surface_size = Vector2(rotated_surface.get_size())

            for position, sprite in self.trail_sprites:
                surface.blit(sprite, position)

            blit_position = self.position - rotated_surface_size * 0.5
            surface.blit(rotated_surface, blit_position)


class Drone(Missile):
    ROTATION_SPEED = 10
    ACCELERATION = 1

    def __init__(self, surface, plane_position):
        self.direction = Vector2(DIRECTION_UP)
        super(Missile, self).__init__(self.random_spawn_position(surface, plane_position),
                                      load_sprite('drone1'), Vector2(0))
        self.trail_sprites = []
        self.trail_counter = 0
        self.add_trail = False
        self.collision_points = [self.position]
        # self.collision_points = [self.position + self.direction * 9, self.position + self.direction * -9]
        self.radius = 6
        self.sprite1 = load_sprite('drone1')
        self.sprite2 = load_sprite('drone2')
        self.active = False

    def draw(self, surface):
        if self.sprite == self.sprite1:
            self.sprite = self.sprite2
        else:
            self.sprite = self.sprite1
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class Balloon(GameObject):
    def __init__(self, surface):
        self.font = pygame.font.Font('assets/fonts/the unseen.ttf', 10)
        position = Vector2(random.randrange(50, surface.get_width() - 50),
                           random.randrange(50, surface.get_height() - 120))
        self.direction = Vector2(DIRECTION_UP)
        super().__init__(position, load_sprite('balloon'), Vector2(0))
        self.radius = 1
        self.appear = False
        self.inflate = True
        self.active = False
        self.time = 1800
        self.timer = True

    def reset(self, surface):
        self.position = Vector2(random.randrange(50, surface.get_width() - 50),
                                random.randrange(50, surface.get_height() - 120))
        self.collision_points = [self.position]
        self.radius = 1
        self.appear = True
        self.inflate = True
        self.active = True
        self.time = 1800

    def move(self, surface):
        # Appear
        if self.appear:
            self.radius += 0.2
            if self.radius >= 15:
                self.appear = False
        # Disappear
        elif self.time <= 60:
            if self.radius >= 0:
                self.radius -= 0.2
        # Move
        elif self.radius >= 9:
            # Inflate
            if self.inflate:
                if self.radius < 15:
                    self.radius += 0.1
                else:
                    self.inflate = False
            # Deflate
            else:
                if self.radius > 10:
                    self.radius -= 0.1
                else:
                    self.inflate = True

    def rotate(self, plane_position):
        pass

    def calculate(self):
        if self.timer:
            self.time -= 1

    def draw(self, surface):
        new_sprite = pygame.transform.scale(self.sprite, (self.radius * 2, self.radius * 2))
        blit_position = self.position - Vector2(self.radius)
        surface.blit(new_sprite, blit_position)
        if self.timer:
            text = str(self.time // 60)
            text_surface = self.font.render(text, True, (255, 255, 255))
            surface.blit(text_surface, self.position - (20, 20))


class Explosion(GameObject):
    ACCELERATION = 0.5
    exists = 120

    def __init__(self, object_position, sound):
        self.direction = Vector2(DIRECTION_UP)
        super().__init__(object_position, load_sprite('explosion1'), Vector2(0))

        self.sprite2 = load_sprite('explosion2')
        self.sprite3 = load_sprite('explosion3')
        self.sprite4 = load_sprite('explosion4')
        self.sprite5 = load_sprite('explosion5')
        self.sprite6 = load_sprite('explosion6')
        self.sprite7 = load_sprite('explosion7')
        if sound:
            self.explosion_sound = load_sound('explosion')
            self.explosion_sound.set_volume(0.5)
            self.explosion_sound.play()

    def rotate(self, mouse_position):
        self.direction.rotate_ip(1)

    def accelerate(self):
        self.velocity = self.direction * self.ACCELERATION

    def draw(self, surface):
        self.exists -= 1
        if self.exists < 114:
            self.sprite = self.sprite2
        if self.exists < 108:
            self.sprite = self.sprite3
        if self.exists < 100:
            self.sprite = self.sprite4
        if self.exists < 80:
            self.sprite = self.sprite5
        if self.exists < 60:
            self.sprite = self.sprite6
        if self.exists < 40:
            self.sprite = self.sprite7
        if self.exists <= 0:
            return -1
        angle = 1
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)


class Bullets(GameObject):
    ACCELERATION = 10

    def __init__(self, plane_position, plane_direction, sound):
        position = plane_position
        direction = plane_direction
        super().__init__(position, load_sprite('bullets'), Vector2(0))
        if sound:
            self.explosion_sound = load_sound('machine_gun')
            self.explosion_sound.set_volume(0.2)
            self.explosion_sound.play()

        self.direction = Vector2(direction)
        self.position = position
        self.speed = self.ACCELERATION
        self.collision_points = [self.position + self.direction * 9]
        self.radius = 6

    def move(self, surface):
        self.velocity = self.direction * self.speed
        self.position = self.position + self.velocity
        self.collision_points = [self.position]

    def draw(self, surface):
        angle = self.direction.angle_to(DIRECTION_UP)
        rotated_surface = rotozoom(self.sprite, angle, 1.0)
        rotated_surface_size = Vector2(rotated_surface.get_size())

        blit_position = self.position - rotated_surface_size * 0.5
        surface.blit(rotated_surface, blit_position)

    def outside(self):
        return self.position.x < 0 or self.position.x > 800 or self.position.y < 0 or self.position.y > 600

    def rotate(self, plane):
        pass

    def trail(self):
        pass
