import pygame
import random
import math
import json
import os

pygame.init()

WIDTH, HEIGHT = 600, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('🐦 Flappy Bird for Kids! 🐦')

SKY_BLUE = (135, 206, 235)
CLOUD_WHITE = (255, 255, 255)
BIRD_YELLOW = (255, 215, 0)
BIRD_ORANGE = (255, 165, 0)
BIRD_RED = (255, 69, 0)
PIPE_GREEN = (34, 139, 34)
PIPE_DARK = (0, 100, 0)
GROUND_BROWN = (139, 69, 19)
GRASS_GREEN = (124, 252, 0)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
SOFT_PINK = (255, 182, 193)
GOLD = (255, 215, 0)
POWER_UP_PURPLE = (147, 112, 219)
STAR_YELLOW = (255, 255, 0)
NIGHT_BLUE = (25, 25, 112)
RAIN_BLUE = (100, 149, 237)
SNOW_WHITE = (248, 248, 255)
FOG_GRAY = (169, 169, 169)

# Made easier for addiction
GRAVITY = 0.4  # Reduced from 0.5
JUMP_STRENGTH = -7  # Reduced from -8
PIPE_WIDTH = 80
PIPE_GAP = 200  # Increased from 180
PIPE_SPEED = 2.5  # Reduced from 3
GROUND_HEIGHT = 100

POWER_UP_CHANCE = 0.4  # Increased from 0.3
POWER_UP_SIZE = 20
POWER_UP_SPEED = 2

font = pygame.font.SysFont('Comic Sans MS', 24, bold=True)
big_font = pygame.font.SysFont('Comic Sans MS', 48, bold=True)
small_font = pygame.font.SysFont('Comic Sans MS', 18, bold=True)

class SoundManager:
    def __init__(self):
        pygame.mixer.init()
        self.sounds = {}

    def play(self, sound_name):
        pass

class WeatherSystem:
    def __init__(self):
        self.rain_drops = []
        self.snow_flakes = []
        self.fog_particles = []
        self.weather_type = 'clear'
        self.weather_intensity = 0

    def set_weather(self, weather_type, intensity=1.0):
        self.weather_type = weather_type
        self.weather_intensity = intensity

        if weather_type == 'rain':
            self.rain_drops = []
            for _ in range(int(50 * intensity)):
                self.rain_drops.append({
                    'x': random.randint(-50, WIDTH + 50),
                    'y': random.randint(-HEIGHT, 0),
                    'speed': random.uniform(8, 12),
                    'length': random.randint(10, 20)
                })
        elif weather_type == 'snow':
            self.snow_flakes = []
            for _ in range(int(30 * intensity)):
                self.snow_flakes.append({
                    'x': random.randint(0, WIDTH),
                    'y': random.randint(-HEIGHT, 0),
                    'speed': random.uniform(1, 3),
                    'size': random.randint(2, 5),
                    'sway': random.uniform(-0.5, 0.5)
                })
        elif weather_type == 'fog':
            self.fog_particles = []
            for _ in range(int(20 * intensity)):
                self.fog_particles.append({
                    'x': random.randint(-100, WIDTH + 100),
                    'y': random.randint(0, HEIGHT - GROUND_HEIGHT),
                    'speed': random.uniform(0.5, 1.5),
                    'size': random.randint(40, 80),
                    'alpha': random.randint(30, 80)
                })

    def update(self):
        if self.weather_type == 'rain':
            for drop in self.rain_drops:
                drop['y'] += drop['speed']
                drop['x'] -= 2
                if drop['y'] > HEIGHT:
                    drop['y'] = random.randint(-50, -10)
                    drop['x'] = random.randint(-50, WIDTH + 50)

        elif self.weather_type == 'snow':
            for flake in self.snow_flakes:
                flake['y'] += flake['speed']
                flake['x'] += flake['sway']
                if flake['y'] > HEIGHT:
                    flake['y'] = random.randint(-50, -10)
                    flake['x'] = random.randint(0, WIDTH)

        elif self.weather_type == 'fog':
            for particle in self.fog_particles:
                particle['x'] -= particle['speed']
                if particle['x'] < -particle['size']:
                    particle['x'] = WIDTH + particle['size']

    def draw(self, screen):
        if self.weather_type == 'rain':
            for drop in self.rain_drops:
                pygame.draw.line(screen, RAIN_BLUE,
                               (drop['x'], drop['y']),
                               (drop['x'] - 5, drop['y'] + drop['length']), 2)

        elif self.weather_type == 'snow':
            for flake in self.snow_flakes:
                pygame.draw.circle(screen, SNOW_WHITE,
                                 (int(flake['x']), int(flake['y'])), flake['size'])

        elif self.weather_type == 'fog':
            fog_surface = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            for particle in self.fog_particles:
                s = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*FOG_GRAY, particle['alpha']),
                                 (particle['size'], particle['size']), particle['size'])
                fog_surface.blit(s, (particle['x'] - particle['size'], particle['y'] - particle['size']))
            screen.blit(fog_surface, (0, 0))

