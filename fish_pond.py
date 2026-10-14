import pygame
import random
import math
from pathlib import Path

# Initialize Pygame
pygame.init()

# Constants
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 680
HUD_HEIGHT = 60
POND = pygame.Rect(45, HUD_HEIGHT + 40, WINDOW_WIDTH - 90, WINDOW_HEIGHT - HUD_HEIGHT - 80)

# Koi body
SEGMENTS = 12
SEGMENT_SPACING = 4.5
BODY_RADIUS = 9
BODY_SHAPE = [0.8, 1.0, 1.0, 0.95, 0.9, 0.8, 0.7, 0.6, 0.5, 0.4, 0.3, 0.25]  # Thick near the head, thin at the tail

# Player koi
START_SIZE = 1.0
GROWTH = 0.035           # Size gained per pellet
ACCELERATION = 0.45
WATER_DRAG = 0.93
FOOD_VALUE = 14          # How much hunger one pellet fills
MAX_HUNGER = 100
GOLDEN_CHANCE = 0.08     # Golden pellets are worth more
FOOD_LIFE = 9000         # Pellets dissolve after this long (milliseconds)

# Save files, kept next to this file
HIGH_SCORE_FILE = Path(__file__).parent / "highscore.txt"
LEVEL_FILE = Path(__file__).parent / "unlocked_level.txt"

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PELLET = (150, 95, 45)
GOLD = (255, 210, 40)
LILY = (70, 160, 60)
LILY_DARK = (50, 120, 45)
HUD_COLOR = (30, 60, 35)
YELLOW = (255, 220, 0)
RED = (220, 40, 40)
PLAYER_COLORS = ((255, 120, 20), (255, 245, 235))   # Orange koi with white patches
RIVAL_COLORS = [((245, 245, 245), (30, 30, 30)), ((230, 60, 40), (250, 250, 250)),
                ((240, 200, 60), (255, 255, 255)), ((60, 60, 70), (230, 120, 40)),
                ((200, 80, 200), (250, 250, 250))]

# FPS
FPS = 60

# ---- The 10 ponds ----
# islands are (x, y, radius) with x and y as fractions across the pond
THEMES = [
    {"name": "Garden Pond", "shape": "rect", "ground": (90, 150, 60), "water": ((60, 140, 140), (25, 80, 95)),
     "border": "stones", "islands": [], "lily_pads": 7, "flower": (255, 170, 200), "extras": []},
    {"name": "Lotus Lake", "shape": "oval", "ground": (110, 165, 70), "water": ((70, 150, 130), (30, 90, 90)),
     "border": "stones", "islands": [], "lily_pads": 13, "flower": (255, 120, 170), "extras": ["lotus"]},
    {"name": "Rock Garden", "shape": "rect", "ground": (215, 200, 165), "water": ((70, 130, 150), (30, 70, 95)),
     "border": "rocks", "islands": [(0.3, 0.42, 45), (0.7, 0.62, 55)], "lily_pads": 3, "flower": (255, 255, 255),
     "extras": ["raked_sand"]},
    {"name": "Autumn Pond", "shape": "oval", "ground": (170, 120, 50), "water": ((70, 110, 100), (30, 60, 60)),
     "border": "brown_rocks", "islands": [], "lily_pads": 4, "flower": (255, 200, 120), "extras": ["leaves"]},
    {"name": "Bamboo Grove", "shape": "rect", "ground": (80, 120, 50), "water": ((50, 130, 110), (20, 70, 70)),
     "border": "bamboo", "islands": [(0.62, 0.5, 42)], "lily_pads": 5, "flower": (255, 240, 150), "extras": ["bridge"]},
    {"name": "Desert Oasis", "shape": "oval", "ground": (225, 195, 130), "water": ((60, 190, 190), (20, 110, 130)),
     "border": "brown_rocks", "islands": [(0.5, 0.5, 50)], "lily_pads": 3, "flower": (255, 150, 80),
     "island_color": (220, 190, 130), "extras": ["palms"]},
    {"name": "Temple Pond", "shape": "rect", "ground": (120, 110, 100), "water": ((50, 120, 130), (20, 60, 80)),
     "border": "bricks", "islands": [(0.25, 0.5, 40), (0.75, 0.5, 40)], "lily_pads": 6, "flower": (255, 255, 255),
     "extras": ["lanterns"]},
    {"name": "Winter Pond", "shape": "oval", "ground": (235, 240, 245), "water": ((120, 170, 200), (50, 100, 140)),
     "border": "snow", "islands": [(0.35, 0.4, 35), (0.65, 0.65, 35)], "lily_pads": 0, "flower": WHITE,
     "island_color": (240, 245, 250), "extras": ["ice", "snow"]},
    {"name": "Moonlight Pond", "shape": "rect", "ground": (25, 40, 30), "water": ((25, 50, 75), (10, 20, 40)),
     "border": "dark_stones", "islands": [(0.5, 0.3, 40), (0.28, 0.7, 35), (0.72, 0.7, 35)], "lily_pads": 6,
     "flower": (200, 200, 255), "island_color": (60, 70, 70), "extras": ["moon", "fireflies"]},
    {"name": "Royal Koi Pond", "shape": "oval", "ground": (60, 110, 50), "water": ((40, 110, 170), (15, 50, 100)),
     "border": "marble", "islands": [(0.5, 0.5, 55)], "lily_pads": 8, "flower": (255, 215, 0),
     "island_color": (235, 235, 230), "extras": ["fountain"]},
]

