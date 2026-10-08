#!/usr/bin/env python3
"""Villiaumite Vector — neon light-cycle arcade for ElbowOS. Python 3 + pygame.

Steer a vermillion cycle. Trails are walls. Grab amber shards. Rivals weave chartreuse
and azure. Arrows / WASD turn. R restarts. --play for a window, default records a reel.
"""
import os, sys, math, random, subprocess

PLAY = "--play" in sys.argv and "--record" not in sys.argv
os.environ.setdefault("SDL_AUDIODRIVER", "dummy")
if not PLAY:
    os.environ.setdefault("SDL_VIDEODRIVER", "dummy")

import pygame

W, H, FPS, SECS = 1080, 1920, 30, 15
OUT = os.environ.get("ELBOWOS_MP4", "/workspace/artifacts/VILLIAUMITE_VECTOR_ElbowOS.mp4")
TITLE, HANDLE = "VILLIAUMITE VECTOR", "x.com/ElbowOS"
CELL, COLS, ROWS = 34, 28, 44
OX, OY = (W - COLS * CELL) // 2, 250
INK = (12, 4, 8)
LANE = (58, 22, 28)
GOLD = (255, 176, 64)
CREAM = (255, 236, 210)
VERM = (255, 54, 36)
LIME = (190, 255, 60)
AZUR = (70, 210, 255)
AMBER = (255, 196, 48)


def cell_free(occ, x, y):
    return 0 <= x < COLS and 0 <= y < ROWS and (x, y) not in occ


class Bike:
    def __init__(self, x, y, dx, dy, color, core, tag):
        self.x, self.y = float(x), float(y)
        self.dx, self.dy = dx, dy
        self.color, self.core, self.tag = color, core, tag
        self.alive = True
        self.trail = {(x, y)}
        self.flash = 0
        self.score_tag = 0

    def head(self):
        return int(self.x), int(self.y)

    def steer(self, occ, rnd):
        if not self.alive:
            return
        hx, hy = self.head()
        options = []
        for ndx, ndy in ((self.dx, self.dy), (-self.dy, self.dx), (self.dy, -self.dx)):
            clear = 0
            xx, yy = hx, hy
            for _ in range(7):
                xx += ndx
                yy += ndy
                if not cell_free(occ, xx, yy):
                    break
                clear += 1
            options.append((clear + rnd.random() * 0.3, ndx, ndy))
        options.sort(reverse=True)
        self.dx, self.dy = options[0][1], options[0][2]

    def step(self, occ, speed):
        if not self.alive:
            return False
        self.x += self.dx * speed
        self.y += self.dy * speed
        hx, hy = self.head()
        if not cell_free(occ, hx, hy):
            self.alive = False
            self.flash = 12
            return True
        if (hx, hy) not in self.trail:
            self.trail.add((hx, hy))
            occ.add((hx, hy))
        return False


