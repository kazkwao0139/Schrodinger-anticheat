"""
Schrodinger Anti-Cheat Interactive Demo
=======================================

직접 마우스를 움직여 에임핵 탐지를 체험하는 데모.
정상 플레이와 에임핵 시뮬레이션의 탐지 차이를 실시간으로 확인할 수 있다.

조작:
    TAB     정상 / 에임핵 모드 전환
    SPACE   타겟 챌린지 시작 / 중지
    1~3     에임핵 타입 (Silent / Aimlock / Snap)
    T/5     트리거봇 토글
    R       초기화
    ESC     종료

실행:
    pip install pygame
    python schrodinger_demo.py

배포 시:
    schrodinger_core.py를 Cython으로 컴파일하여 .pyd로 변환 후,
    .py 원본 대신 .pyd만 동봉한다. 탐지 로직이 바이너리에 숨겨진다.
"""

import pygame
import sys
import math
import random
import csv
import os
from datetime import datetime

try:
    from schrodinger_core import SchrodingerCore
except ImportError:
    print("[ERROR] schrodinger_core module not found.")
    print("  Place schrodinger_core.pyd (or .py) in the same directory.")
    sys.exit(1)


# ─── Window ───────────────────────────────────────────────
import ctypes
ctypes.windll.user32.SetProcessDPIAware()
pygame.init()

# Resolution override: python schrodinger_demo.py 1920 1080
_info = pygame.display.Info()
if len(sys.argv) >= 3:
    W, H = int(sys.argv[1]), int(sys.argv[2])
    _WINDOWED = True
else:
    W, H = _info.current_w, _info.current_h
    _WINDOWED = False
PANEL = int(340 * (H / 700))
CANVAS = W - PANEL


# ─── Colors ───────────────────────────────────────────────
C_BG     = (10, 10, 15)
C_PANEL  = (22, 27, 34)
C_BORDER = (48, 54, 61)
C_TEXT   = (230, 237, 243)
C_DIM    = (139, 148, 158)
C_CYAN   = (0, 212, 255)
C_RED    = (248, 81, 73)
C_GREEN  = (63, 185, 80)
C_YELLOW = (255, 215, 0)
C_ORANGE = (255, 140, 0)

AIM_TYPES = {
    'silent':  'SILENT AIM',
    'aimlock': 'AIMLOCK (Rage)',
    'snap':    'SNAP (50-150ms)',
}


