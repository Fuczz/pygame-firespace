"""Game ban tau vu tru nho, viet de nguoi moi hoc Python co the doc duoc."""

import array
import json
import math
import random
from pathlib import Path

import pygame


# ------------------------------- Cai dat game -------------------------------
WIDTH, HEIGHT = 960, 540
FPS = 60
PLAYER_SPEED = 5
BULLET_SPEED = 10
STARTING_LIVES = 3
BACKGROUND = (70, 58, 73)
WHITE = (250, 246, 247)
SAVE_FILE = Path("space_shooter_save.json")
ASSET_DIR = Path(__file__).resolve().parent / "assets"


def get_game_font(size, bold=False):
    """Chon font he thong co day du dau tieng Viet, co font du phong."""
    for name in ("segoeui", "tahoma", "arial", "dejavusans"):
        font_path = pygame.font.match_font(name, bold=bold)
        if font_path:
            return pygame.font.Font(font_path, size)
    return pygame.font.Font(None, size)


def make_sweep(start_frequency, end_frequency, duration, volume, grit=0.0):
    """Tao hieu ung am thanh manh hon voi am tram, hoa am va tieng va dap."""
    sample_rate = 22050
    samples = array.array("h")
    total = int(sample_rate * duration)
    phase = 0.0
    for i in range(total):
        progress = i / max(1, total - 1)
        frequency = start_frequency + (end_frequency - start_frequency) * progress
        phase += 2 * math.pi * frequency / sample_rate
        attack = min(1.0, i / max(1, sample_rate * 0.008))
        envelope = attack * (1 - progress) ** 1.7
        layered_tone = math.sin(phase) + 0.30 * math.sin(phase * 2.01) + 0.12 * math.sin(phase * 3.03)
        noise = random.uniform(-1, 1) * grit * (1 - progress) ** 2
        value = max(-1, min(1, (layered_tone * 0.7 + noise) * envelope))
        samples.append(int(32767 * volume * value))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_gunshot():
    """Phat tieng sung ngan: tieng crack, than am tram va tieng doi xa."""
    sample_rate = 22050
    duration = 0.30
    total = int(sample_rate * duration)
    raw = [random.uniform(-1, 1) for _ in range(total)]
    low_pass = []
    filtered = 0.0
    for value in raw:
        filtered += 0.105 * (value - filtered)
        low_pass.append(filtered)

    samples = array.array("h")
    echo_delay = int(sample_rate * 0.055)
    far_echo_delay = int(sample_rate * 0.105)
    for i in range(total):
        t = i / sample_rate
        high = raw[i] - low_pass[i]
        crack = high * math.exp(-t * 105)
        body = low_pass[i] * math.exp(-t * 13)
        thump = math.sin(2 * math.pi * (92 - 28 * t) * t) * math.exp(-t * 19)
        echo = 0.0
        if i >= echo_delay:
            echo += (raw[i - echo_delay] - low_pass[i - echo_delay]) * 0.20 * math.exp(-t * 10)
        if i >= far_echo_delay:
            echo += (raw[i - far_echo_delay] - low_pass[i - far_echo_delay]) * 0.10 * math.exp(-t * 12)
        envelope = min(1.0, t / 0.0025)
        mixed = envelope * (0.75 * crack + 0.34 * body + 0.66 * thump + echo)
        samples.append(int(32767 * 0.72 * max(-1, min(1, mixed))))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_explosion(duration=0.8, volume=0.72, rumble_frequency=48):
    """Tieng no nhieu lop: xung no, tieng ran va rumble tram keo dai."""
    sample_rate = 22050
    total = int(sample_rate * duration)
    raw = [random.uniform(-1, 1) for _ in range(total)]
    low_pass = []
    filtered = 0.0
    for value in raw:
        filtered += 0.038 * (value - filtered)
        low_pass.append(filtered)

    samples = array.array("h")
    echo_delay = int(sample_rate * 0.12)
    phase = 0.0
    for i in range(total):
        t = i / sample_rate
        progress = i / max(1, total - 1)
        phase += 2 * math.pi * (rumble_frequency - 15 * progress) / sample_rate
        high = raw[i] - low_pass[i]
        blast = high * math.exp(-t * 27)
        crackle = high * math.exp(-t * 6.5)
        debris = low_pass[i] * math.exp(-t * 4.2)
        rumble = low_pass[i] * math.exp(-t * 2.1)
        sub_bass = math.sin(phase) * math.exp(-t * 2.4)
        echo = 0.0
        if i >= echo_delay:
            echo = (raw[i - echo_delay] - low_pass[i - echo_delay]) * 0.15 * math.exp(-t * 3.6)
        envelope = min(1.0, t / 0.003) * (1 - progress * 0.22)
        mixed = envelope * (0.56 * blast + 0.30 * crackle + 0.48 * debris + 0.82 * rumble + 0.55 * sub_bass + echo)
        samples.append(int(32767 * volume * max(-1, min(1, mixed))))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_pickup_sound():
    """Am nhat vat tang dan theo ba not de nhan ra ro rang."""
    sample_rate = 22050
    duration = 0.48
    notes = (660, 880, 1175)
    samples = array.array("h")
    total = int(sample_rate * duration)
    for i in range(total):
        progress = i / total
        note_position = progress * len(notes)
        note_index = min(len(notes) - 1, int(note_position))
        local = note_position - note_index
        frequency = notes[note_index]
        envelope = math.sin(math.pi * local) * (1 - progress * 0.35)
        wave = math.sin(2 * math.pi * frequency * i / sample_rate)
        wave += 0.22 * math.sin(4 * math.pi * frequency * i / sample_rate)
        samples.append(int(32767 * 0.28 * envelope * wave))
    return pygame.mixer.Sound(buffer=samples.tobytes())