def level_settings(level):
    # Everything that gets harder as you go: level 1 is gentle, level 10 is a feeding frenzy
    i = level - 1
    return {
        "target_size": 1.5 + 0.05 * i,          # Grow this big to move on
        "player_speed": 4.5 + 0.08 * i,
        "hunger_drain": 3.5 + 0.3 * i,          # Per second (times your size)
        "rivals": 2 + i // 3,                   # 2, 2, 2, 3, 3, 3, 4, 4, 4, 5
        "rival_speed": 2.2 + 0.3 * i,           # Faster than you by the last levels
        "rival_turn": 0.18 + 0.04 * i,          # How sharply they steer toward food
        "rival_reach": 1.2 * i,                 # Bigger bites
        "rival_dash": 1 + 0.04 * i,             # Speed boost when food is close
        "rival_steal": level >= 6,              # Some rivals go for the food nearest to you
        "max_food": 12 + i // 2,
        "spawn_every": (max(450, 900 - 45 * i), max(800, 1600 - 70 * i)),
    }

class Koi:
    def __init__(self, x, y, colors, size=START_SIZE):
        self.x, self.y = x, y
        self.dx, self.dy = 0, 0
        self.size = size
        self.main_color, self.patch_color = colors
        self.points = [(x - i * SEGMENT_SPACING, y) for i in range(SEGMENTS)]
        self.wiggle_offset = random.uniform(0, 1000)

    def swim(self, ax, ay, max_speed, keep_in_pond):
        # Push in a direction; water drag slows the fish down over time
        self.dx = (self.dx + ax) * WATER_DRAG
        self.dy = (self.dy + ay) * WATER_DRAG
        speed = math.hypot(self.dx, self.dy)
        if speed > max_speed:
            self.dx, self.dy = self.dx / speed * max_speed, self.dy / speed * max_speed
        self.x, self.y = keep_in_pond(self.x + self.dx, self.y + self.dy, 15)

    def update_body(self, time):
        # The head swings side to side as the fish swims, and every body
        # segment follows the one in front of it, so the swing travels down the body
        speed = math.hypot(self.dx, self.dy)
        heading = self.heading()
        wiggle = math.sin((time + self.wiggle_offset) / 110) * min(speed, 3) * 1.3
        head_x = self.x - math.sin(heading) * wiggle
        head_y = self.y + math.cos(heading) * wiggle
        self.points[0] = (head_x, head_y)

        spacing = SEGMENT_SPACING * self.size
        for i in range(1, SEGMENTS):
            px, py = self.points[i - 1]
            x, y = self.points[i]
            distance = math.hypot(x - px, y - py) or 1
            self.points[i] = (px + (x - px) / distance * spacing, py + (y - py) / distance * spacing)

    def heading(self):
        # Direction from the second segment to the head
        (hx, hy), (nx, ny) = self.points[0], self.points[1]
        return math.atan2(hy - ny, hx - nx)

    def mouth(self):
        heading = self.heading()
        reach = BODY_RADIUS * self.size
        return self.points[0][0] + math.cos(heading) * reach, self.points[0][1] + math.sin(heading) * reach

    def draw_shadow(self, screen, color):
        for i in range(SEGMENTS - 1, -1, -1):
            x, y = self.points[i]
            pygame.draw.circle(screen, color, (x + 6, y + 8), BODY_RADIUS * self.size * BODY_SHAPE[i])

    def draw(self, screen, time):
        size = self.size
        heading = self.heading()
        side_x, side_y = -math.sin(heading), math.cos(heading)

        # Tail fin: two lobes that swish behind the last segment
        tail_x, tail_y = self.points[-1]
        (bx, by) = self.points[-2]
        tail_angle = math.atan2(tail_y - by, tail_x - bx) + math.sin((time + self.wiggle_offset) / 110) * 0.35
        for spread in (-0.5, 0.5):
            tip = (tail_x + math.cos(tail_angle + spread) * 16 * size, tail_y + math.sin(tail_angle + spread) * 16 * size)
            middle = (tail_x + math.cos(tail_angle) * 9 * size, tail_y + math.sin(tail_angle) * 9 * size)
            pygame.draw.polygon(screen, self.main_color, [(tail_x, tail_y), tip, middle])

        # Side fins near the head
        fin_x, fin_y = self.points[2]
        for side in (-1, 1):
            base = (fin_x + side_x * side * BODY_RADIUS * size * 0.8, fin_y + side_y * side * BODY_RADIUS * size * 0.8)
            tip = (base[0] + side_x * side * 8 * size - math.cos(heading) * 7 * size,
                   base[1] + side_y * side * 8 * size - math.sin(heading) * 7 * size)
            back = (fin_x - math.cos(heading) * 6 * size, fin_y - math.sin(heading) * 6 * size)
            pygame.draw.polygon(screen, self.main_color, [base, tip, back])

        # Body, tail to head
        for i in range(SEGMENTS - 1, -1, -1):
            pygame.draw.circle(screen, self.main_color, self.points[i], BODY_RADIUS * size * BODY_SHAPE[i])

        # Koi patches on a few segments
        for i, offset in ((1, -0.35), (4, 0.4), (7, -0.2)):
            x, y = self.points[i]
            radius = BODY_RADIUS * size * BODY_SHAPE[i] * 0.55
            pygame.draw.circle(screen, self.patch_color, (x + side_x * offset * radius, y + side_y * offset * radius), radius)

        # Eyes on both sides of the head
        hx, hy = self.points[0]
        for side in (-1, 1):
            eye = (hx + math.cos(heading) * 4 * size + side_x * side * 5 * size,
                   hy + math.sin(heading) * 4 * size + side_y * side * 5 * size)
            pygame.draw.circle(screen, BLACK, eye, max(2, 2 * size))