class BackgroundLayer:
    def __init__(self, elements, speed_multiplier, y_range):
        self.elements = elements
        self.speed_multiplier = speed_multiplier
        self.y_range = y_range
        self.x_offset = 0

    def update(self, base_speed):
        self.x_offset -= base_speed * self.speed_multiplier
        if self.x_offset <= -WIDTH:
            self.x_offset = 0

    def draw(self, screen, time_of_day):
        for i in range(3):
            x_pos = i * WIDTH + self.x_offset
            for element in self.elements:
                element['draw_func'](screen, x_pos + element['x'], element['y'], time_of_day)

class TimeSystem:
    def __init__(self):
        self.time_of_day = 0.0
        self.day_length = 2000

    def update(self, score):
        cycle_position = (score * 10) % self.day_length
        self.time_of_day = cycle_position / self.day_length

    def get_sky_color(self):
        if self.time_of_day < 0.25:
            ratio = self.time_of_day / 0.25
            return self.interpolate_color(NIGHT_BLUE, SKY_BLUE, ratio)
        elif self.time_of_day < 0.75:
            return SKY_BLUE
        else:
            ratio = (self.time_of_day - 0.75) / 0.25
            return self.interpolate_color(SKY_BLUE, NIGHT_BLUE, ratio)

    def get_cloud_color(self):
        if self.time_of_day < 0.25 or self.time_of_day > 0.75:
            return (200, 200, 220)
        return CLOUD_WHITE

    def is_night(self):
        return self.time_of_day < 0.25 or self.time_of_day > 0.75

    def interpolate_color(self, color1, color2, ratio):
        return tuple(int(c1 + (c2 - c1) * ratio) for c1, c2 in zip(color1, color2))