def make_music():
    """Tao mot nen am thanh vu tru nhe, lap lien tuc khi dang choi."""
    sample_rate = 22050
    duration = 2.4
    samples = array.array("h")
    for i in range(int(sample_rate * duration)):
        t = i / sample_rate
        pulse = 0.5 + 0.5 * math.sin(2 * math.pi * 0.8 * t)
        wave = math.sin(2 * math.pi * 110 * t) + 0.35 * math.sin(2 * math.pi * 164.81 * t)
        samples.append(int(32767 * 0.035 * pulse * wave))
    return pygame.mixer.Sound(buffer=samples.tobytes())


class SoundEffects:
    def __init__(self):
        self.enabled = True
        self.music = None
        self.shoot = None
        self.asteroid_break = None
        self.boss_destroy = None
        self.impact = None
        self.bomb = None
        self.pickup = None
        self.game_over = None
        try:
            if pygame.mixer.get_init() is None:
                pygame.mixer.init(22050, -16, 1, 512)
            self.music = make_music()
            self.music.set_volume(0.45)
            gunshot_file = ASSET_DIR / "gunshot.wav"
            explosion_file = ASSET_DIR / "explosion.wav"
            self.shoot = pygame.mixer.Sound(str(gunshot_file)) if gunshot_file.exists() else make_gunshot()
            boom = pygame.mixer.Sound(str(explosion_file)) if explosion_file.exists() else make_explosion(0.82, 0.78, 48)
            self.asteroid_break = boom
            self.boss_destroy = pygame.mixer.Sound(str(explosion_file)) if explosion_file.exists() else make_explosion(0.82, 0.78, 48)
            self.impact = pygame.mixer.Sound(str(explosion_file)) if explosion_file.exists() else make_explosion(0.82, 0.78, 48)
            self.bomb = pygame.mixer.Sound(str(explosion_file)) if explosion_file.exists() else make_explosion(0.82, 0.78, 48)
            self.shoot.set_volume(0.78)
            self.asteroid_break.set_volume(0.82)
            self.boss_destroy.set_volume(1.0)
            self.impact.set_volume(0.55)
            self.bomb.set_volume(0.95)
            self.pickup = make_pickup_sound()
            self.game_over = make_sweep(440, 55, 0.90, 0.43, 0.12)
            self.start_music()
        except pygame.error:
            # May be unavailable on a computer without an audio device.
            self.enabled = False

    def start_music(self):
        if self.enabled and self.music:
            self.music.play(-1)

    def play(self, sound):
        if self.enabled and sound:
            if isinstance(sound, (list, tuple)):
                sound = random.choice(sound)
            sound.play()

    def toggle(self):
        self.enabled = not self.enabled
        if self.enabled:
            self.start_music()
        else:
            pygame.mixer.stop()


def load_high_score():
    try:
        return int(json.loads(SAVE_FILE.read_text(encoding="utf-8")).get("high_score", 0))
    except (OSError, ValueError, TypeError, json.JSONDecodeError):
        return 0


def save_high_score(score):
    try:
        SAVE_FILE.write_text(json.dumps({"high_score": score}), encoding="utf-8")
    except OSError:
        pass


class Star:
    """Sao nho va sao lap lanh hinh chu thap trong anh tham khao."""
    def __init__(self):
        self.x = random.randrange(WIDTH)
        self.y = random.randrange(HEIGHT)
        self.speed = random.uniform(0.35, 1.1)
        self.size = random.choice((1, 1, 2, 3))
        self.twinkle = random.random() * 6

    def update(self):
        self.y += self.speed
        self.twinkle += 0.045
        if self.y > HEIGHT:
            self.x, self.y = random.randrange(WIDTH), -5

    def draw(self, screen):
        brightness = int(130 + 90 * (0.5 + 0.5 * math.sin(self.twinkle)))
        color = (brightness, brightness - 3, brightness + 8)
        x, y = int(self.x), int(self.y)
        if self.size >= 3:
            pygame.draw.line(screen, color, (x - 7, y), (x + 7, y), 2)
            pygame.draw.line(screen, color, (x, y - 7), (x, y + 7), 2)
        else:
            pygame.draw.circle(screen, color, (x, y), self.size)