class FishPondGame:
    def __init__(self):
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("Fish Pond")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.Font(None, 36)
        self.big_font = pygame.font.Font(None, 80)
        self.small_font = pygame.font.Font(None, 24)

        self.high_score = self.load_number(HIGH_SCORE_FILE, 0)
        self.unlocked_level = max(1, min(len(THEMES), self.load_number(LEVEL_FILE, 1)))
        self.state = "menu"  # "menu", "playing", "paused", "level_complete", "game_over" or "won"
        self.ripples = []
        self.particles = []
        self.time = 0
        self.score = 0

        self.start_level(self.unlocked_level)

    # ---- Saving ----

    def load_number(self, path, default):
        try:
            return int(path.read_text())
        except (OSError, ValueError):
            return default

    def save_number(self, path, number):
        try:
            path.write_text(str(number))
        except OSError:
            pass  # Not being able to save shouldn't crash the game

    # ---- Levels ----

    def start_level(self, level):
        self.level = level
        self.theme = THEMES[level - 1]
        self.settings = level_settings(level)
        self.level_start_score = self.score
        self.level_bonus = 0

        # Islands in pixels for this pond
        self.islands = [(POND.left + fx * POND.width, POND.top + fy * POND.height, radius)
                        for fx, fy, radius in self.theme["islands"]]

        self.background = self.make_background()
        self.overlay = self.make_overlay()
        self.fireflies = [[random.uniform(POND.left, POND.right), random.uniform(POND.top, POND.bottom),
                           random.uniform(0, 6)] for _ in range(25)]
        self.snowflakes = [[random.uniform(0, WINDOW_WIDTH), random.uniform(0, WINDOW_HEIGHT),
                            random.uniform(0.5, 1.5)] for _ in range(80)]

        x, y = self.open_spot(POND.center)
        self.player = Koi(x, y, PLAYER_COLORS)
        self.rivals = []
        for k in range(self.settings["rivals"]):
            x, y = self.open_spot()
            self.rivals.append(Koi(x, y, RIVAL_COLORS[k % len(RIVAL_COLORS)], size=1.2))
        self.rest_spot = self.open_spot(POND.center)  # Where rivals drift when there's no food
        self.food = []
        self.ripples = []
        self.spawn_timer = 500
        self.hunger = MAX_HUNGER

    def complete_level(self):
        self.level_bonus = 100 * self.level + int(self.hunger)
        self.score += self.level_bonus
        if self.level == len(THEMES):
            self.state = "won"
        else:
            self.state = "level_complete"
            self.unlocked_level = max(self.unlocked_level, self.level + 1)
            self.save_number(LEVEL_FILE, self.unlocked_level)
        self.update_high_score()

    def end_game(self):
        self.state = "game_over"
        self.update_high_score()

    def update_high_score(self):
        self.new_high_score = self.score > self.high_score
        if self.new_high_score:
            self.high_score = self.score
            self.save_number(HIGH_SCORE_FILE, self.high_score)

    # ---- Pond shape ----

    def inside_pond(self, x, y, margin):
        if self.theme["shape"] == "oval":
            a, b = POND.width / 2 - margin, POND.height / 2 - margin
            inside = ((x - POND.centerx) / a) ** 2 + ((y - POND.centery) / b) ** 2 <= 1
        else:
            inside = POND.inflate(-margin * 2, -margin * 2).collidepoint(x, y)
        on_island = any(math.hypot(x - ix, y - iy) < radius + margin for ix, iy, radius in self.islands)
        return inside and not on_island

    def keep_in_pond(self, x, y, margin):
        # Pull a point back inside the water, and push it off any island
        if self.theme["shape"] == "oval":
            a, b = POND.width / 2 - margin, POND.height / 2 - margin
            nx, ny = (x - POND.centerx) / a, (y - POND.centery) / b
            distance = math.hypot(nx, ny)
            if distance > 1:
                x, y = POND.centerx + nx / distance * a, POND.centery + ny / distance * b
        else:
            x = max(POND.left + margin, min(POND.right - margin, x))
            y = max(POND.top + margin, min(POND.bottom - margin, y))
        for ix, iy, radius in self.islands:
            distance = math.hypot(x - ix, y - iy) or 1
            if distance < radius + margin:
                x = ix + (x - ix) / distance * (radius + margin)
                y = iy + (y - iy) / distance * (radius + margin)
        return x, y

    def open_spot(self, near=None):
        # A random spot in open water (or the spot nearest to "near" that's free)
        if near and self.inside_pond(near[0], near[1], 50):
            return near
        for _ in range(500):
            x, y = random.uniform(POND.left, POND.right), random.uniform(POND.top, POND.bottom)
            if self.inside_pond(x, y, 50):
                return x, y
        return POND.centerx, POND.top + 60

    def perimeter(self, spacing):
        # Points spaced along the edge of the pond, for drawing the border
        points = []
        if self.theme["shape"] == "oval":
            a, b = POND.width / 2, POND.height / 2
            count = int(math.pi * (a + b) / spacing)
            for k in range(count):
                angle = 2 * math.pi * k / count
                points.append((POND.centerx + math.cos(angle) * a, POND.centery + math.sin(angle) * b))
        else:
            for x in range(POND.left, POND.right + 1, spacing):
                points += [(x, POND.top), (x, POND.bottom)]
            for y in range(POND.top + spacing, POND.bottom, spacing):
                points += [(POND.left, y), (POND.right, y)]
        return points

    # ---- Drawing the pond (once per level) ----

    def make_background(self):
        theme = self.theme
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        surface.fill(theme["ground"])
        if "raked_sand" in theme["extras"]:
            # Zen garden lines raked into the sand
            darker = tuple(c - 25 for c in theme["ground"])
            for y in range(HUD_HEIGHT + 5, WINDOW_HEIGHT, 12):
                points = [(x, y + math.sin(x / 40) * 3) for x in range(0, WINDOW_WIDTH + 20, 20)]
                pygame.draw.lines(surface, darker, False, points, 2)

        # Water gets darker toward the middle of the pond, like it's deeper there
        light, dark = theme["water"]
        for step in range(30):
            t = step / 29
            color = tuple(int(light[c] + (dark[c] - light[c]) * t) for c in range(3))
            rect = POND.inflate(-step * 8, -step * 6)
            if theme["shape"] == "oval":
                pygame.draw.ellipse(surface, color, rect)
            else:
                pygame.draw.rect(surface, color, rect, border_radius=max(10, 60 - step * 2))

        if "moon" in theme["extras"]:
            # Reflection of the moon on the water
            moon = pygame.Rect(0, 0, 70, 50)
            moon.center = (POND.left + POND.width * 0.78, POND.top + POND.height * 0.3)
            pygame.draw.ellipse(surface, (210, 210, 170), moon)
            for k in range(4):
                y = moon.bottom + 8 + k * 9
                pygame.draw.line(surface, (120, 120, 110), (moon.left + k * 6, y), (moon.right - k * 6, y), 2)

        self.draw_islands(surface)
        self.draw_border(surface)

        if "lanterns" in theme["extras"]:
            for x, y in ((POND.left - 25, POND.top - 25), (POND.right + 25, POND.top - 25),
                         (POND.left - 25, POND.bottom + 25), (POND.right + 25, POND.bottom + 25)):
                self.draw_lantern(surface, x, y)
        return surface

    def draw_islands(self, surface):
        theme = self.theme
        island_color = theme.get("island_color", (130, 130, 125))
        shade = tuple(max(0, c - 40) for c in island_color)
        deep_water = theme["water"][1]
        for x, y, radius in self.islands:
            pygame.draw.circle(surface, tuple(max(0, c - 15) for c in deep_water), (x, y), radius + 10)
            pygame.draw.circle(surface, shade, (x + 3, y + 4), radius)
            pygame.draw.circle(surface, island_color, (x, y), radius)
            if "fountain" in theme["extras"]:
                # Marble fountain with a pool in the middle (the spray is animated in draw())
                pygame.draw.circle(surface, GOLD, (x, y), radius - 6, 3)
                pygame.draw.circle(surface, theme["water"][0], (x, y), radius - 16)
            elif "palms" in theme["extras"]:
                pass  # The palm tree on the oasis island is part of the overlay
            elif theme["ground"][0] < 60 or island_color[0] > 230:
                pygame.draw.circle(surface, shade, (x - radius * 0.3, y - radius * 0.2), radius * 0.35)
            else:
                # Moss and little bushes
                random.seed(int(x * y))
                for _ in range(5):
                    angle = random.uniform(0, 2 * math.pi)
                    distance = random.uniform(0, radius * 0.6)
                    pygame.draw.circle(surface, (70, 130, 60), (x + math.cos(angle) * distance, y + math.sin(angle) * distance),
                                       random.randint(6, 12))
                random.seed()

    def draw_border(self, surface):
        style = self.theme["border"]
        if style == "marble":
            band = POND.inflate(30, 30)
            if self.theme["shape"] == "oval":
                pygame.draw.ellipse(surface, (235, 235, 230), band, 26)
                pygame.draw.ellipse(surface, GOLD, band.inflate(-22, -22), 3)
            else:
                pygame.draw.rect(surface, (235, 235, 230), band, 26, border_radius=40)
                pygame.draw.rect(surface, GOLD, band.inflate(-22, -22), 3, border_radius=30)
            return

        spacing = {"bamboo": 17, "bricks": 22}.get(style, 26)
        for x, y in self.perimeter(spacing):
            if style == "bamboo":
                # Bamboo poles seen from above: green circles with a ring
                pygame.draw.circle(surface, (60, 100, 40), (x + 2, y + 3), 10)
                pygame.draw.circle(surface, (120, 170, 70), (x, y), 10)
                pygame.draw.circle(surface, (90, 140, 50), (x, y), 6, 2)
            elif style == "bricks":
                brick = pygame.Rect(0, 0, 22, 22)
                brick.center = (x, y)
                pygame.draw.rect(surface, (150, 70, 50), brick)
                pygame.draw.rect(surface, (100, 45, 30), brick, 2)
            else:
                radius = random.randint(13, 20)
                if style == "rocks":
                    radius += 4
                grey = random.randint(120, 170)
                color = {
                    "stones": (grey, grey, grey + 5),
                    "rocks": (grey + 30, grey + 25, grey + 15),
                    "brown_rocks": (grey + 20, grey - 10, grey - 50),
                    "snow": (245, 248, 252),
                    "dark_stones": (grey // 3, grey // 3, grey // 3 + 10),
                }[style]
                shadow = tuple(max(0, c - 35) for c in color)
                if style == "snow":
                    shadow = (190, 210, 230)
                pygame.draw.circle(surface, shadow, (x + 2, y + 3), radius)
                pygame.draw.circle(surface, color, (x, y), radius)

    def draw_lantern(self, surface, x, y):
        pygame.draw.rect(surface, (90, 90, 85), (x - 15, y - 15, 30, 30), border_radius=4)
        pygame.draw.rect(surface, (150, 150, 140), (x - 11, y - 11, 22, 22), border_radius=3)
        pygame.draw.circle(surface, (255, 200, 90), (x, y), 6)

    def make_overlay(self):
        # Things that float on top of the water: fish swim underneath them
        theme = self.theme
        surface = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        rng = random.Random(self.level)  # Same layout every time you play this level

        def free_spot(radius):
            for _ in range(200):
                x, y = rng.uniform(POND.left, POND.right), rng.uniform(POND.top, POND.bottom)
                if self.inside_pond(x, y, radius + 10):
                    return x, y
            return None

        flower_chance = 0.8 if "lotus" in theme["extras"] else 0.4
        for _ in range(theme["lily_pads"]):
            radius = rng.randint(22, 36)
            spot = free_spot(radius)
            if not spot:
                continue
            x, y = spot
            notch = rng.uniform(0, 2 * math.pi)
            pygame.draw.circle(surface, (*LILY_DARK, 235), (x + 3, y + 3), radius)
            pygame.draw.circle(surface, (*LILY, 235), (x, y), radius)
            # Cut a wedge out of the pad, like a real lily pad
            wedge = [(x, y),
                     (x + math.cos(notch - 0.3) * (radius + 4), y + math.sin(notch - 0.3) * (radius + 4)),
                     (x + math.cos(notch + 0.3) * (radius + 4), y + math.sin(notch + 0.3) * (radius + 4))]
            pygame.draw.polygon(surface, (0, 0, 0, 0), wedge)
            if rng.random() < flower_chance:
                for petal in range(6):
                    angle = petal * math.pi / 3
                    pygame.draw.circle(surface, (*theme["flower"], 255), (x + math.cos(angle) * 6, y + math.sin(angle) * 6), 6)
                pygame.draw.circle(surface, (*YELLOW, 255), (x, y), 4)

        if "leaves" in theme["extras"]:
            for _ in range(30):
                spot = free_spot(8)
                if spot:
                    x, y = spot
                    angle = rng.uniform(0, math.pi)
                    color = rng.choice([(230, 120, 30), (200, 60, 30), (240, 190, 50)])
                    length, width = 10, 5
                    leaf = [(x + math.cos(angle) * length, y + math.sin(angle) * length),
                            (x + math.cos(angle + math.pi / 2) * width, y + math.sin(angle + math.pi / 2) * width),
                            (x - math.cos(angle) * length, y - math.sin(angle) * length),
                            (x - math.cos(angle + math.pi / 2) * width, y - math.sin(angle + math.pi / 2) * width)]
                    pygame.draw.polygon(surface, (*color, 240), leaf)

        if "ice" in theme["extras"]:
            for _ in range(6):
                spot = free_spot(25)
                if spot:
                    x, y = spot
                    points = [(x + math.cos(a) * rng.uniform(18, 32), y + math.sin(a) * rng.uniform(12, 24))
                              for a in [k * math.pi / 4 for k in range(8)]]
                    pygame.draw.polygon(surface, (240, 250, 255, 190), points)

        if "bridge" in theme["extras"]:
            # Wooden bridge across the pond
            bridge = pygame.Rect(POND.left + POND.width * 0.28 - 30, POND.top - 30, 60, POND.height + 60)
            pygame.draw.rect(surface, (120, 80, 40, 255), bridge.move(4, 4))
            pygame.draw.rect(surface, (170, 120, 70, 255), bridge)
            for y in range(bridge.top, bridge.bottom, 12):
                pygame.draw.line(surface, (120, 80, 40, 255), (bridge.left, y), (bridge.right, y), 2)
            pygame.draw.rect(surface, (100, 60, 30, 255), (bridge.left - 4, bridge.top, 6, bridge.height))
            pygame.draw.rect(surface, (100, 60, 30, 255), (bridge.right - 2, bridge.top, 6, bridge.height))

        if "palms" in theme["extras"]:
            # Palm trees seen from above, hanging over the water
            spots = [(POND.left + 20, POND.top + 30), (POND.right - 20, POND.bottom - 30), (POND.right - 40, POND.top + 20)]
            spots += [(ix, iy) for ix, iy, _ in self.islands]
            for x, y in spots:
                for k in range(7):
                    angle = k * 2 * math.pi / 7
                    tip = (x + math.cos(angle) * 48, y + math.sin(angle) * 48)
                    side = (math.cos(angle + math.pi / 2) * 9, math.sin(angle + math.pi / 2) * 9)
                    mid = (x + math.cos(angle) * 24, y + math.sin(angle) * 24)
                    pygame.draw.polygon(surface, (50, 130, 50, 245),
                                        [(x, y), (mid[0] + side[0], mid[1] + side[1]), tip, (mid[0] - side[0], mid[1] - side[1])])
                pygame.draw.circle(surface, (120, 85, 45, 255), (x, y), 8)
        return surface

    # ---- Game loop pieces ----

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False

            if event.type != pygame.KEYDOWN:
                continue

            if event.key == pygame.K_ESCAPE:
                return False

            if self.state == "menu":
                if event.key == pygame.K_SPACE:
                    self.score = 0
                    self.start_level(1)
                    self.state = "playing"
                elif event.key == pygame.K_c and self.unlocked_level > 1:
                    self.score = 0
                    self.start_level(self.unlocked_level)
                    self.state = "playing"

            elif self.state == "playing":
                if event.key == pygame.K_p:
                    self.state = "paused"

            elif self.state == "paused":
                if event.key in (pygame.K_p, pygame.K_SPACE):
                    self.state = "playing"

            elif self.state == "level_complete":
                if event.key == pygame.K_SPACE:
                    self.start_level(self.level + 1)
                    self.state = "playing"

            elif self.state == "game_over":
                if event.key == pygame.K_SPACE:
                    # Try the same level again, with the score you had when you started it
                    self.score = self.level_start_score
                    self.start_level(self.level)
                    self.state = "playing"
                elif event.key == pygame.K_m:
                    self.state = "menu"

            elif self.state == "won":
                if event.key in (pygame.K_SPACE, pygame.K_m):
                    self.score = 0
                    self.start_level(1)
                    self.state = "menu"

        return True

    def update(self, dt):
        self.time += dt
        self.update_effects(dt)

        # Fish keep gently moving their bodies even on the menu
        for koi in [self.player] + self.rivals:
            koi.update_body(self.time)

        if self.state != "playing":
            return

        self.move_player()
        self.move_rivals()
        self.spawn_food(dt)

        # Pellets slowly dissolve
        for pellet in self.food:
            pellet["life"] -= dt
        self.food = [pellet for pellet in self.food if pellet["life"] > 0]

        # Eating: player first, then the rivals get whatever they reach
        for pellet in self.food[:]:
            if self.touches(self.player, pellet, 0):
                self.eat(pellet)
                continue
            for rival in self.rivals:
                if self.touches(rival, pellet, self.settings["rival_reach"]):
                    self.food.remove(pellet)
                    rival.size = min(1.8, rival.size + 0.015)  # Rivals grow a little too
                    self.ripples.append([pellet["x"], pellet["y"], 4, 1.0])
                    break

        if self.player.size >= self.settings["target_size"]:
            self.complete_level()
            return

        # Hunger drains faster the bigger you are
        self.hunger -= self.settings["hunger_drain"] * self.player.size * dt / 1000
        if self.hunger <= 0:
            self.hunger = 0
            self.end_game()

    def move_player(self):
        keys = pygame.key.get_pressed()
        ax = ay = 0
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            ax -= ACCELERATION
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            ax += ACCELERATION
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            ay -= ACCELERATION
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            ay += ACCELERATION
        self.player.swim(ax, ay, self.settings["player_speed"], self.keep_in_pond)

    def move_rivals(self):
        settings = self.settings
        for k, rival in enumerate(self.rivals):
            target = None
            if self.food:
                if settings["rival_steal"] and k % 2 == 1:
                    # Sneaky rival: goes for the pellet closest to YOU
                    target = min(self.food, key=lambda p: math.hypot(p["x"] - self.player.x, p["y"] - self.player.y))
                else:
                    target = min(self.food, key=lambda p: math.hypot(p["x"] - rival.x, p["y"] - rival.y))

            if target:
                tx, ty = target["x"], target["y"]
                push = settings["rival_turn"]
            else:
                tx, ty = self.rest_spot  # Nothing to eat: drift back to their resting spot
                push = 0.08
            distance = math.hypot(tx - rival.x, ty - rival.y) or 1
            ax, ay = (tx - rival.x) / distance * push, (ty - rival.y) / distance * push

            # Swim around islands instead of getting stuck on them
            for ix, iy, radius in self.islands:
                away_x, away_y = rival.x - ix, rival.y - iy
                gap = math.hypot(away_x, away_y) or 1
                if gap < radius + 45:
                    ax += -away_y / gap * push * 1.5
                    ay += away_x / gap * push * 1.5

            speed = settings["rival_speed"]
            if target and distance < 150:
                speed *= settings["rival_dash"]  # Lunge at food that's close
            rival.swim(ax, ay, speed, self.keep_in_pond)

    def touches(self, koi, pellet, extra_reach):
        mx, my = koi.mouth()
        return math.hypot(mx - pellet["x"], my - pellet["y"]) < 8 + 5 * koi.size + extra_reach

    def spawn_food(self, dt):
        # Food lands in little handfuls, making a ripple
        self.spawn_timer -= dt
        if self.spawn_timer > 0 or len(self.food) >= self.settings["max_food"]:
            return
        self.spawn_timer = random.randint(*self.settings["spawn_every"])
        cx, cy = self.open_spot()
        for _ in range(random.randint(1, 3)):
            x, y = cx + random.randint(-25, 25), cy + random.randint(-25, 25)
            if self.inside_pond(x, y, 20):
                self.food.append({"x": x, "y": y, "life": FOOD_LIFE, "golden": random.random() < GOLDEN_CHANCE})
        self.ripples.append([cx, cy, 5, 1.0])

    def eat(self, pellet):
        self.food.remove(pellet)
        golden = pellet["golden"]
        self.score += 50 if golden else 10
        self.hunger = MAX_HUNGER if golden else min(MAX_HUNGER, self.hunger + FOOD_VALUE)
        self.player.size += GROWTH * (3 if golden else 1)
        self.burst(pellet["x"], pellet["y"], GOLD if golden else PELLET)
        self.ripples.append([pellet["x"], pellet["y"], 4, 1.0])

    def burst(self, x, y, color):
        # Little explosion of particles
        for _ in range(12):
            angle = random.uniform(0, 2 * math.pi)
            speed = random.uniform(0.03, 0.12)
            self.particles.append({
                "x": x, "y": y,
                "vx": math.cos(angle) * speed, "vy": math.sin(angle) * speed,
                "life": random.uniform(250, 500), "color": color,
            })

    def update_effects(self, dt):
        for particle in self.particles:
            particle["x"] += particle["vx"] * dt
            particle["y"] += particle["vy"] * dt
            particle["life"] -= dt
        self.particles = [p for p in self.particles if p["life"] > 0]

        # Ripples grow outward and fade away
        for ripple in self.ripples:
            ripple[2] += dt * 0.04
            ripple[3] -= dt / 1200
        self.ripples = [r for r in self.ripples if r[3] > 0]
        if random.random() < 0.01:
            # The odd random ripple, like a bug landing on the water
            x, y = self.open_spot()
            self.ripples.append([x, y, 3, 0.6])

        for flake in self.snowflakes:
            flake[1] += flake[2] * dt * 0.05
            flake[0] += math.sin((self.time + flake[1] * 10) / 600) * 0.3
            if flake[1] > WINDOW_HEIGHT:
                flake[0], flake[1] = random.uniform(0, WINDOW_WIDTH), HUD_HEIGHT
        for firefly in self.fireflies:
            firefly[0] += math.sin(self.time / 900 + firefly[2]) * 0.4
            firefly[1] += math.cos(self.time / 1100 + firefly[2] * 2) * 0.3

    # ---- Drawing each frame ----

    def draw(self):
        self.screen.blit(self.background, (0, 0))
        extras = self.theme["extras"]
        deep_water = self.theme["water"][1]

        for x, y, radius, strength in self.ripples:
            color = tuple(int(deep_water[c] + (220 - deep_water[c]) * strength * 0.6) for c in range(3))
            pygame.draw.circle(self.screen, color, (x, y), radius, 2)

        if "fountain" in extras:
            # Water spraying up from the fountain in the middle
            fx, fy, radius = self.islands[0]
            for k in range(12):
                angle = k * math.pi / 6 + self.time / 800
                reach = (radius - 18) * (0.4 + 0.6 * abs(math.sin(self.time / 300 + k)))
                pygame.draw.circle(self.screen, (200, 230, 255), (fx + math.cos(angle) * reach, fy + math.sin(angle) * reach), 3)
            pygame.draw.circle(self.screen, WHITE, (fx, fy), 6)

        for pellet in self.food:
            # Flicker when about to dissolve
            if pellet["life"] < 2000 and (self.time // 150) % 2 == 0:
                continue
            color = GOLD if pellet["golden"] else PELLET
            radius = 6 if pellet["golden"] else 4
            pygame.draw.circle(self.screen, color, (pellet["x"], pellet["y"]), radius)
            pygame.draw.circle(self.screen, WHITE, (pellet["x"] - 1, pellet["y"] - 1), 1)

        shadow = tuple(max(0, c - 25) for c in deep_water)
        fish = self.rivals + [self.player]  # Player drawn last so it's on top
        for koi in fish:
            koi.draw_shadow(self.screen, shadow)
        for koi in fish:
            koi.draw(self.screen, self.time)

        # Lily pads, leaves, bridges... float on top - fish swim underneath them
        self.screen.blit(self.overlay, (0, 0))

        if "fireflies" in extras:
            for x, y, offset in self.fireflies:
                if math.sin(self.time / 400 + offset * 3) > -0.3:
                    pygame.draw.circle(self.screen, (120, 120, 40), (x, y), 5)
                    pygame.draw.circle(self.screen, (255, 255, 150), (x, y), 2)
        if "snow" in extras:
            for x, y, size in self.snowflakes:
                pygame.draw.circle(self.screen, WHITE, (x, y), size + 1)

        self.draw_particles()
        self.draw_hud()
        self.draw_screens()

        pygame.display.flip()

    def draw_particles(self):
        for particle in self.particles:
            size = max(1, int(particle["life"] / 120))
            pygame.draw.circle(self.screen, particle["color"], (int(particle["x"]), int(particle["y"])), size)

    def draw_hud(self):
        pygame.draw.rect(self.screen, HUD_COLOR, (0, 0, WINDOW_WIDTH, HUD_HEIGHT))
        score_text = self.font.render(f"Score: {self.score}", True, WHITE)
        self.screen.blit(score_text, (15, 8))
        level_text = self.small_font.render(f"Level {self.level}: {self.theme['name']}", True, (180, 220, 180))
        self.screen.blit(level_text, (15, 37))
        best_text = self.font.render(f"Best: {self.high_score}", True, YELLOW)
        self.screen.blit(best_text, best_text.get_rect(topright=(WINDOW_WIDTH - 15, 18)))

        # Growth bar: fill it to move on to the next pond
        growth = (self.player.size - START_SIZE) / (self.settings["target_size"] - START_SIZE)
        self.draw_bar("Growth", 12, max(0, min(1, growth)), (90, 170, 255))

        # Hunger bar: green when full, yellow, then red when nearly empty
        fullness = self.hunger / MAX_HUNGER
        if fullness > 0.5:
            color = (int(60 + 180 * (1 - fullness) * 2), 200, 60)
        else:
            color = (240, int(60 + 140 * fullness * 2), 60)
        self.draw_bar("Hunger", 34, fullness, color)

    def draw_bar(self, label, y, fullness, color):
        bar = pygame.Rect(WINDOW_WIDTH // 2 - 60, y, 200, 14)
        text = self.small_font.render(label, True, WHITE)
        self.screen.blit(text, text.get_rect(midright=(bar.left - 10, bar.centery)))
        pygame.draw.rect(self.screen, BLACK, bar, border_radius=7)
        pygame.draw.rect(self.screen, color, (bar.x, bar.y, bar.width * fullness, bar.height), border_radius=7)
        pygame.draw.rect(self.screen, WHITE, bar, 2, border_radius=7)

    def draw_screens(self):
        if self.state == "menu":
            lines = [
                "Eat food to grow - outgrow 10 different ponds!",
                "Keep your hunger bar from running out",
                "The other koi get hungrier every level",
                "Arrows / WASD to swim     SPACE: start at level 1",
            ]
            if self.unlocked_level > 1:
                lines.append(f"C: continue from level {self.unlocked_level}")
            self.draw_overlay("FISH POND", lines)
        elif self.state == "paused":
            self.draw_overlay("PAUSED", ["Press P to continue"])
        elif self.state == "level_complete":
            next_theme = THEMES[self.level]
            rivals_next = level_settings(self.level + 1)["rivals"]
            warning = "...and there's one more of them!" if rivals_next > self.settings["rivals"] else ""
            lines = [f"Level bonus: +{self.level_bonus}",
                     f"Next pond: {next_theme['name']}",
                     "The other koi are getting hungrier" + ("" if warning else "..."),
                     warning, "SPACE to swim on"]
            self.draw_overlay(f"LEVEL {self.level} COMPLETE!", [line for line in lines if line])
        elif self.state == "game_over":
            lines = ["Your koi got too hungry!", f"Score: {self.score}    Best: {self.high_score}"]
            if self.new_high_score:
                lines.append("NEW HIGH SCORE!")
            lines.append(f"SPACE: try level {self.level} again   M: menu")
            self.draw_overlay("GAME OVER", lines)
        elif self.state == "won":
            lines = ["You outgrew all 10 ponds!", "You're the king of the koi!",
                     f"Final score: {self.score}    Best: {self.high_score}"]
            if self.new_high_score:
                lines.append("NEW HIGH SCORE!")
            lines.append("SPACE for menu")
            self.draw_overlay("YOU WIN!", lines)

    def draw_overlay(self, title, lines):
        # Darken the game behind the message
        shade = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT), pygame.SRCALPHA)
        shade.fill((0, 0, 0, 160))
        self.screen.blit(shade, (0, 0))

        title_text = self.big_font.render(title, True, WHITE)
        y = WINDOW_HEIGHT // 2 - 40 - len(lines) * 18
        self.screen.blit(title_text, title_text.get_rect(center=(WINDOW_WIDTH // 2, y)))
        y += 70
        for line in lines:
            color = YELLOW if "HIGH SCORE" in line or line.startswith("Next pond") else WHITE
            text = self.font.render(line, True, color)
            self.screen.blit(text, text.get_rect(center=(WINDOW_WIDTH // 2, y)))
            y += 40

    def run(self):
        running = True
        while running:
            dt = self.clock.tick(FPS)
            running = self.handle_events()
            self.update(dt)
            self.draw()

        pygame.quit()

if __name__ == "__main__":
    game = FishPondGame()
    game.run()