class SeasonSystem:
    def __init__(self):
        self.current_season = 'spring'
        self.seasons = ['spring', 'summer', 'fall', 'winter']
        self.season_index = 0

    def update(self, score):
        new_season_index = (score // 30) % 4  # Changed from 50 to 30 for more frequent changes
        if new_season_index != self.season_index:
            self.season_index = new_season_index
            self.current_season = self.seasons[new_season_index]

    def get_season_modifiers(self):
        if self.current_season == 'spring':
            return {'gravity': GRAVITY * 0.9, 'pipe_color': PIPE_GREEN, 'grass_color': (124, 252, 0)}  # Easier
        elif self.current_season == 'summer':
            return {'gravity': GRAVITY * 0.8, 'pipe_color': (255, 140, 0), 'grass_color': (34, 139, 34)}  # Easier
        elif self.current_season == 'fall':
            return {'gravity': GRAVITY, 'pipe_color': (160, 82, 45), 'grass_color': (184, 134, 11)}
        elif self.current_season == 'winter':
            return {'gravity': GRAVITY * 1.1, 'pipe_color': (70, 130, 180), 'grass_color': (248, 248, 255)}

class Particle:
    def __init__(self, x, y, color, velocity, size=3):
        self.x = x
        self.y = y
        self.color = color
        self.velocity = velocity
        self.size = size
        self.life = 30
        self.max_life = 30

    def update(self):
        self.x += self.velocity[0]
        self.y += self.velocity[1]
        self.life -= 1
        self.velocity = (self.velocity[0] * 0.98, self.velocity[1] + 0.1)

    def draw(self, screen):
        alpha = int(255 * (self.life / self.max_life))
        color_with_alpha = (*self.color[:3], alpha)
        s = pygame.Surface((self.size * 2, self.size * 2), pygame.SRCALPHA)
        pygame.draw.circle(s, color_with_alpha, (self.size, self.size), self.size)
        screen.blit(s, (self.x - self.size, self.y - self.size))

class PowerUp:
    def __init__(self, x, y, power_type):
        self.x = x
        self.y = y
        self.power_type = power_type
        self.collected = False
        self.bob_offset = random.uniform(0, 2 * math.pi)
        self.bob_timer = 0

    def update(self):
        self.x -= PIPE_SPEED
        self.bob_timer += 0.1

    def draw(self, screen):
        bob_y = self.y + math.sin(self.bob_timer + self.bob_offset) * 3

        if self.power_type == 'star':
            points = []
            for i in range(10):
                angle = i * math.pi / 5
                if i % 2 == 0:
                    radius = POWER_UP_SIZE
                else:
                    radius = POWER_UP_SIZE // 2
                x = self.x + radius * math.cos(angle - math.pi/2)
                y = bob_y + radius * math.sin(angle - math.pi/2)
                points.append((x, y))
            pygame.draw.polygon(screen, STAR_YELLOW, points)
            pygame.draw.polygon(screen, GOLD, points, 2)

        elif self.power_type == 'shield':
            pygame.draw.circle(screen, POWER_UP_PURPLE, (int(self.x), int(bob_y)), POWER_UP_SIZE)
            pygame.draw.circle(screen, WHITE, (int(self.x), int(bob_y)), POWER_UP_SIZE, 3)

    def get_rect(self):
        return pygame.Rect(self.x - POWER_UP_SIZE, self.y - POWER_UP_SIZE,
                          POWER_UP_SIZE * 2, POWER_UP_SIZE * 2)

    def is_off_screen(self):
        return self.x + POWER_UP_SIZE < 0

class Bird:
    def __init__(self):
        self.x = WIDTH // 4
        self.y = HEIGHT // 2
        self.velocity = 0
        self.size = 20  # Reduced from 25 for easier gameplay
        self.wing_angle = 0
        self.trail = []
        self.shield_time = 0
        self.invincible = False
        self.body_tilt = 0
        # Pixel mask for precise collision
        self.create_collision_mask()

    def create_collision_mask(self):
        # Create a more forgiving collision mask (smaller than visual size)
        self.collision_size = self.size - 5

    def jump(self):
        self.velocity = JUMP_STRENGTH

    def update(self, season_modifiers, weather, pipes):
        gravity = season_modifiers['gravity']

        # Environmental physics - air pressure from pipes
        for pipe in pipes:
            distance = abs(pipe.x + PIPE_WIDTH/2 - self.x)
            if distance < 100:  # Within influence range
                pressure_effect = (100 - distance) / 100 * 0.2
                if self.y < pipe.height or self.y > pipe.height + PIPE_GAP:
                    # Near pipe walls, slight upward pressure
                    gravity -= pressure_effect

        if weather.weather_type == 'snow':
            gravity *= 0.8
            if random.random() < 0.1:
                self.velocity += random.uniform(-0.5, 0.5)

        self.velocity += gravity
        self.y += self.velocity
        self.wing_angle += 15

        self.body_tilt = max(-30, min(30, self.velocity * 3))

        self.trail.append((self.x, self.y))
        if len(self.trail) > 8:
            self.trail.pop(0)

        if self.shield_time > 0:
            self.shield_time -= 1
            self.invincible = True
        else:
            self.invincible = False

    def draw(self, screen):
        # Trail effect
        for i, (trail_x, trail_y) in enumerate(self.trail):
            alpha = int(50 * (i / len(self.trail)))
            size = int(self.size * 0.3 * (i / len(self.trail)))
            if size > 0:
                s = pygame.Surface((size * 2, size * 2), pygame.SRCALPHA)
                pygame.draw.circle(s, (*BIRD_YELLOW, alpha), (size, size), size)
                screen.blit(s, (trail_x - size, trail_y - size))

        # Shield effect
        if self.invincible:
            shield_size = self.size + 8
            shield_alpha = int(100 + 50 * math.sin(self.wing_angle * 0.5))
            s = pygame.Surface((shield_size * 2, shield_size * 2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*POWER_UP_PURPLE, shield_alpha), (shield_size, shield_size), shield_size, 3)
            screen.blit(s, (self.x - shield_size, self.y - shield_size))

        # Bird body
        pygame.draw.ellipse(screen, BIRD_YELLOW, (self.x - self.size, self.y - self.size//2, self.size * 2, self.size))
        pygame.draw.ellipse(screen, BIRD_ORANGE, (self.x - self.size + 3, self.y - self.size//2 + 2, self.size * 2 - 6, self.size - 4))

        # Wing animation
        wing_flap = math.sin(math.radians(self.wing_angle)) * 10
        wing_y = self.y - 8 + wing_flap

        pygame.draw.ellipse(screen, BIRD_RED, (self.x - 18, wing_y - 10, 25, 18))
        pygame.draw.ellipse(screen, BIRD_ORANGE, (self.x - 15, wing_y - 8, 20, 14))

        # Eye
        eye_x, eye_y = self.x + 8, self.y - 5
        pygame.draw.circle(screen, WHITE, (int(eye_x), int(eye_y)), 7)
        pygame.draw.circle(screen, BLACK, (int(eye_x + 2), int(eye_y)), 4)
        pygame.draw.circle(screen, WHITE, (int(eye_x + 3), int(eye_y - 1)), 1)

        # Beak
        beak_tip_x = self.x + self.size + 8
        beak_tip_y = self.y + 2
        beak_points = [
            (self.x + self.size - 3, self.y - 2),
            (beak_tip_x, beak_tip_y),
            (self.x + self.size - 3, self.y + 6)
        ]
        pygame.draw.polygon(screen, BIRD_ORANGE, beak_points)
        pygame.draw.polygon(screen, BIRD_RED, beak_points, 1)

        # Tail
        tail_points = [
            (self.x - self.size + 2, self.y),
            (self.x - self.size - 8, self.y - 6),
            (self.x - self.size - 8, self.y + 6)
        ]
        pygame.draw.polygon(screen, BIRD_RED, tail_points)

    def get_collision_rect(self):
        # More precise collision detection with smaller hitbox
        return pygame.Rect(self.x - self.collision_size, self.y - self.collision_size//2,
                          self.collision_size * 2, self.collision_size)

    def get_rect(self):
        return self.get_collision_rect()

class Pipe:
    def __init__(self, x):
        self.x = x
        # More forgiving pipe heights
        min_height = 120  # Increased from 100
        max_height = HEIGHT - PIPE_GAP - GROUND_HEIGHT - 120  # More space
        self.height = random.randint(min_height, max_height)
        self.passed = False
        self.scored = False

    def update(self):
        self.x -= PIPE_SPEED

    def draw(self, screen, pipe_color):
        pipe_dark = tuple(max(0, c - 50) for c in pipe_color)

        # Top pipe
        top_rect = pygame.Rect(self.x, 0, PIPE_WIDTH, self.height)
        pygame.draw.rect(screen, pipe_color, top_rect)
        pygame.draw.rect(screen, pipe_dark, top_rect, 3)

        # Top cap
        cap_rect = pygame.Rect(self.x - 5, self.height - 20, PIPE_WIDTH + 10, 30)
        pygame.draw.rect(screen, pipe_color, cap_rect)
        pygame.draw.rect(screen, pipe_dark, cap_rect, 3)

        # Bottom pipe
        bottom_y = self.height + PIPE_GAP
        bottom_rect = pygame.Rect(self.x, bottom_y, PIPE_WIDTH, HEIGHT - bottom_y - GROUND_HEIGHT)
        pygame.draw.rect(screen, pipe_color, bottom_rect)
        pygame.draw.rect(screen, pipe_dark, bottom_rect, 3)

        # Bottom cap
        cap_rect = pygame.Rect(self.x - 5, bottom_y, PIPE_WIDTH + 10, 30)
        pygame.draw.rect(screen, pipe_color, cap_rect)
        pygame.draw.rect(screen, pipe_dark, cap_rect, 3)

    def get_rects(self):
        # Slightly smaller collision boxes for more forgiving gameplay
        margin = 3
        top_rect = pygame.Rect(self.x + margin, 0, PIPE_WIDTH - 2*margin, self.height)
        bottom_rect = pygame.Rect(self.x + margin, self.height + PIPE_GAP, PIPE_WIDTH - 2*margin,
                                HEIGHT - self.height - PIPE_GAP - GROUND_HEIGHT)
        return [top_rect, bottom_rect]

    def is_off_screen(self):
        return self.x + PIPE_WIDTH < 0

class GameState:
    def __init__(self):
        self.high_score = self.load_high_score()
        self.games_played = 0
        self.total_score = 0

    def load_high_score(self):
        try:
            if os.path.exists('flappy_save.json'):
                with open('flappy_save.json', 'r') as f:
                    data = json.load(f)
                    return data.get('high_score', 0)
        except:
            pass
        return 0

    def save_high_score(self, score):
        if score > self.high_score:
            self.high_score = score
            try:
                data = {'high_score': self.high_score}
                with open('flappy_save.json', 'w') as f:
                    json.dump(data, f)
            except:
                pass

# Enhanced background drawing functions
def draw_mountain(screen, x, y, time_of_day):
    if time_of_day < 0.25 or time_of_day > 0.75:
        color = (60, 60, 80)
        snow_color = (200, 200, 220)
    else:
        color = (100, 100, 120)
        snow_color = (255, 255, 255)

    points = [(x, y), (x + 80, y - 60), (x + 120, y - 40), (x + 200, y)]
    pygame.draw.polygon(screen, color, points)

    # Snow caps
    if time_of_day < 0.3 or time_of_day > 0.7:
        snow_points = [(x + 70, y - 50), (x + 80, y - 60), (x + 90, y - 50)]
        pygame.draw.polygon(screen, snow_color, snow_points)

def draw_tree(screen, x, y, time_of_day):
    if time_of_day < 0.25 or time_of_day > 0.75:
        trunk_color = (80, 50, 20)
        leaf_color = (20, 60, 20)
    else:
        trunk_color = (139, 69, 19)
        leaf_color = (34, 139, 34)

    # Trunk
    pygame.draw.rect(screen, trunk_color, (x + 15, y - 40, 10, 40))
    # Leaves
    pygame.draw.circle(screen, leaf_color, (x + 20, y - 50), 20)
    # Highlight for depth
    pygame.draw.circle(screen, tuple(min(255, c + 30) for c in leaf_color), (x + 15, y - 55), 8)

def draw_cloud_bg(screen, x, y, time_of_day):
    if time_of_day < 0.25 or time_of_day > 0.75:
        color = (200, 200, 220)
    else:
        color = CLOUD_WHITE

    # Main cloud body
    pygame.draw.circle(screen, color, (x, y), 15)
    pygame.draw.circle(screen, color, (x + 20, y), 20)
    pygame.draw.circle(screen, color, (x + 40, y), 15)
    pygame.draw.circle(screen, color, (x + 20, y - 10), 15)

def draw_star(screen, x, y, time_of_day):
    if time_of_day < 0.3 or time_of_day > 0.7:  # Only show at night
        twinkle = math.sin(pygame.time.get_ticks() * 0.01 + x * 0.1) * 0.5 + 0.5
        size = int(2 + twinkle * 2)
        color = (255, 255, int(200 + twinkle * 55))
        pygame.draw.circle(screen, color, (int(x), int(y)), size)

def draw_background(screen, time_system, season_system, bg_layers, weather):
    sky_color = time_system.get_sky_color()

    # Adjust sky color based on weather
    if weather.weather_type == 'fog':
        sky_color = tuple(max(0, c - 30) for c in sky_color)
    elif weather.weather_type == 'rain':
        sky_color = tuple(max(0, c - 20) for c in sky_color)

    # Gradient sky
    for y in range(HEIGHT - GROUND_HEIGHT):
        color_ratio = y / (HEIGHT - GROUND_HEIGHT)
        r = int(sky_color[0] + (255 - sky_color[0]) * color_ratio * 0.3)
        g = int(sky_color[1] + (255 - sky_color[1]) * color_ratio * 0.3)
        b = int(sky_color[2] + (255 - sky_color[2]) * color_ratio * 0.1)
        pygame.draw.line(screen, (r, g, b), (0, y), (WIDTH, y))

    # Draw parallax layers
    for layer in bg_layers:
        layer.draw(screen, time_system.time_of_day)

    # Ground
    season_mods = season_system.get_season_modifiers()
    ground_rect = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, GROUND_HEIGHT)
    pygame.draw.rect(screen, GROUND_BROWN, ground_rect)

    # Grass with texture
    grass_rect = pygame.Rect(0, HEIGHT - GROUND_HEIGHT, WIDTH, 20)
    pygame.draw.rect(screen, season_mods['grass_color'], grass_rect)

    # Add some grass texture
    for i in range(0, WIDTH, 10):
        grass_height = random.randint(15, 25)
        pygame.draw.line(screen, tuple(max(0, c - 20) for c in season_mods['grass_color']),
                        (i, HEIGHT - GROUND_HEIGHT), (i, HEIGHT - GROUND_HEIGHT + grass_height), 2)

def draw_score(screen, score):
    score_text = big_font.render(str(score), True, WHITE)
    score_outline = big_font.render(str(score), True, BLACK)

    # Draw outline
    for dx in [-2, -1, 0, 1, 2]:
        for dy in [-2, -1, 0, 1, 2]:
            if dx != 0 or dy != 0:
                screen.blit(score_outline, (WIDTH//2 - score_outline.get_width()//2 + dx, 50 + dy))

    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, 50))

def draw_season_indicator(screen, season):
    season_icons = {'spring': '🌸', 'summer': '☀️', 'fall': '🍂', 'winter': '❄️'}
    season_text = small_font.render(f"{season_icons.get(season, '')} {season.title()}", True, WHITE)
    screen.blit(season_text, (10, 10))

def draw_weather_indicator(screen, weather):
    if weather.weather_type != 'clear':
        weather_icons = {'rain': '🌧️', 'snow': '❄️', 'fog': '🌫️'}
        weather_text = small_font.render(f"{weather_icons.get(weather.weather_type, '')} {weather.weather_type.title()}", True, WHITE)
        screen.blit(weather_text, (10, 30))

def draw_score_popup(screen, x, y, points, timer):
    if timer > 0:
        alpha = int(255 * (timer / 60))
        popup_y = y - (60 - timer)

        score_text = f"+{points}"
        color = STAR_YELLOW if points > 1 else WHITE

        text_surface = font.render(score_text, True, color)
        s = pygame.Surface(text_surface.get_size(), pygame.SRCALPHA)
        s.set_alpha(alpha)
        s.blit(text_surface, (0, 0))
        screen.blit(s, (x - text_surface.get_width()//2, popup_y))

def draw_game_over(screen, score, high_score, game_state):
    overlay = pygame.Surface((WIDTH, HEIGHT))
    overlay.set_alpha(128)
    overlay.fill(BLACK)
    screen.blit(overlay, (0, 0))
    game_over_text = big_font.render('Game Over!', True, WHITE)
    screen.blit(game_over_text, (WIDTH//2 - game_over_text.get_width()//2, HEIGHT//2 - 100))

    score_text = font.render(f'Score: {score}', True, WHITE)
    screen.blit(score_text, (WIDTH//2 - score_text.get_width()//2, HEIGHT//2 - 40))

    if score > high_score:
        new_record_text = font.render('NEW HIGH SCORE!', True, GOLD)
        screen.blit(new_record_text, (WIDTH//2 - new_record_text.get_width()//2, HEIGHT//2 - 10))
        high_score_text = font.render(f'High Score: {score}', True, GOLD)
    else:
        high_score_text = font.render(f'High Score: {high_score}', True, WHITE)

    screen.blit(high_score_text, (WIDTH//2 - high_score_text.get_width()//2, HEIGHT//2 + 20))

    restart_text = font.render('Press SPACE to play again', True, SOFT_PINK)
    screen.blit(restart_text, (WIDTH//2 - restart_text.get_width()//2, HEIGHT//2 + 60))

    stats_text = small_font.render(f'Games Played: {game_state.games_played}', True, WHITE)
    screen.blit(stats_text, (WIDTH//2 - stats_text.get_width()//2, HEIGHT//2 + 100))

    if game_state.games_played > 0:
        avg_score = game_state.total_score / game_state.games_played
        avg_text = small_font.render(f'Average Score: {avg_score:.1f}', True, WHITE)
        screen.blit(avg_text, (WIDTH//2 - avg_text.get_width()//2, HEIGHT//2 + 120))

def main():
    clock = pygame.time.Clock()
    sound_manager = SoundManager()
    weather_system = WeatherSystem()
    time_system = TimeSystem()
    season_system = SeasonSystem()
    game_state = GameState()

    bg_elements_far = [
        {'x': 100, 'y': 250, 'draw_func': draw_mountain},
        {'x': 300, 'y': 280, 'draw_func': draw_mountain},
        {'x': 500, 'y': 260, 'draw_func': draw_mountain},
    ]

    bg_elements_mid = [
        {'x': 50, 'y': 100, 'draw_func': draw_cloud_bg},
        {'x': 200, 'y': 80, 'draw_func': draw_cloud_bg},
        {'x': 400, 'y': 120, 'draw_func': draw_cloud_bg},
        {'x': 150, 'y': 50, 'draw_func': draw_star},
        {'x': 350, 'y': 70, 'draw_func': draw_star},
        {'x': 500, 'y': 40, 'draw_func': draw_star},
    ]

    bg_elements_close = [
        {'x': 150, 'y': HEIGHT - GROUND_HEIGHT, 'draw_func': draw_tree},
        {'x': 350, 'y': HEIGHT - GROUND_HEIGHT, 'draw_func': draw_tree},
        {'x': 550, 'y': HEIGHT - GROUND_HEIGHT, 'draw_func': draw_tree},
    ]

    bg_layers = [
        BackgroundLayer(bg_elements_far, 0.2, (200, 300)),
        BackgroundLayer(bg_elements_mid, 0.5, (50, 150)),
        BackgroundLayer(bg_elements_close, 0.8, (HEIGHT - GROUND_HEIGHT - 50, HEIGHT - GROUND_HEIGHT)),
    ]

    bird = Bird()
    pipes = []
    power_ups = []
    particles = []
    score = 0
    game_over = False
    pipe_timer = 0
    score_popup_timer = 0
    score_popup_points = 0
    score_popup_x = 0
    score_popup_y = 0

    weather_timer = 0

    running = True
    while running:
        dt = clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if game_over:
                        bird = Bird()
                        pipes = []
                        power_ups = []
                        particles = []
                        score = 0
                        game_over = False
                        pipe_timer = 0
                        score_popup_timer = 0
                        game_state.games_played += 1
                        weather_system.set_weather('clear')
                    else:
                        bird.jump()
                        sound_manager.play('jump')

        if not game_over:
            time_system.update(score)
            season_system.update(score)
            season_modifiers = season_system.get_season_modifiers()

            weather_timer += 1
            if weather_timer > 1800:
                weather_timer = 0
                weather_types = ['clear', 'rain', 'snow', 'fog']
                if random.random() < 0.3:
                    new_weather = random.choice(weather_types)
                    weather_system.set_weather(new_weather, random.uniform(0.5, 1.0))

            weather_system.update()

            for layer in bg_layers:
                layer.update(PIPE_SPEED)

            bird.update(season_modifiers, weather_system, pipes)

            if bird.y > HEIGHT - GROUND_HEIGHT - bird.size or bird.y < -bird.size:
                game_over = True
                game_state.save_high_score(score)
                game_state.total_score += score

            pipe_timer += 1
            if pipe_timer > 90:
                pipes.append(Pipe(WIDTH))
                pipe_timer = 0

                if random.random() < POWER_UP_CHANCE:
                    power_type = random.choice(['star', 'shield'])
                    power_y = random.randint(100, HEIGHT - GROUND_HEIGHT - 100)
                    power_ups.append(PowerUp(WIDTH + 150, power_y, power_type))

            for pipe in pipes[:]:
                pipe.update()

                if not pipe.scored and pipe.x + PIPE_WIDTH < bird.x:
                    pipe.scored = True
                    points = 1

                    if season_system.current_season == 'winter':
                        points = 2
                    elif weather_system.weather_type == 'fog':
                        points = 3

                    score += points
                    score_popup_timer = 60
                    score_popup_points = points
                    score_popup_x = bird.x
                    score_popup_y = bird.y - 30
                    sound_manager.play('score')

                    for _ in range(5):
                        particles.append(Particle(
                            bird.x + random.randint(-20, 20),
                            bird.y + random.randint(-20, 20),
                            STAR_YELLOW,
                            (random.uniform(-2, 2), random.uniform(-3, -1))
                        ))

                if not bird.invincible:
                    bird_rect = bird.get_collision_rect()
                    for pipe_rect in pipe.get_rects():
                        if bird_rect.colliderect(pipe_rect):
                            game_over = True
                            game_state.save_high_score(score)
                            game_state.total_score += score
                            break

                if pipe.is_off_screen():
                    pipes.remove(pipe)

            for power_up in power_ups[:]:
                power_up.update()

                if bird.get_rect().colliderect(power_up.get_rect()) and not power_up.collected:
                    power_up.collected = True
                    sound_manager.play('powerup')

                    if power_up.power_type == 'star':
                        bonus_points = 5
                        score += bonus_points
                        score_popup_timer = 60
                        score_popup_points = bonus_points
                        score_popup_x = power_up.x
                        score_popup_y = power_up.y

                        for _ in range(10):
                            particles.append(Particle(
                                power_up.x + random.randint(-30, 30),
                                power_up.y + random.randint(-30, 30),
                                STAR_YELLOW,
                                (random.uniform(-4, 4), random.uniform(-5, -1))
                            ))

                    elif power_up.power_type == 'shield':
                        bird.shield_time = 300

                        for _ in range(8):
                            particles.append(Particle(
                                power_up.x + random.randint(-25, 25),
                                power_up.y + random.randint(-25, 25),
                                POWER_UP_PURPLE,
                                (random.uniform(-3, 3), random.uniform(-4, -1))
                            ))

                    power_ups.remove(power_up)
                elif power_up.is_off_screen():
                    power_ups.remove(power_up)

            for particle in particles[:]:
                particle.update()
                if particle.life <= 0:
                    particles.remove(particle)

            if score_popup_timer > 0:
                score_popup_timer -= 1

        draw_background(screen, time_system, season_system, bg_layers, weather_system)

        season_modifiers = season_system.get_season_modifiers()
        for pipe in pipes:
            pipe.draw(screen, season_modifiers['pipe_color'])

        for power_up in power_ups:
            if not power_up.collected:
                power_up.draw(screen)

        for particle in particles:
            particle.draw(screen)

        bird.draw(screen)

        weather_system.draw(screen)

        draw_score(screen, score)
        draw_season_indicator(screen, season_system.current_season)
        draw_weather_indicator(screen, weather_system)

        if score_popup_timer > 0:
            draw_score_popup(screen, score_popup_x, score_popup_y, score_popup_points, score_popup_timer)

        if bird.invincible:
            shield_text = small_font.render(f'Shield: {bird.shield_time//60 + 1}s', True, POWER_UP_PURPLE)
            screen.blit(shield_text, (10, HEIGHT - 30))

        if game_over:
            draw_game_over(screen, score, game_state.high_score, game_state)

        pygame.display.flip()

    pygame.quit()

if __name__ == "__main__":
    main()