class Player:
    def __init__(self):
        self.rect = pygame.Rect(WIDTH // 2 - 25, HEIGHT - 100, 50, 52)
        self.cooldown = 0
        self.invulnerable = 0
        self.triple_shot_time = 0
        self.speed_boost_time = 0
        self.shield_time = 0

    def update(self, keys):
        dx = int(keys[pygame.K_RIGHT] or keys[pygame.K_d]) - int(keys[pygame.K_LEFT] or keys[pygame.K_a])
        dy = int(keys[pygame.K_DOWN] or keys[pygame.K_s]) - int(keys[pygame.K_UP] or keys[pygame.K_w])
        speed = PLAYER_SPEED + (2 if self.speed_boost_time > 0 else 0)
        self.rect.x += dx * speed
        self.rect.y += dy * speed
        self.rect.clamp_ip(pygame.Rect(12, 12, WIDTH - 24, HEIGHT - 24))
        self.cooldown = max(0, self.cooldown - 1)
        self.invulnerable = max(0, self.invulnerable - 1)
        self.triple_shot_time = max(0, self.triple_shot_time - 1)
        self.speed_boost_time = max(0, self.speed_boost_time - 1)
        self.shield_time = max(0, self.shield_time - 1)

    def shoot(self):
        if self.cooldown == 0:
            self.cooldown = 13
            if self.triple_shot_time > 0:
                return [
                    pygame.Rect(self.rect.centerx - 5, self.rect.top - 16, 10, 10),
                    pygame.Rect(self.rect.centerx - 20, self.rect.top - 8, 10, 10),
                    pygame.Rect(self.rect.centerx + 10, self.rect.top - 8, 10, 10),
                ]
            return [pygame.Rect(self.rect.centerx - 5, self.rect.top - 16, 10, 10)]
        return []

    def draw(self, screen):
        if self.invulnerable and (self.invulnerable // 5) % 2 == 0:
            return
        x, y = self.rect.centerx, self.rect.centery
        # Lua tau, canh mau vang va dong co duoc ve bang da giac.
        pygame.draw.polygon(screen, (236, 190, 69), [(self.rect.left, y + 7), (self.rect.left - 7, y + 15), (self.rect.left + 10, y + 20)])
        pygame.draw.polygon(screen, (236, 190, 69), [(self.rect.right, y + 7), (self.rect.right + 7, y + 15), (self.rect.right - 10, y + 20)])
        hull = [(x, self.rect.top), (x - 18, self.rect.bottom - 10), (x - 25, y + 10), (x - 14, y + 4), (x + 14, y + 4), (x + 25, y + 10), (x + 18, self.rect.bottom - 10)]
        pygame.draw.polygon(screen, (247, 241, 231), hull)
        pygame.draw.polygon(screen, (255, 255, 255), hull, 2)
        pygame.draw.polygon(screen, (194, 68, 73), [(x, self.rect.top + 6), (x - 11, y + 12), (x - 6, self.rect.bottom - 12), (x + 6, self.rect.bottom - 12), (x + 11, y + 12)])
        pygame.draw.polygon(screen, (108, 202, 213), [(x, y - 3), (x - 6, y + 9), (x + 6, y + 9)])
        flame_height = random.randint(7, 13)
        pygame.draw.polygon(screen, (238, 112, 75), [(x - 7, self.rect.bottom - 4), (x, self.rect.bottom + flame_height), (x + 7, self.rect.bottom - 4)])
        if self.shield_time > 0:
            pulse = 2 * math.sin(pygame.time.get_ticks() / 130)
            pygame.draw.ellipse(screen, (95, 218, 239), self.rect.inflate(22 + round(pulse), 20 + round(pulse)), 3)
            pygame.draw.ellipse(screen, (190, 248, 255), self.rect.inflate(14, 14), 1)


class Asteroid:
    """Thien thach co ba co, moi co co HP va diem thuong rieng."""
    SIZES = {1: 26, 2: 52, 3: 104}

    def __init__(self, speed, kind=None):
        self.kind = kind or random.choices((1, 2, 3), weights=(5, 3, 1))[0]
        self.size = self.SIZES[self.kind]
        self.max_hp = self.kind
        self.hp = self.max_hp
        self.hp_display_timer = 0
        self.rect = pygame.Rect(random.randint(10, WIDTH - self.size - 10), -self.size, self.size, self.size)
        self.speed = speed
        self.drift = random.uniform(-0.45, 0.45)
        self.angle = 0
        count = random.randint(7, 9)
        self.points = []
        for i in range(count):
            a = 2 * math.pi * i / count
            radius = random.uniform(0.38, 0.50) * self.size
            self.points.append((math.cos(a) * radius, math.sin(a) * radius))
        self.craters = [
            (random.uniform(-0.18, 0.18) * self.size, random.uniform(-0.18, 0.18) * self.size, random.randint(3, 7))
            for _ in range(3)
        ]

    def update(self):
        self.rect.y += self.speed
        self.rect.x += int(round(self.drift))
        # Chi gioi han theo chieu ngang. Khong kep truc doc de vat can roi khoi man hinh.
        if self.rect.left < 0:
            self.rect.left = 0
        elif self.rect.right > WIDTH:
            self.rect.right = WIDTH
        self.hp_display_timer = max(0, self.hp_display_timer - 1)

    def draw(self, screen):
        center = self.rect.center
        points = [(int(center[0] + x), int(center[1] + y)) for x, y in self.points]
        pygame.draw.polygon(screen, (145, 168, 174), points)
        pygame.draw.polygon(screen, (181, 197, 194), points, 2)
        for x, y, radius in self.craters:
            px, py = int(center[0] + x), int(center[1] + y)
            pygame.draw.circle(screen, (165, 185, 184), (px, py), radius + 2)
            pygame.draw.circle(screen, (126, 151, 159), (px - 1, py + 1), radius)
        if self.hp < self.max_hp and self.hp_display_timer > 0:
            bar = pygame.Rect(self.rect.left, self.rect.top - 9, self.rect.width, 5)
            pygame.draw.rect(screen, (66, 48, 57), bar, border_radius=3)
            fill = bar.copy()
            fill.width = round(bar.width * self.hp / self.max_hp)
            pygame.draw.rect(screen, (244, 103, 105), fill, border_radius=3)


class Boss:
    def __init__(self, stage):
        self.stage = stage
        self.max_hp = 50 + (stage - 1) * 15
        self.hp = self.max_hp
        self.rect = pygame.Rect(WIDTH // 2 - 94, 82, 188, 82)
        self.shot_timer = 70
        self.phase = random.random() * math.tau

    def update(self, player):
        self.phase += 0.012 + min(self.stage, 8) * 0.001
        sway = min(190, 125 + self.stage * 9)
        self.rect.centerx = round(WIDTH // 2 + math.sin(self.phase) * sway)
        self.shot_timer -= 1
        if self.shot_timer <= 0:
            self.shot_timer = max(34, 100 - self.stage * 8)
            bomb_chance = min(0.55, 0.08 + self.stage * 0.075)
            if random.random() < bomb_chance:
                return [BossBomb(self.rect.midbottom, player.rect.centery)]
            triple_chance = min(0.82, 0.22 + self.stage * 0.12)
            offsets = (-38, 0, 38) if random.random() < triple_chance else (0,)
            return [
                EnemyOrb((self.rect.centerx + offset, self.rect.bottom - 2),
                         (player.rect.centerx + offset * 2, player.rect.centery), self.stage)
                for offset in offsets
            ]
        return []

    def draw(self, screen):
        x, y = self.rect.centerx, self.rect.centery
        # Wide, angular battlecruiser silhouette with plated wings and glowing core.
        hull = [(x, self.rect.top - 5), (x - 28, y - 26), (x - 59, y - 31),
                (self.rect.left, y - 3), (x - 72, y + 16), (x - 82, self.rect.bottom),
                (x - 37, y + 25), (x, self.rect.bottom - 9), (x + 37, y + 25),
                (x + 82, self.rect.bottom), (x + 72, y + 16), (self.rect.right, y - 3),
                (x + 59, y - 31), (x + 28, y - 26)]
        pygame.draw.polygon(screen, (57, 48, 70), hull)
        pygame.draw.polygon(screen, (222, 199, 216), hull, 3)

        for side in (-1, 1):
            wing = [(x + side * 37, y - 14), (x + side * 78, y - 5),
                    (x + side * 57, y + 17), (x + side * 27, y + 14)]
            pygame.draw.polygon(screen, (120, 87, 112), wing)
            pygame.draw.polygon(screen, (194, 153, 175), wing, 2)
            stripe = [(x + side * 50, y + 5), (x + side * 72, y - 1),
                      (x + side * 59, y + 8), (x + side * 43, y + 11)]
            pygame.draw.polygon(screen, (238, 86, 105), stripe)
            engine_x = x + side * 49
            flame = 7 + round(5 * (0.5 + 0.5 * math.sin(self.phase * 4 + side)))
            pygame.draw.ellipse(screen, (255, 113, 112), (engine_x - 10, y + 22, 20, flame))
            pygame.draw.ellipse(screen, (255, 218, 177), (engine_x - 5, y + 24, 10, max(3, flame - 4)))

        armor = [(x, y - 34), (x - 30, y - 11), (x - 24, y + 21),
                 (x, y + 34), (x + 24, y + 21), (x + 30, y - 11)]
        pygame.draw.polygon(screen, (139, 68, 94), armor)
        pygame.draw.polygon(screen, (245, 175, 193), armor, 2)
        pygame.draw.polygon(screen, (80, 194, 211), [(x, y - 25), (x - 12, y - 5),
                                                    (x, y + 7), (x + 12, y - 5)])
        pygame.draw.polygon(screen, (197, 251, 247), [(x, y - 21), (x - 5, y - 7), (x + 5, y - 7)])
        pulse = 0.5 + 0.5 * math.sin(self.phase * 3)
        core_radius = 18 + round(4 * pulse)
        pygame.draw.circle(screen, (96, 223, 231), (x, y - 7), core_radius, 2)
        pygame.draw.circle(screen, (172, 250, 245), (x, y - 7), 3 + round(2 * pulse))
        pygame.draw.line(screen, (255, 202, 218), (x - 20, y + 15), (x - 7, y + 23), 3)
        pygame.draw.line(screen, (255, 202, 218), (x + 20, y + 15), (x + 7, y + 23), 3)
        bar = pygame.Rect(WIDTH // 2 - 150, 67, 300, 12)
        pygame.draw.rect(screen, (57, 42, 57), bar, border_radius=6)
        fill = bar.copy()
        fill.width = round(bar.width * max(0, self.hp) / self.max_hp)
        pygame.draw.rect(screen, (237, 94, 111), fill, border_radius=6)
        pygame.draw.rect(screen, (239, 220, 231), bar, 2, border_radius=6)


class EnemyOrb:
    """Qua cau nang luong lon cua boss, lon hon dan cua nguoi choi."""
    def __init__(self, start, target, stage):
        self.x, self.y = start
        dx, dy = target[0] - start[0], target[1] - start[1]
        length = max(1, math.hypot(dx, dy))
        speed = 3.0 + min(stage, 8) * 0.22
        self.radius = 26 + min(stage, 8)
        self.vx, self.vy = dx / length * speed, dy / length * speed
        diameter = self.radius * 2
        self.rect = pygame.Rect(0, 0, diameter, diameter)
        self.rect.center = start
        self.phase = random.random() * math.tau

    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rect.center = (round(self.x), round(self.y))
        self.phase += 0.12

    def draw(self, screen):
        pygame.draw.circle(screen, (255, 86, 119), self.rect.center, self.radius)
        pygame.draw.circle(screen, (255, 158, 170), self.rect.center, self.radius - 5, 3)
        pygame.draw.circle(screen, (255, 220, 217), self.rect.center, max(3, self.radius // 3))
        glint = (self.rect.centerx - round(4 * math.cos(self.phase)),
                 self.rect.centery - round(4 * math.sin(self.phase)))
        pygame.draw.circle(screen, WHITE, glint, max(2, self.radius // 7))


class BossBomb:
    BLAST_RADIUS = WIDTH // 4

    def __init__(self, start, target_y):
        self.x, self.y = start
        self.target_y = max(HEIGHT // 3, min(HEIGHT - 85, target_y))
        self.rect = pygame.Rect(0, 0, 32, 32)
        self.rect.center = start
        self.exploded = False
        self.timer = 0
        self.phase = 0

    def update(self, stage):
        self.phase += 0.18
        just_exploded = False
        if not self.exploded:
            self.y += 3.1 + min(stage, 8) * 0.18
            self.rect.center = (round(self.x), round(self.y))
            if self.y >= self.target_y:
                self.exploded = True
                self.timer = 24
                just_exploded = True
        else:
            self.timer -= 1
        return just_exploded

    @property
    def finished(self):
        return self.exploded and self.timer <= 0

    def draw(self, screen):
        if not self.exploded:
            pygame.draw.circle(screen, (255, 121, 72), self.rect.center, 17)
            pygame.draw.circle(screen, (255, 232, 179), self.rect.center, 8)
            pygame.draw.circle(screen, WHITE, (self.rect.centerx - 4, self.rect.centery - 5), 3)
            return
        progress = 1 - self.timer / 24
        radius = max(1, round(self.BLAST_RADIUS * min(1, progress * 1.8)))
        glow = pygame.Surface((self.BLAST_RADIUS * 2, self.BLAST_RADIUS * 2), pygame.SRCALPHA)
        center = (self.BLAST_RADIUS, self.BLAST_RADIUS)
        pygame.draw.circle(glow, (255, 101, 96, 42), center, radius)
        pygame.draw.circle(glow, (255, 189, 116, 170), center, radius, 5)
        pygame.draw.circle(glow, (255, 230, 190, 220), center, max(2, radius // 3), 3)
        screen.blit(glow, (self.rect.centerx - self.BLAST_RADIUS, self.rect.centery - self.BLAST_RADIUS))


class PowerUp:
    LABELS = {"heart": "+1 MẠNG", "triple": "3 TIA", "speed": "TĂNG TỐC", "shield": "KHIÊN"}

    def __init__(self, x, y, kind=None):
        self.kind = kind or random.choice(("heart", "triple", "speed", "shield"))
        self.rect = pygame.Rect(x - 16, y - 16, 32, 32)
        self.phase = random.random() * 6

    def update(self):
        self.rect.y += 2
        self.phase += 0.08
        self.rect.x += int(round(math.sin(self.phase) * 1.2))

    def draw(self, screen, font):
        color = {"heart": (236, 79, 102), "triple": (239, 191, 98), "speed": (105, 205, 218), "shield": (105, 155, 235)}[self.kind]
        pygame.draw.circle(screen, (245, 235, 239), self.rect.center, 18)
        pygame.draw.circle(screen, color, self.rect.center, 15)
        x, y = self.rect.center
        if self.kind == "heart":
            pygame.draw.circle(screen, WHITE, (x - 4, y - 3), 5)
            pygame.draw.circle(screen, WHITE, (x + 4, y - 3), 5)
            pygame.draw.polygon(screen, WHITE, [(x - 9, y - 2), (x + 9, y - 2), (x, y + 10)])
        elif self.kind == "triple":
            for offset in (-7, 0, 7):
                pygame.draw.ellipse(screen, (255, 251, 226), (x + offset - 2, y - 8, 4, 14))
                pygame.draw.circle(screen, WHITE, (x + offset, y - 8), 2)
        elif self.kind == "speed":
            for offset in (-7, 0, 7):
                pygame.draw.polygon(screen, WHITE, [(x - 4, y + offset + 2), (x, y + offset - 2),
                                                   (x + 4, y + offset + 2), (x + 2, y + offset + 2),
                                                   (x + 2, y + offset + 5), (x - 2, y + offset + 5),
                                                   (x - 2, y + offset + 2)])
        else:
            shield = [(x, y - 10), (x + 9, y - 6), (x + 7, y + 4), (x, y + 10),
                      (x - 7, y + 4), (x - 9, y - 6)]
            pygame.draw.polygon(screen, WHITE, shield)
            pygame.draw.polygon(screen, (105, 155, 235), [(x, y - 6), (x + 5, y - 4),
                                                          (x + 4, y + 3), (x, y + 7),
                                                          (x - 4, y + 3), (x - 5, y - 4)])


def apply_power_up(player, kind, lives):
    if kind == "heart":
        return lives + 1
    if kind == "triple":
        player.triple_shot_time = 10 * FPS
    elif kind == "speed":
        player.speed_boost_time = 10 * FPS
    elif kind == "shield":
        player.shield_time = 10 * FPS
    return lives


class Particle:
    def __init__(self, position):
        self.x, self.y = position
        angle = random.random() * math.tau
        speed = random.uniform(1.2, 4.2)
        self.dx, self.dy = math.cos(angle) * speed, math.sin(angle) * speed
        self.life = random.randint(18, 32)

    def update(self):
        self.x += self.dx
        self.y += self.dy
        self.life -= 1

    def draw(self, screen):
        if self.life > 0:
            pygame.draw.circle(screen, (255, 190, 120), (int(self.x), int(self.y)), max(1, self.life // 8))


class Button:
    def __init__(self, text, center, width=250, height=52):
        self.text = text
        self.rect = pygame.Rect(0, 0, width, height)
        self.rect.center = center

    def draw(self, screen, font):
        hovered = self.rect.collidepoint(pygame.mouse.get_pos())
        fill = (174, 85, 91) if hovered else (143, 72, 83)
        pygame.draw.rect(screen, (220, 192, 195), self.rect, border_radius=13)
        inner = self.rect.inflate(-4, -4)
        pygame.draw.rect(screen, fill, inner, border_radius=11)
        label = font.render(self.text, True, WHITE)
        screen.blit(label, label.get_rect(center=self.rect.center))


def draw_text(screen, font, text, center, color=WHITE):
    image = font.render(text, True, color)
    screen.blit(image, image.get_rect(center=center))


def draw_panel(screen, rect, color=(54, 45, 60, 218)):
    panel = pygame.Surface(rect.size, pygame.SRCALPHA)
    pygame.draw.rect(panel, color, panel.get_rect(), border_radius=20)
    pygame.draw.rect(panel, (208, 194, 207, 235), panel.get_rect(), width=2, border_radius=20)
    screen.blit(panel, rect.topleft)


def new_game():
    return Player(), [], [], [], [], [], [], 0, STARTING_LIVES, 0


def main():
    pygame.init()
    pygame.display.set_caption("Tau Vu Tru - Bao Ve Ngan Ha")
    screen = pygame.display.set_mode((WIDTH, HEIGHT))
    clock = pygame.time.Clock()
    title_font = get_game_font(48, bold=True)
    font = get_game_font(25)
    button_font = get_game_font(23, bold=True)
    small_font = get_game_font(18)
    sounds = SoundEffects()
    stars = [Star() for _ in range(95)]
    high_score = load_high_score()
    state = "menu"
    player, bullets, asteroids, particles, lasers, bombs, powerups, score, lives, spawn_timer = new_game()
    boss = None
    boss_stage = 0
    difficulty_level = 0
    next_boss_score = 100
    buttons = []
    running = True

    def start_game():
        nonlocal player, bullets, asteroids, particles, lasers, bombs, powerups, score, lives, spawn_timer
        nonlocal boss, boss_stage, difficulty_level, next_boss_score, state
        player, bullets, asteroids, particles, lasers, bombs, powerups, score, lives, spawn_timer = new_game()
        boss = None
        boss_stage = 0
        difficulty_level = 0
        next_boss_score = 100
        state = "playing"

    def record_score():
        nonlocal high_score
        if score > high_score:
            high_score = score
            save_high_score(high_score)

    def destroy_asteroid(asteroid):
        nonlocal score
        if asteroid in asteroids:
            asteroids.remove(asteroid)
            score += asteroid.kind
            record_score()
            particles.extend(Particle(asteroid.rect.center) for _ in range(14 + asteroid.kind * 3))
            sounds.play(sounds.asteroid_break)
            drop_chance = min(0.72, 0.14 + difficulty_level * 0.07)
            if random.random() < drop_chance:
                powerups.append(PowerUp(*asteroid.rect.center))

    def damage_asteroid(asteroid, damage=1):
        asteroid.hp -= damage
        asteroid.hp_display_timer = 90
        if asteroid.hp <= 0:
            destroy_asteroid(asteroid)

    while running:
        clock.tick(FPS)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    if state == "playing":
                        state = "paused"
                    elif state == "paused":
                        state = "playing"
                    elif state == "instructions":
                        state = "menu"
                    else:
                        running = False
                elif event.key in (pygame.K_RETURN, pygame.K_SPACE):
                    if state in ("menu", "game_over"):
                        start_game()
                    elif state == "paused":
                        state = "playing"
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                for button in buttons:
                    if button.rect.collidepoint(event.pos):
                        if button.text in ("BẮT ĐẦU", "CHƠI LẠI"):
                            start_game()
                        elif button.text == "HƯỚNG DẪN":
                            state = "instructions"
                        elif button.text == "CHƠI TIẾP":
                            state = "playing"
                        elif button.text == "VỀ MENU":
                            state = "menu"
                        elif button.text == "QUAY LẠI":
                            state = "menu"
                        elif button.text == "THOÁT":
                            running = False
                        elif button.text.startswith("ÂM THANH"):
                            sounds.toggle()

        for star in stars:
            star.update()
        keys = pygame.key.get_pressed()

        if state == "playing":
            player.update(keys)
            mouse_pos = pygame.mouse.get_pos()
            mouse_fire = pygame.mouse.get_pressed()[0] and not any(
                button.rect.collidepoint(mouse_pos) for button in buttons
            )
            if keys[pygame.K_SPACE] or mouse_fire:
                shots = player.shoot()
                if shots:
                    bullets.extend(shots)
                    sounds.play(sounds.shoot)

            if boss is None and score >= next_boss_score:
                boss_stage += 1
                boss = Boss(boss_stage)
                next_boss_score += 100

            spawn_timer += 1
            if spawn_timer >= max(16, 58 - score // 80 - difficulty_level * 4):
                spawn_timer = 0
                asteroid_speed = 2 + min(score / 250, 3) + min(difficulty_level * 0.4, 3.2)
                asteroids.append(Asteroid(asteroid_speed))

            for bullet in bullets[:]:
                bullet.y -= BULLET_SPEED
                if bullet.bottom < 0:
                    bullets.remove(bullet)
            for asteroid in asteroids[:]:
                asteroid.update()
                if asteroid.rect.top >= HEIGHT:
                    asteroids.remove(asteroid)
                elif player.rect.colliderect(asteroid.rect) and (player.invulnerable == 0 or player.shield_time > 0):
                    if player.shield_time > 0:
                        destroy_asteroid(asteroid)
                    else:
                        asteroids.remove(asteroid)
                        lives -= 1
                        player.invulnerable = 75
                        particles.extend(Particle(asteroid.rect.center) for _ in range(12))
                        sounds.play(sounds.impact)

            for asteroid in asteroids[:]:
                hit = next((bullet for bullet in bullets if asteroid.rect.colliderect(bullet)), None)
                if hit:
                    bullets.remove(hit)
                    damage_asteroid(asteroid)

            if boss is not None:
                for attack in boss.update(player):
                    if isinstance(attack, BossBomb):
                        bombs.append(attack)
                    else:
                        lasers.append(attack)
                for bullet in bullets[:]:
                    if boss.rect.colliderect(bullet):
                        bullets.remove(bullet)
                        boss.hp -= 1
                        if boss.hp <= 0:
                            boss_center = boss.rect.center
                            defeated_stage = boss.stage
                            boss = None
                            difficulty_level += 1
                            score += 10 * defeated_stage
                            record_score()
                            particles.extend(Particle(boss_center) for _ in range(45))
                            sounds.play(sounds.boss_destroy)
                            # Boss cang cao cho nhieu co hoi nhan vat pham hon.
                            drop_chance = min(0.99, 0.78 + defeated_stage * 0.06)
                            if random.random() < drop_chance:
                                powerups.append(PowerUp(*boss_center))
                                if defeated_stage >= 2 and random.random() < min(0.82, 0.2 + defeated_stage * 0.11):
                                    powerups.append(PowerUp(boss_center[0] + 36, boss_center[1]))
                            break

            for orb in lasers[:]:
                orb.update()
                if (orb.rect.top > HEIGHT or orb.rect.bottom < 0 or
                        orb.rect.right < 0 or orb.rect.left > WIDTH):
                    lasers.remove(orb)
                elif orb.rect.colliderect(player.rect):
                    lasers.remove(orb)
                    if player.shield_time == 0 and player.invulnerable == 0:
                        lives -= 1
                        player.invulnerable = 90
                        sounds.play(sounds.impact)

            for bomb in bombs[:]:
                if bomb.update(boss_stage):
                    blast_x, blast_y = bomb.rect.center
                    for asteroid in asteroids[:]:
                        distance = math.hypot(asteroid.rect.centerx - blast_x, asteroid.rect.centery - blast_y)
                        if distance <= bomb.BLAST_RADIUS:
                            damage_asteroid(asteroid, 2)
                    player_distance = math.hypot(player.rect.centerx - blast_x, player.rect.centery - blast_y)
                    if (player_distance <= bomb.BLAST_RADIUS and player.shield_time == 0
                            and player.invulnerable == 0):
                        lives -= 1
                        player.invulnerable = 90
                    sounds.play(sounds.bomb)
                if bomb.finished:
                    bombs.remove(bomb)

            for powerup in powerups[:]:
                powerup.update()
                if powerup.rect.top > HEIGHT:
                    powerups.remove(powerup)
                elif player.rect.colliderect(powerup.rect):
                    lives = apply_power_up(player, powerup.kind, lives)
                    powerups.remove(powerup)
                    sounds.play(sounds.pickup)

            if lives <= 0:
                state = "game_over"
                sounds.play(sounds.game_over)
                if score > high_score:
                    high_score = score
                    save_high_score(high_score)

        for particle in particles[:]:
            particle.update()
            if particle.life <= 0:
                particles.remove(particle)

        # Nen va sao lap lanh.
        screen.fill(BACKGROUND)
        for star in stars:
            star.draw(screen)
        for particle in particles:
            particle.draw(screen)

        buttons = []
        if state == "playing":
            for bullet in bullets:
                pygame.draw.circle(screen, (244, 91, 112), bullet.center, 8)
                pygame.draw.circle(screen, (255, 177, 164), bullet.center, 5)
                pygame.draw.circle(screen, (255, 250, 226), bullet.center, 2)
            for asteroid in asteroids:
                asteroid.draw(screen)
            for powerup in powerups:
                powerup.draw(screen, button_font)
            for laser in lasers:
                laser.draw(screen)
            for bomb in bombs:
                bomb.draw(screen)
            if boss is not None:
                boss.draw(screen)
            player.draw(screen)

            # Bang diem va trang thai gon nhe tren cung.
            pygame.draw.rect(screen, (54, 45, 60), (WIDTH // 2 - 48, 16, 96, 46), border_radius=10)
            pygame.draw.rect(screen, (239, 226, 235), (WIDTH // 2 - 48, 16, 96, 46), 2, border_radius=10)
            draw_text(screen, button_font, str(score), (WIDTH // 2, 39))
            draw_text(screen, small_font, f"MẠNG: {lives}", (85, 38))
            draw_text(screen, small_font, f"KỶ LỤC: {high_score}", (WIDTH - 100, 38))
            if boss is not None:
                draw_text(screen, small_font, f"TRÙM {boss.stage}  |  HP: {boss.hp}/{boss.max_hp}", (WIDTH // 2, 178), (255, 216, 222))
            effects = []
            if player.triple_shot_time:
                effects.append(f"BA TIA {math.ceil(player.triple_shot_time / FPS)}s")
            if player.speed_boost_time:
                effects.append(f"TĂNG TỐC {math.ceil(player.speed_boost_time / FPS)}s")
            if player.shield_time:
                effects.append(f"KHIÊN {math.ceil(player.shield_time / FPS)}s")
            if effects:
                draw_text(screen, small_font, "   •   ".join(effects), (WIDTH // 2, HEIGHT - 26), (247, 221, 145))
            buttons.append(Button("ÂM THANH: " + ("BẬT" if sounds.enabled else "TẮT"), (WIDTH - 96, HEIGHT - 30), 170, 38))
            draw_text(screen, small_font, "ESC: TẠM DỪNG", (95, HEIGHT - 30), (225, 215, 225))

        if state == "menu":
            draw_panel(screen, pygame.Rect(WIDTH // 2 - 235, 76, 470, 410))
            draw_text(screen, title_font, "TÀU VŨ TRỤ", (WIDTH // 2, 137), (243, 218, 221))
            draw_text(screen, font, "BẢO VỆ NGÂN HÀ", (WIDTH // 2, 190), (190, 215, 218))
            buttons = [Button("BẮT ĐẦU", (WIDTH // 2, 270)), Button("HƯỚNG DẪN", (WIDTH // 2, 335)), Button("THOÁT", (WIDTH // 2, 400))]
            for button in buttons:
                button.draw(screen, button_font)
            draw_text(screen, small_font, f"Kỷ lục: {high_score}", (WIDTH // 2, 455), (220, 210, 221))
            draw_text(screen, small_font, "Âm thanh được tạo trực tiếp trong game", (WIDTH // 2, 510), (220, 210, 221))
        elif state == "instructions":
            draw_panel(screen, pygame.Rect(WIDTH // 2 - 280, 105, 560, 330))
            draw_text(screen, title_font, "HƯỚNG DẪN", (WIDTH // 2, 160), (243, 218, 221))
            draw_text(screen, font, "Di chuyển: WASD hoặc phím mũi tên", (WIDTH // 2, 230))
            draw_text(screen, font, "Bắn: giữ chuột trái hoặc phím CÁCH", (WIDTH // 2, 275))
            draw_text(screen, font, "Vật cản cỡ nhỏ, vừa, lớn cần 1, 2, 3 phát bắn", (WIDTH // 2, 320))
            draw_text(screen, font, "Nhặt tim, ba tia, tăng tốc hoặc khiên 10 giây", (WIDTH // 2, 360))
            draw_text(screen, font, "Cứ mỗi 100 điểm, một Trùm sẽ xuất hiện", (WIDTH // 2, 400))
            draw_text(screen, small_font, "Nhấn ESC hoặc QUAY LẠI để trở về", (WIDTH // 2, 420), (220, 210, 221))
            buttons = [Button("QUAY LẠI", (WIDTH // 2, 470))]
        elif state == "paused":
            draw_panel(screen, pygame.Rect(WIDTH // 2 - 230, 115, 460, 330))
            draw_text(screen, title_font, "TẠM DỪNG", (WIDTH // 2, 165), (243, 218, 221))
            buttons = [Button("CHƠI TIẾP", (WIDTH // 2, 250)), Button("CHƠI LẠI", (WIDTH // 2, 315)), Button("VỀ MENU", (WIDTH // 2, 380))]
            for button in buttons:
                button.draw(screen, button_font)
        elif state == "game_over":
            draw_panel(screen, pygame.Rect(WIDTH // 2 - 250, 95, 500, 350))
            draw_text(screen, title_font, "BẠN ĐÃ THUA", (WIDTH // 2, 155), (243, 176, 182))
            draw_text(screen, font, f"Điểm của bạn: {score}", (WIDTH // 2, 220))
            draw_text(screen, font, f"Kỷ lục: {high_score}", (WIDTH // 2, 260), (240, 215, 152))
            buttons = [Button("CHƠI LẠI", (WIDTH // 2, 330)), Button("VỀ MENU", (WIDTH // 2, 395))]
            for button in buttons:
                button.draw(screen, button_font)

        # Nut am thanh hien tren cac man hinh menu.
        if state in ("menu", "instructions", "paused", "game_over"):
            sound_button = Button("ÂM THANH: " + ("BẬT" if sounds.enabled else "TẮT"), (WIDTH - 105, 32), 190, 38)
            sound_button.draw(screen, small_font)
            buttons.append(sound_button)

        if state == "playing":
            sound_button = buttons[-1]
            sound_button.draw(screen, small_font)

        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