# ─── Demo ─────────────────────────────────────────────────
class Demo:
    def __init__(self):
        pygame.init()
        flags = 0 if _WINDOWED else pygame.NOFRAME
        self.screen = pygame.display.set_mode((W, H), flags)
        pygame.display.set_caption("Schrodinger Anti-Cheat Test")
        self.clock = pygame.time.Clock()
        pygame.mouse.set_cursor(pygame.SYSTEM_CURSOR_CROSSHAIR)

        fn = 'malgungothic'
        sc = H / 700  # scale factor based on reference 700p height
        self.f_title  = pygame.font.SysFont(fn, int(20 * sc), bold=True)
        self.f_big    = pygame.font.SysFont(fn, int(36 * sc), bold=True)
        self.f_mid    = pygame.font.SysFont(fn, int(14 * sc))
        self.f_small  = pygame.font.SysFont(fn, int(11 * sc))
        self.f_hint   = pygame.font.SysFont(fn, int(20 * sc))
        self.ui_scale = sc

        # Tick rate config
        self.tickrate = 60
        self.feed_interval = 1000 // self.tickrate  # ms between feeds

        self.core = SchrodingerCore()
        self.core._MS = int(self.core._MS * sc)  # scale speed filter to resolution
        self.core._B = int(300 * (self.tickrate / 60))  # scale buffer to tick rate

        # State
        self.mode = 'normal'
        self.aim_type = 'silent'

        # Trail
        self.trail = []

        # Challenge
        self.ch_active = False
        self.ch_target = None
        self.ch_total = 0
        self.ch_max = 20
        self.ch_timer = 0.0
        self.ch_timeout = 3.0
        self.spawn_delay = 0.0

        # Aimbot
        self.vpos = [float(CANVAS // 2), float(H // 2)]
        self.locked = False     # aimlock: locked on target
        self.snapping = False
        self.snap_from = [0.0, 0.0]
        self.snap_to = [0.0, 0.0]
        self.snap_t = 0.0
        self.snap_dur = 0.05

        # Aimbot FOV
        self.aim_fov = 100           # aimbot activation radius (px)

        # Trigger bot (separate: auto-click when cursor is ON target)
        self.trig_on = False         # trigger bot enabled
        self.trig_delay = 0.0       # countdown to auto-fire
        self.trig_armed = False      # waiting to fire

        # Visual effects
        self.hits = []
        self.last_feed = 0
        self.data_count = 0
        self.flash_timer = 0.0       # red flash on anomaly
        self.last_result = None      # debug: latest DetectionResult
        self.last_intent = None      # intent score from last hit
        self.last_cursor_dist = None # cursor-target distance at last hit

        # UI: aim type button rects (filled in _draw_panel)
        self.aim_btn_rects = {}

        # Log file
        log_dir = os.path.join(os.path.dirname(__file__), 'logs')
        os.makedirs(log_dir, exist_ok=True)
        ts = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_path = os.path.join(log_dir, f'detection_{ts}.csv')
        self._log_file = open(self.log_path, 'w', newline='', encoding='utf-8')
        self._log_writer = csv.writer(self._log_file)
        self._log_writer.writerow([
            'time_ms', 'x', 'y', 'mode', 'aim_type',
            'is_anomaly', 'anomaly_count',
        ])

        # Result
        self.show_result = False
        self.result_data = {}

    # ─── Main Loop ────────────────────────────────────────

    def run(self):
        while True:
            dt = self.clock.tick(self.tickrate) / 1000.0
            self._events()
            self._update(dt)
            self._draw()

    # ─── Events ───────────────────────────────────────────

    def _events(self):
        for ev in pygame.event.get():
            if ev.type == pygame.QUIT:
                self._log_file.close()
                pygame.quit()
                sys.exit()

            elif ev.type == pygame.KEYDOWN:
                if self.show_result:
                    self.show_result = False
                    continue

                if ev.key == pygame.K_ESCAPE:
                    self._log_file.close()
                    pygame.quit()
                    sys.exit()
                elif ev.key == pygame.K_TAB:
                    self.mode = 'aimbot' if self.mode == 'normal' else 'normal'
                    print(f"[MODE] → {self.mode.upper()}  aim_type={self.aim_type}")
                    self._full_reset()
                elif ev.key == pygame.K_SPACE:
                    if self.ch_active:
                        self._end_challenge()
                    else:
                        self._start_challenge()
                elif ev.key == pygame.K_r:
                    self._full_reset()
                elif ev.key == pygame.K_1:
                    self.aim_type = 'silent'
                elif ev.key == pygame.K_2:
                    self.aim_type = 'aimlock'
                elif ev.key == pygame.K_3:
                    self.aim_type = 'snap'
                elif ev.key in (pygame.K_5, pygame.K_t):
                    self.trig_on = not self.trig_on
                elif ev.key == pygame.K_F1:
                    self._set_tickrate(max(20, self.tickrate - 10))
                elif ev.key == pygame.K_F2:
                    self._set_tickrate(min(240, self.tickrate + 10))

            elif ev.type == pygame.MOUSEWHEEL:
                if self.mode == 'aimbot':
                    self.aim_fov = max(5, min(300, self.aim_fov + ev.y * 5))

            elif ev.type == pygame.MOUSEMOTION:
                self._on_move(ev.pos, ev.rel)

            elif ev.type == pygame.MOUSEBUTTONDOWN and ev.button == 1:
                # Panel button clicks
                if self.mode == 'aimbot':
                    clicked_btn = False
                    for atype, rect in self.aim_btn_rects.items():
                        if rect.collidepoint(ev.pos):
                            if atype == '_trig_toggle':
                                self.trig_on = not self.trig_on
                            else:
                                self.aim_type = atype
                            clicked_btn = True
                            break
                    if not clicked_btn and not self.show_result:
                        self._on_click(ev.pos)
                elif not self.show_result:
                    self._on_click(ev.pos)

    def _set_tickrate(self, tr):
        self.tickrate = tr
        self.feed_interval = 1000 // tr
        self.core._B = int(300 * (tr / 60))

    # ─── Challenge ────────────────────────────────────────

    def _start_challenge(self):
        print(f"\n--- CHALLENGE START --- mode={self.mode} aim={self.aim_type} trig={'ON' if self.trig_on else 'OFF'}")
        self.ch_active = True
        self.ch_total = 0
        self.ch_target = None
        self.ch_timer = 0.0
        self.spawn_delay = 0.5
        self.trig_armed = False
        self.trig_delay = 0.0
        self.core.reset()
        self.trail.clear()
        self.data_count = 0
        self.flash_timer = 0.0

    def _end_challenge(self):
        self.ch_active = False
        self.ch_target = None
        self.spawn_delay = 0.0
        self.trig_armed = False

        if self.ch_total > 0:
            verdict = self.core.get_verdict()
            ac = self.core.get_anomaly_count()
            aim = self.aim_type if self.mode == 'aimbot' else 'none'
            print(f"\n=== RESULT === mode={self.mode} aim={aim} verdict={verdict} anomalies={ac}\n")
            self.result_data = {
                'verdict': verdict,
                'anomalies': ac,
                'total': self.ch_total,
                'mode': self.mode,
                'aim_type': self.aim_type if self.mode == 'aimbot' else None,
            }
            self.show_result = True

    def _full_reset(self):
        self.core.reset()
        self.trail.clear()
        self.data_count = 0
        self.hits.clear()
        self.locked = False
        self.snapping = False
        self.trig_armed = False
        self.trig_delay = 0.0
        self.flash_timer = 0.0
        self.last_intent = None
        self.last_cursor_dist = None
        if self.ch_active:
            self.ch_active = False
            self.ch_target = None
            self.spawn_delay = 0.0
        self.show_result = False

    def _spawn_target(self):
        if not self.ch_active or self.ch_total >= self.ch_max:
            self._end_challenge()
            return
        self.ch_total += 1
        m = 80
        x = random.randint(m, CANVAS - m)
        y = random.randint(m, H - m)
        self.ch_target = (x, y)
        self.ch_timer = 0.0
        self.trig_armed = False

    # ─── Mouse ────────────────────────────────────────────

    def _on_move(self, pos, rel=(0, 0)):
        x, y = pos
        if x >= CANVAS:
            return

        now = pygame.time.get_ticks()
        if now - self.last_feed < self.feed_interval:
            return
        self.last_feed = now

        if self.mode == 'normal':
            self._feed(float(x), float(y), float(now))
            return

        real_x, real_y = float(x), float(y)

        if self.aim_type == 'silent':
            # Cursor = real mouse, feed = real mouse → no detection
            self.vpos = [real_x, real_y]
            self._feed(real_x, real_y, float(now))

        elif self.aim_type == 'aimlock':
            if self.locked:
                # Locked: vpos stays on target, feed real mouse (zigzag → detection)
                self._feed(real_x, real_y, float(now))
            else:
                self.vpos = [real_x, real_y]
                self._feed(real_x, real_y, float(now))

        elif self.aim_type == 'snap':
            if self.snapping:
                pass  # vpos managed by _update only
            else:
                self.vpos = [real_x, real_y]
                self._feed(real_x, real_y, float(now))

        # Trigger arming moved to _update

    def _on_click(self, pos):
        x, y = pos
        if x >= CANVAS or not self.ch_active or not self.ch_target:
            return

        tx, ty = self.ch_target
        print(f"[CLICK] mode={self.mode} aim={self.aim_type} mouse=({x},{y}) target=({tx},{ty})")

        if self.mode == 'aimbot':
            # FOV 체크: 실제 마우스가 타겟 FOV 안에 있는가?
            mx, my = float(x), float(y)
            fov_dist = math.sqrt((tx - mx) ** 2 + (ty - my) ** 2)
            in_fov = fov_dist <= self.aim_fov

            if self.aim_type == 'silent':
                if in_fov:
                    print(f"[SILENT] hit → target({tx},{ty})  cursor stays({self.vpos[0]:.0f},{self.vpos[1]:.0f})")
                    self._resolve_hit(float(tx), float(ty))
                else:
                    print(f"[SILENT] out of FOV ({fov_dist:.0f}>{self.aim_fov})")
                    self._resolve_hit(mx, my)
                return
            elif self.aim_type == 'aimlock':
                self._resolve_hit(self.vpos[0], self.vpos[1])
                return
            elif self.aim_type == 'snap':
                if not self.snapping:
                    self._resolve_hit(self.vpos[0], self.vpos[1])
                return
        if self.mode == 'aimbot':
            cx, cy = self.vpos[0], self.vpos[1]
        else:
            cx, cy = float(x), float(y)

        self._resolve_hit(cx, cy)

    def _resolve_hit(self, cx, cy):
        if not self.ch_target:
            return
        tx, ty = self.ch_target
        dist = math.sqrt((tx - cx) ** 2 + (ty - cy) ** 2)
        hit = dist <= 35

        # Intent 분석 (히트 시에만)
        intent = self.core.check_hit(float(tx), float(ty)) if hit else None
        self.last_intent = intent
        if hit and len(self.core._px) > 0:
            lx, ly = self.core._px[-1], self.core._py[-1]
            self.last_cursor_dist = math.sqrt((tx - lx) ** 2 + (ty - ly) ** 2)
        else:
            self.last_cursor_dist = None

        result = "HIT" if hit else "MISS"
        print(f"  [{result}] aim=({cx:.0f},{cy:.0f}) target=({tx},{ty}) dist={dist:.1f}")
        if intent is not None:
            # 팬텀 히트 거리 계산 (디버그용)
            lx, ly = self.core._px[-1], self.core._py[-1]
            cdist = math.sqrt((tx - lx) ** 2 + (ty - ly) ** 2)
            flags = []
            if cdist > self.core._PH:
                flags.append('PHANTOM')
            if intent < self.core._IT:
                flags.append('LOW_INTENT')
            flag_str = ' ← ' + ' + '.join(flags) if flags else ''
            print(f"  intent={intent:.3f} cursor_dist={cdist:.0f}{flag_str}")

        if hit:
            self.hits.append([float(tx), float(ty), "+1", C_GREEN, 0.5])
        else:
            self.hits.append([cx, cy, "MISS", C_RED, 0.5])

        self.locked = False  # release aimlock
        self.ch_target = None
        self.ch_timer = 0.0
        self.spawn_delay = 0.3
        self.trig_armed = False

    def _aimlock(self, tx, ty):
        now = pygame.time.get_ticks()
        print(f"[AIMLOCK] teleport ({self.vpos[0]:.0f},{self.vpos[1]:.0f}) → ({tx},{ty})")
        self.locked = True
        self.vpos = [float(tx), float(ty)]
        pygame.mouse.set_pos(int(tx), int(ty))
        self._feed(float(tx), float(ty), float(now))

    def _snap(self, tx, ty):
        self.snapping = True
        self.snap_from = list(self.vpos)
        self.snap_to = [float(tx), float(ty)]
        self.snap_t = 0.0
        self.snap_dur = random.uniform(0.05, 0.15)
        print(f"[SNAP] ({self.snap_from[0]:.0f},{self.snap_from[1]:.0f}) → ({tx},{ty})  dur={self.snap_dur*1000:.0f}ms")
        # 첫 프레임에 타겟 좌표를 즉시 feed → 속도 스파이크 → 3차 미분 비율 탐지
        now = pygame.time.get_ticks()
        self._feed(float(tx), float(ty), float(now))

    # ─── Feed ─────────────────────────────────────────────

    def _feed(self, x, y, t):
        result = self.core.add_point(x, y, t)
        self.data_count = result.data_count
        self.last_result = result

        # CSV log
        self._log_writer.writerow([
            f'{t:.0f}', f'{x:.1f}', f'{y:.1f}',
            self.mode, self.aim_type,
            int(result.is_anomaly), self.core.get_anomaly_count(),
        ])
        self._log_file.flush()

        # Flash on anomaly
        if result.is_anomaly:
            self.flash_timer = 0.15
            print(f"  *** ANOMALY *** count={self.core.get_anomaly_count()}")

        intensity = min(result.anomaly_score / 10.0, 1.0)
        self.trail.append((x, y, intensity))
        if len(self.trail) > 200:
            self.trail.pop(0)

    # ─── Update ───────────────────────────────────────────

    def _update(self, dt):
        # Hit effects
        for h in self.hits:
            h[4] -= dt
        self.hits = [h for h in self.hits if h[4] > 0]

        # Flash timer
        if self.flash_timer > 0:
            self.flash_timer -= dt

        # Auto-activate aimbot when target enters FOV
        if self.mode == 'aimbot' and self.ch_target and self.ch_active and not self.snapping:
            tx, ty = self.ch_target
            mx, my = pygame.mouse.get_pos()
            fov_dist = math.sqrt((tx - mx) ** 2 + (ty - my) ** 2)

            if self.aim_type == 'aimlock' and fov_dist <= self.aim_fov:
                if not self.locked:
                    print(f"[AIMLOCK] auto-lock → ({tx},{ty})")
                self.locked = True
                self.vpos = [float(tx), float(ty)]
                pygame.mouse.set_pos(int(tx), int(ty))

            elif self.aim_type == 'snap' and fov_dist <= self.aim_fov:
                vdist = math.sqrt((tx - self.vpos[0]) ** 2 + (ty - self.vpos[1]) ** 2)
                if vdist > 35:
                    self._snap(tx, ty)

        # Snap animation (visual only — data already fed at snap start)
        if self.snapping:
            self.snap_t += dt
            p = min(self.snap_t / self.snap_dur, 1.0)
            ease = 1 - (1 - p) ** 3

            sx, sy = self.snap_from
            tx, ty = self.snap_to
            self.vpos[0] = sx + (tx - sx) * ease
            self.vpos[1] = sy + (ty - sy) * ease
            pygame.mouse.set_pos(int(self.vpos[0]), int(self.vpos[1]))

            if p >= 1.0:
                self.snapping = False

        # Aimlock: continuously feed target position while locked
        if self.locked and self.ch_target:
            now = pygame.time.get_ticks()
            self._feed(self.vpos[0], self.vpos[1], float(now))

        # ─── Trigger bot: 커서가 타겟 위에 있으면 클릭 ───
        if self.trig_on and self.ch_target and self.ch_active and not self.snapping and not self.trig_armed:
            tx, ty = self.ch_target
            # 트리거 = vpos가 타겟 위에 있는가? (히트 반경 35px)
            vdist = math.sqrt((tx - self.vpos[0]) ** 2 + (ty - self.vpos[1]) ** 2)
            if vdist <= 35:
                self.trig_armed = True
                self.trig_delay = random.uniform(0.03, 0.12)

        # Trigger bot auto-fire
        if self.trig_armed and self.ch_target:
            self.trig_delay -= dt
            if self.trig_delay <= 0:
                self.trig_armed = False
                tx, ty = self.ch_target
                print(f"[TRIGGER] auto-fire → vpos({self.vpos[0]:.0f},{self.vpos[1]:.0f})")
                self._resolve_hit(self.vpos[0], self.vpos[1])

        # Target timeout
        if self.ch_active and self.ch_target and not self.snapping:
            self.ch_timer += dt
            if self.ch_timer >= self.ch_timeout:
                tx, ty = self.ch_target
                self.hits.append([float(tx), float(ty), "TIMEOUT", C_ORANGE, 0.5])
                self.ch_target = None
                self.ch_timer = 0.0
                self.spawn_delay = 0.3
                self.trig_armed = False

        # Spawn delay
        if self.ch_active and self.spawn_delay > 0 and not self.ch_target:
            self.spawn_delay -= dt
            if self.spawn_delay <= 0:
                self.spawn_delay = 0.0
                self._spawn_target()

    # ─── Draw ─────────────────────────────────────────────

    def _draw(self):
        self.screen.fill(C_BG)
        self._draw_grid()

        if not self.trail:
            self._draw_canvas_hint()

        self._draw_trail()
        self._draw_target()
        self._draw_cursor()
        self._draw_hits()

        # Red flash border on anomaly
        if self.flash_timer > 0:
            alpha = int(180 * (self.flash_timer / 0.15))
            flash = pygame.Surface((CANVAS, H), pygame.SRCALPHA)
            pygame.draw.rect(flash, (248, 81, 73, alpha), (0, 0, CANVAS, H), 4)
            self.screen.blit(flash, (0, 0))

        self._draw_panel()

        if self.mode == 'aimbot' and self.ch_active:
            self._draw_aim_indicator()

        if self.show_result:
            self._draw_result()

        pygame.display.flip()

    def _draw_grid(self):
        c = (20, 25, 30)
        for x in range(0, CANVAS, 50):
            pygame.draw.line(self.screen, c, (x, 0), (x, H))
        for y in range(0, H, 50):
            pygame.draw.line(self.screen, c, (0, y), (CANVAS, y))

    def _draw_canvas_hint(self):
        cx, cy = CANVAS // 2, H // 2
        lines = [
            ("Move mouse here", self.f_hint, C_DIM),
            ("", None, None),
            ("SPACE  start challenge", self.f_mid, C_CYAN),
            ("TAB    toggle aimbot", self.f_mid, C_CYAN),
            ("1~4  aim type  /  T  trigger", self.f_mid, C_CYAN),
        ]
        sc = self.ui_scale
        y = cy - int(60 * sc)
        for text, font, color in lines:
            if font is None:
                y += int(12 * sc)
                continue
            surf = font.render(text, True, color)
            self.screen.blit(surf, (cx - surf.get_width() // 2, y))
            y += int(28 * sc)

    def _draw_trail(self):
        n = len(self.trail)
        if n < 2:
            return
        for i in range(1, n):
            x0, y0, _ = self.trail[i - 1]
            x1, y1, inten = self.trail[i]
            fade = i / n

            if self.mode == 'aimbot':
                r = int(255 * inten * fade)
                g = int(255 * (1 - inten) * fade)
                color = (min(255, max(0, r)), min(255, max(0, g)), 0)
            else:
                r = int(255 * inten * fade)
                g = int(212 * (1 - inten) * fade)
                b = int(255 * fade)
                color = (min(255, max(0, r)), min(255, max(0, g)), min(255, max(0, b)))

            w = max(1, int(2 + inten * 2))
            pygame.draw.line(self.screen, color, (int(x0), int(y0)), (int(x1), int(y1)), w)

        lx, ly, _ = self.trail[-1]
        c = C_GREEN if self.mode == 'aimbot' else C_CYAN
        pygame.draw.circle(self.screen, c, (int(lx), int(ly)), 4)

    def _draw_target(self):
        if not self.ch_target:
            return
        tx, ty = self.ch_target
        pygame.draw.circle(self.screen, C_RED, (tx, ty), 25, 2)
        pygame.draw.circle(self.screen, C_RED, (tx, ty), 15, 2)
        pygame.draw.circle(self.screen, C_RED, (tx, ty), 5)
        pulse = int(25 + 10 * math.sin(self.ch_timer * 5))
        pygame.draw.circle(self.screen, C_RED, (tx, ty), pulse, 1)

    def _draw_cursor(self):
        if self.mode != 'aimbot':
            return
        x, y = int(self.vpos[0]), int(self.vpos[1])
        pygame.draw.circle(self.screen, C_GREEN, (x, y), 8, 2)
        pygame.draw.circle(self.screen, C_GREEN, (x, y), 2)
        pygame.draw.line(self.screen, C_GREEN, (x - 14, y), (x - 5, y))
        pygame.draw.line(self.screen, C_GREEN, (x + 5, y), (x + 14, y))
        pygame.draw.line(self.screen, C_GREEN, (x, y - 14), (x, y - 5))
        pygame.draw.line(self.screen, C_GREEN, (x, y + 5), (x, y + 14))

    def _draw_hits(self):
        for h in self.hits:
            x, y, text, color, remaining = h
            progress = 1.0 - remaining / 0.5
            offset = int(progress * 30)
            surf = self.f_mid.render(text, True, color)
            self.screen.blit(surf, (int(x) - surf.get_width() // 2, int(y) - 20 - offset))

    def _draw_aim_indicator(self):
        sc = self.ui_scale
        label = AIM_TYPES.get(self.aim_type, '')
        label += f"  FOV:{self.aim_fov}"
        if self.trig_on:
            label += "  +TRIGGER"
        t = self.f_small.render(label, True, (0, 0, 0))
        sw = t.get_width() + int(20 * sc)
        sh = int(28 * sc)
        s = pygame.Surface((sw, sh), pygame.SRCALPHA)
        s.fill((255, 165, 0, 180))
        self.screen.blit(s, (int(10 * sc), int(10 * sc)))
        self.screen.blit(t, (int(18 * sc), int(10 * sc) + (sh - t.get_height()) // 2))

    # ─── Panel (simplified — verdict only) ────────────────

    def _draw_panel(self):
        sc = self.ui_scale
        pygame.draw.rect(self.screen, C_PANEL, (CANVAS, 0, PANEL, H))
        pygame.draw.line(self.screen, C_BORDER, (CANVAS, 0), (CANVAS, H))

        x = CANVAS + int(20 * sc)
        pw = PANEL - int(40 * sc)
        y = int(20 * sc)

        # ── Title ──
        self.screen.blit(self.f_title.render("SCHRODINGER", True, C_CYAN), (x, y))
        y += int(24 * sc)
        self.screen.blit(self.f_small.render(f"Anti-Cheat Test  |  {self.tickrate} tick  (F1/F2)", True, C_DIM), (x, y))
        y += int(28 * sc)

        # ── Mode ──
        pygame.draw.line(self.screen, C_BORDER, (x, y), (x + pw, y))
        y += int(12 * sc)
        mc = C_RED if self.mode == 'aimbot' else C_GREEN
        mode_label = self.mode.upper()
        self.screen.blit(self.f_title.render(f"MODE: {mode_label}", True, mc), (x, y))
        y += int(26 * sc)

        if self.mode == 'aimbot':
            # Aim type buttons
            btn_labels = [
                ('silent',  '1 Silent'),
                ('aimlock', '2 Aimlock'),
                ('snap',    '3 Snap'),
            ]
            bh = int(18 * sc)
            bx = x
            for atype, label in btn_labels:
                selected = (atype == self.aim_type)
                surf = self.f_small.render(label, True, C_CYAN if selected else C_DIM)
                bw = surf.get_width() + int(10 * sc)
                btn_rect = pygame.Rect(bx, y, bw, bh)
                self.aim_btn_rects[atype] = btn_rect
                if selected:
                    pygame.draw.rect(self.screen, C_CYAN, btn_rect, 1, border_radius=3)
                self.screen.blit(surf, (bx + int(5 * sc), y + int(2 * sc)))
                bx += bw + int(4 * sc)
            y += int(24 * sc)

            # Trigger bot toggle button
            trig_label = f"T Trigger: {'ON' if self.trig_on else 'OFF'}"
            trig_color = C_GREEN if self.trig_on else C_DIM
            trig_surf = self.f_small.render(trig_label, True, trig_color)
            tw = trig_surf.get_width() + int(10 * sc)
            trig_rect = pygame.Rect(x, y, tw, bh)
            self.aim_btn_rects['_trig_toggle'] = trig_rect
            if self.trig_on:
                pygame.draw.rect(self.screen, C_GREEN, trig_rect, 1, border_radius=3)
            self.screen.blit(trig_surf, (x + int(5 * sc), y + int(2 * sc)))
            y += int(22 * sc)

            # Extra info
            info_parts = [f"Aim FOV: {self.aim_fov}px  (scroll)"]
            for info in info_parts:
                self.screen.blit(self.f_small.render(info, True, C_ORANGE), (x, y))
                y += int(16 * sc)
        y += int(8 * sc)

        # ── Big Verdict ──
        pygame.draw.line(self.screen, C_BORDER, (x, y), (x + pw, y))
        y += int(16 * sc)

        verdict = self.core.get_verdict()
        ac = self.core.get_anomaly_count()

        if self.data_count < 10:
            vc = C_DIM
            vt = "..."
            sub = "Collecting data"
        elif verdict == 'CLEAN':
            vc = C_GREEN
            vt = "CLEAN"
            sub = "No anomaly detected"
        elif verdict == 'WARNING':
            vc = C_YELLOW
            vt = "WARNING"
            sub = f"{ac} anomalies detected"
        else:
            vc = C_RED
            vt = "SUSPECT"
            sub = f"{ac} anomalies detected"

        # Verdict box
        vbox_h = int(80 * sc)
        vr = pygame.Rect(x - 5, y, pw + 10, vbox_h)
        box_bg = pygame.Surface((vr.w, vr.h), pygame.SRCALPHA)
        box_bg.fill((*vc, 20))
        self.screen.blit(box_bg, vr.topleft)
        pygame.draw.rect(self.screen, vc, vr, 2, border_radius=8)

        # Big text
        t = self.f_big.render(vt, True, vc)
        self.screen.blit(t, (x + pw // 2 - t.get_width() // 2, y + int(12 * sc)))
        # Subtitle
        t2 = self.f_small.render(sub, True, vc)
        self.screen.blit(t2, (x + pw // 2 - t2.get_width() // 2, y + int(55 * sc)))
        y += int(100 * sc)

        # ── Challenge Progress ──
        if self.ch_active:
            pygame.draw.line(self.screen, C_BORDER, (x, y), (x + pw, y))
            y += int(12 * sc)
            self.screen.blit(
                self.f_mid.render(f"Target {self.ch_total} / {self.ch_max}", True, C_TEXT),
                (x, y),
            )
            y += int(30 * sc)

        # ── Debug Log ──
        pygame.draw.line(self.screen, C_BORDER, (x, y), (x + pw, y))
        y += int(10 * sc)
        self.screen.blit(self.f_small.render("DETECTION", True, C_DIM), (x, y))
        y += int(16 * sc)
        if self.last_result:
            r = self.last_result
            verdict = self.core.get_verdict()
            v_c = C_RED if verdict == 'SUSPECT' else C_ORANGE if verdict == 'WARNING' else C_DIM
            status = "DETECTED" if r.is_anomaly else "OK"
            st_c = C_RED if r.is_anomaly else C_DIM
            logs = [
                (f"status:     {status}", st_c),
                (f"anomalies:  {ac}", C_RED if ac > 0 else C_DIM),
                (f"verdict:    {verdict}", v_c),
            ]
            for text, color in logs:
                self.screen.blit(self.f_small.render(text, True, color), (x, y))
                y += int(14 * sc)
        else:
            self.screen.blit(self.f_small.render("No data yet", True, C_DIM), (x, y))
            y += int(14 * sc)
        y += int(6 * sc)

        # ── Controls (bottom) ──
        y = H - int(160 * sc)
        pygame.draw.line(self.screen, C_BORDER, (x, y), (x + pw, y))
        y += int(10 * sc)
        self.screen.blit(self.f_small.render("CONTROLS", True, C_DIM), (x, y))
        y += int(18 * sc)
        controls = [
            ("TAB",    "Mode Toggle"),
            ("SPACE",  "Start / Stop"),
            ("Click",  "Aim Type (panel)"),
            ("T / 5",  "Trigger Bot Toggle"),
            ("Scroll", "Trigger FOV"),
            ("+/-",    "Smooth Aim Strength"),
            ("F1/F2",  "Tick Rate -/+"),
            ("R",      "Reset"),
            ("ESC",    "Quit"),
        ]
        key_offset = int(55 * sc)
        for key, desc in controls:
            self.screen.blit(self.f_small.render(key, True, C_CYAN), (x, y))
            self.screen.blit(self.f_small.render(desc, True, C_DIM), (x + key_offset, y))
            y += int(15 * sc)

    # ─── Result Overlay ───────────────────────────────────

    def _draw_result(self):
        sc = self.ui_scale
        overlay = pygame.Surface((W, H), pygame.SRCALPHA)
        overlay.fill((0, 0, 0, 200))
        self.screen.blit(overlay, (0, 0))

        bw, bh = int(400 * sc), int(260 * sc)
        bx = (W - bw) // 2
        by = (H - bh) // 2
        pygame.draw.rect(self.screen, C_PANEL, (bx, by, bw, bh), border_radius=10)
        pygame.draw.rect(self.screen, C_BORDER, (bx, by, bw, bh), 1, border_radius=10)

        d = self.result_data
        cx = bx + bw // 2
        y = by + int(25 * sc)

        # Title
        t = self.f_title.render("RESULT", True, C_CYAN)
        self.screen.blit(t, (cx - t.get_width() // 2, y))
        y += int(35 * sc)

        # Mode info
        mode_txt = d['mode'].upper()
        if d.get('aim_type'):
            mode_txt += f"  /  {AIM_TYPES.get(d['aim_type'], d['aim_type'].upper())}"
        t = self.f_mid.render(mode_txt, True, C_DIM)
        self.screen.blit(t, (cx - t.get_width() // 2, y))
        y += int(30 * sc)

        # Big verdict
        v = d['verdict']
        ac = d['anomalies']
        if v == 'CLEAN':
            vc, vt = C_GREEN, "CLEAN"
        elif v == 'WARNING':
            vc, vt = C_YELLOW, "WARNING"
        else:
            vc, vt = C_RED, "SUSPECT"

        vbox_h = int(70 * sc)
        vr = pygame.Rect(bx + int(30 * sc), y, bw - int(60 * sc), vbox_h)
        s = pygame.Surface((vr.w, vr.h), pygame.SRCALPHA)
        s.fill((*vc, 25))
        self.screen.blit(s, vr.topleft)
        pygame.draw.rect(self.screen, vc, vr, 2, border_radius=6)

        t = self.f_big.render(vt, True, vc)
        self.screen.blit(t, (cx - t.get_width() // 2, y + int(8 * sc)))

        if ac > 0:
            sub = f"{ac} anomalies detected"
        else:
            sub = "No anomaly detected"
        t2 = self.f_small.render(sub, True, vc)
        self.screen.blit(t2, (cx - t2.get_width() // 2, y + int(48 * sc)))
        y += int(85 * sc)

        # Dismiss
        t = self.f_small.render("Press any key to continue", True, C_DIM)
        self.screen.blit(t, (cx - t.get_width() // 2, y))


# ─── Entry ────────────────────────────────────────────────
if __name__ == '__main__':
    Demo().run()