class Game:
    def __init__(self, seed=7):
        pygame.init()
        pygame.font.init()
        flags = 0 if PLAY else pygame.HIDDEN
        try:
            self.screen = pygame.display.set_mode((W, H), flags)
        except pygame.error:
            os.environ["SDL_VIDEODRIVER"] = "dummy"
            pygame.display.quit()
            pygame.display.init()
            self.screen = pygame.display.set_mode((W, H), pygame.HIDDEN)
        pygame.display.set_caption(TITLE)
        self.font = pygame.font.Font(None, 86)
        self.mid = pygame.font.Font(None, 52)
        self.small = pygame.font.Font(None, 40)
        self.rnd = random.Random(seed)
        self.reset()

    def reset(self):
        self.t = 0
        self.score = 0
        self.combo = 0
        self.occ = set()
        self.shards = []
        self.bursts = []
        self.player = Bike(6, ROWS - 6, 0, -1, VERM, CREAM, "YOU")
        self.rivals = [
            Bike(COLS - 7, 8, 0, 1, LIME, (230, 255, 180), "LIME"),
            Bike(COLS // 2, 10, 1, 0, AZUR, (210, 250, 255), "AZUR"),
        ]
        for b in (self.player, *self.rivals):
            self.occ |= set(b.trail)
        self.spawn_shards(8)

    def spawn_shards(self, n):
        for _ in range(n):
            for _try in range(40):
                x, y = self.rnd.randrange(1, COLS - 1), self.rnd.randrange(2, ROWS - 2)
                if cell_free(self.occ, x, y) and (x, y) not in self.shards:
                    self.shards.append((x, y))
                    break

    def respawn(self, bike, color, core, tag):
        for _ in range(50):
            x, y = self.rnd.randrange(2, COLS - 2), self.rnd.randrange(2, ROWS - 2)
            if cell_free(self.occ, x, y):
                d = self.rnd.choice(((1, 0), (-1, 0), (0, 1), (0, -1)))
                nb = Bike(x, y, d[0], d[1], color, core, tag)
                self.occ.add((x, y))
                return nb
        return bike

    def update(self, keys=None, auto=False):
        self.t += 1
        if keys and self.player.alive:
            if keys[pygame.K_LEFT] or keys[pygame.K_a]:
                self.player.dx, self.player.dy = -1, 0
            elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
                self.player.dx, self.player.dy = 1, 0
            elif keys[pygame.K_UP] or keys[pygame.K_w]:
                self.player.dx, self.player.dy = 0, -1
            elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
                self.player.dx, self.player.dy = 0, 1
        if auto or not PLAY:
            if self.t % 4 == 0 and self.player.alive:
                self.player.steer(self.occ, self.rnd)
        if self.t % 5 == 0:
            for rv in self.rivals:
                if rv.alive:
                    rv.steer(self.occ, self.rnd)
        crashed = self.player.step(self.occ, 0.34)
        if crashed:
            self.bursts.append([self.player.x, self.player.y, 18, VERM])
            self.combo = 0
            self.player = self.respawn(self.player, VERM, CREAM, "YOU")
        for i, rv in enumerate(self.rivals):
            if rv.step(self.occ, 0.28):
                self.bursts.append([rv.x, rv.y, 16, rv.color])
                self.score += 40
                spec = (LIME, (230, 255, 180), "LIME") if i == 0 else (AZUR, (210, 250, 255), "AZUR")
                self.rivals[i] = self.respawn(rv, *spec)
        hx, hy = self.player.head()
        if (hx, hy) in self.shards:
            self.shards.remove((hx, hy))
            self.score += 25 + self.combo * 5
            self.combo = min(self.combo + 1, 12)
            self.bursts.append([hx + 0.5, hy + 0.5, 10, AMBER])
            self.spawn_shards(1)
        elif self.t % 18 == 0 and self.player.alive:
            self.score += 1
        if len(self.shards) < 6 and self.t % 20 == 0:
            self.spawn_shards(1)
        self.bursts = [b for b in self.bursts if b[2] > 0]
        for b in self.bursts:
            b[2] -= 1

    def draw(self, surf):
        surf.fill(INK)
        for i in range(8):
            pygame.draw.circle(surf, (40 + i * 4, 10, 16), (W // 2, 980), 820 - i * 70, 8)
        pygame.draw.rect(surf, (28, 10, 14), (OX - 16, OY - 16, COLS * CELL + 32, ROWS * CELL + 32), border_radius=18)
        for c in range(COLS + 1):
            pygame.draw.line(surf, LANE, (OX + c * CELL, OY), (OX + c * CELL, OY + ROWS * CELL), 1)
        for r in range(ROWS + 1):
            pygame.draw.line(surf, LANE, (OX, OY + r * CELL), (OX + COLS * CELL, OY + r * CELL), 1)
        for bike in (*self.rivals, self.player):
            for (cx, cy) in bike.trail:
                rect = pygame.Rect(OX + cx * CELL + 4, OY + cy * CELL + 4, CELL - 8, CELL - 8)
                pygame.draw.rect(surf, bike.color, rect.inflate(6, 6), border_radius=6)
                pygame.draw.rect(surf, bike.core, rect, border_radius=5)
            if bike.alive:
                px = OX + bike.x * CELL + CELL / 2
                py = OY + bike.y * CELL + CELL / 2
                ang = math.atan2(bike.dy, bike.dx)
                nose = (px + math.cos(ang) * 18, py + math.sin(ang) * 18)
                pygame.draw.circle(surf, bike.color, (int(px), int(py)), 16)
                pygame.draw.circle(surf, bike.core, nose, 7)
        pulse = 0.55 + 0.45 * math.sin(self.t * 0.3)
        for sx, sy in self.shards:
            cx = OX + sx * CELL + CELL // 2
            cy = OY + sy * CELL + CELL // 2
            r = int(8 + 4 * pulse)
            pts = [(cx, cy - r), (cx + r, cy), (cx, cy + r), (cx - r, cy)]
            pygame.draw.polygon(surf, AMBER, pts)
            pygame.draw.polygon(surf, CREAM, pts, 2)
        for bx, by, life, col in self.bursts:
            rad = (20 - life) * 4
            pygame.draw.circle(surf, col, (int(OX + bx * CELL), int(OY + by * CELL)), rad, 3)
        banner = pygame.Surface((W, 210), pygame.SRCALPHA)
        banner.fill((18, 6, 10, 220))
        surf.blit(banner, (0, 0))
        title = self.font.render(TITLE, True, GOLD)
        surf.blit(title, title.get_rect(center=(W // 2, 78)))
        score = self.mid.render(f"SCORE  {self.score:04d}    COMBO x{self.combo}", True, CREAM)
        surf.blit(score, score.get_rect(center=(W // 2, 148)))
        foot = pygame.Surface((W, 110), pygame.SRCALPHA)
        foot.fill((18, 6, 10, 210))
        surf.blit(foot, (0, H - 110))
        handle = self.mid.render(HANDLE, True, GOLD)
        surf.blit(handle, handle.get_rect(center=(W // 2, H - 64)))

    def play_interactive(self):
        clock = pygame.time.Clock()
        running = True
        while running:
            keys = pygame.key.get_pressed()
            for ev in pygame.event.get():
                if ev.type == pygame.QUIT or (ev.type == pygame.KEYDOWN and ev.key == pygame.K_ESCAPE):
                    running = False
                if ev.type == pygame.KEYDOWN and ev.key == pygame.K_r:
                    self.reset()
            self.update(keys, auto=False)
            self.draw(self.screen)
            pygame.display.flip()
            clock.tick(FPS)
        pygame.quit()

    def record(self):
        os.makedirs(os.path.dirname(OUT) or ".", exist_ok=True)
        cmd = [
            "ffmpeg", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}",
            "-r", str(FPS), "-i", "-", "-an", "-c:v", "libx264", "-pix_fmt", "yuv420p",
            "-crf", "20", "-movflags", "+faststart", OUT,
        ]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE, stderr=subprocess.PIPE)
        frames = FPS * SECS
        try:
            for _ in range(frames):
                self.update(auto=True)
                self.draw(self.screen)
                raw = pygame.image.tobytes(self.screen, "RGB")
                if len(raw) != W * H * 3:
                    raise RuntimeError(f"bad frame size {len(raw)}")
                proc.stdin.write(raw)
        finally:
            if proc.stdin:
                proc.stdin.close()
        err = proc.stderr.read().decode("utf-8", "ignore") if proc.stderr else ""
        rc = proc.wait()
        if rc != 0 or not os.path.isfile(OUT) or os.path.getsize(OUT) < 10000:
            raise SystemExit(f"ffmpeg failed ({rc}):\n{err[-1500:]}")
        print("wrote", OUT, os.path.getsize(OUT))
        pygame.quit()


def main():
    g = Game()
    if PLAY:
        g.play_interactive()
    else:
        g.record()


if __name__ == "__main__":
    main()
