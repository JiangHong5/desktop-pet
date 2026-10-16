import os
import re
import pygame
import sys

class Pet:
    """Represents a pet that can be controlled and animated. It can be moved, rotated, and scaled.
    You can also toggle if we simulate physics for the pet.
    """

    def __init__(self, name, pos=(0, 0), scale=(1, 1)):
        self.name = name
        self.scale = scale
        # Use os.path.join for portability
        self.path = os.path.join("assets", name)
        self.frames = {}  # animation_name -> list[Surface]
        self._load_frames()

        # Choose initial image: prefer 'stand', otherwise any first available animation
        default_anim = "stand"
        if default_anim in self.frames and self.frames[default_anim]:
            self.image = self.frames[default_anim][0]
        else:
            # pick first available
            any_anim = next(iter(self.frames.values()), None)
            if any_anim and len(any_anim) > 0:
                self.image = any_anim[0]
            else:
                # fallback placeholder surface
                surf = pygame.Surface((50, 50), pygame.SRCALPHA)
                surf.fill((200, 200, 200, 255))
                self.image = surf

        self.rect = self.image.get_rect(topleft=pos)
        self.velocity = pygame.Vector2(0, 0)
        self.gravity = 0.5
        self.physics_enabled = True

        self.dragging = False
        # mouse_offset: (dx, dy) from mouse to rect.center when dragging starts
        self.mouse_offset = (0, 0)

        # ground 常量（按需要调整）
        display_surf = pygame.display.get_surface()
        if display_surf:
            self.GROUND_Y = display_surf.get_height() - 50  # 假设地面在窗口底部上方 50 像素处
        else:
            self.GROUND_Y = 400  # fallback if display not initialized at this moment

        # 根据初始位置决定是否着地
        self.on_ground = self.rect.bottom >= self.GROUND_Y
        self.prev_on_ground = self.on_ground  # 用于检测状态变化
        if self.on_ground:
            self.rect.bottom = self.GROUND_Y
            self.velocity.y = 0

        self.animation_flag = False
        self.wanted_animation = "stand"
        self.last_animation = "stand"
        self.animation_timer = 0
        self.frame = -1
        self.frame_timer = 0
        self.frame_during = []
        self.animation = "stand"

    def _load_frames(self):
        """Scan the asset directory and preload all png frames into memory.

        The filenames are interpreted as:
            <anim>.png            -> single-frame animation "anim"
            <anim>_0.png, <anim>_1.png, ... -> multi-frame animation "anim"
        All loaded images are scaled according to `self.scale`.
        """
        self.frames = {}
        if not os.path.isdir(self.path):
            # No assets directory found; leave frames empty
            return

        files = [f for f in os.listdir(self.path) if f.lower().endswith(".png")]
        # Group by animation name, capture optional numeric suffix
        grouped = {}
        for f in files:
            namepart = f[:-4]  # strip .png
            m = re.match(r"(?P<name>.+?)(?:_(?P<idx>\d+))?$", namepart)
            if not m:
                continue
            anim = m.group("name")
            idx = m.group("idx")
            idx = int(idx) if idx is not None else None
            grouped.setdefault(anim, []).append((idx, f))

        for anim, entries in grouped.items():
            # sort: entries with numeric idx sorted by idx, others after (or before — we choose numeric then non-numeric)
            numeric = [e for e in entries if e[0] is not None]
            non_numeric = [e for e in entries if e[0] is None]
            numeric.sort(key=lambda x: x[0])
            sorted_files = [e[1] for e in numeric] + [e[1] for e in non_numeric]

            surfaces = []
            for fname in sorted_files:
                fullpath = os.path.join(self.path, fname)
                try:
                    surf = pygame.image.load(fullpath).convert_alpha()
                except Exception:
                    # skip files that fail to load
                    continue
                if self.scale != (1, 1):
                    w = int(surf.get_width() * self.scale[0])
                    h = int(surf.get_height() * self.scale[1])
                    if w <= 0: w = 1
                    if h <= 0: h = 1
                    surf = pygame.transform.scale(surf, (w, h))
                surfaces.append(surf)

            if surfaces:
                self.frames[anim] = surfaces

        # If nothing found, frames stays empty; caller will handle fallback

    def update(self):
        # 先记录上一次状态
        self.prev_on_ground = self.on_ground

        if not self.dragging and not self.on_ground:
            self.setup_animation('fall')

        # 物理更新
        if self.physics_enabled and not self.dragging:
            if not self.on_ground:
                self.velocity.y += self.gravity
                self.rect.y += int(self.velocity.y)

            if self.rect.bottom >= self.GROUND_Y:
                self.rect.bottom = self.GROUND_Y
                self.on_ground = True
                self.velocity.y = 0
            else:
                self.on_ground = False

        # 落地瞬间触发落地动画（从空中变为着地）
        if not self.prev_on_ground and self.on_ground:
            # 示例参数：总时长 20 帧，逐帧三帧，每帧时长分别为 6、7、7
            self.setup_animation("land", has_frame=True, frame_during=[6, 7, 7])

        # 拖拽逻辑（不再打印调试信息）
        mouse_pressed = pygame.mouse.get_pressed()[0]
        mouse_pos = pygame.mouse.get_pos()
        if mouse_pressed and self.rect.collidepoint(mouse_pos):
            if not self.dragging:
                # on drag start, compute offset from mouse to rect center
                mouse_x, mouse_y = mouse_pos
                self.mouse_offset = (self.rect.centerx - mouse_x, self.rect.centery - mouse_y)
            self.dragging = True
        else:
            self.dragging = False

        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            new_center = (mouse_x + self.mouse_offset[0], mouse_y + self.mouse_offset[1])
            self.rect.center = (int(new_center[0]), int(new_center[1]))
            if self.rect.bottom >= self.GROUND_Y:
                self.rect.bottom = self.GROUND_Y
                self.on_ground = True
            else:
                self.on_ground = False
            self.velocity.y = 0

        # 每帧处理动画
        self.do_animation()

    def setup_animation(self, name: str = "stand", has_frame: bool = False, frame_during: list = []):
        """Set up an animation. Execute it by `do_animation`.

        Args:
            name (str, optional): The name of the animation (Decides by the file name). Defaults to "stand".
            has_frame (bool, optional): Whether the animation has specific frames. Defaults to False.
            frame_during (list[int], optional): A list of durations for each frame.
        """
        self.wanted_animation = name
        self.animation_timer = 2 if not has_frame else sum(frame_during)
        self.frame_during = list(frame_during)
        if has_frame and self.frame_during:
            self.frame = 0
            self.frame_timer = self.frame_during[0]
        else:
            self.frame = -1
            self.frame_timer = 0
        self.animation_flag = True

    def do_animation(self):
        """Execute the animation."""
        try:
            if not self.animation_flag:
                return

            self.animation = self.wanted_animation

            if self.animation_timer > 0:
                self.animation_timer -= 1

            if self.frame != -1:
                if self.frame_timer > 0:
                    self.frame_timer -= 1
                if self.frame_timer <= 0:
                    self.frame += 1
                    if self.frame >= len(self.frame_during):
                        self.frame = -1
                        self.frame_timer = 0
                    else:
                        self.frame_timer = self.frame_during[self.frame]

            if self.animation_timer == 0 and self.frame == -1:
                self.animation_flag = False
                self.last_animation = self.animation
                self.animation = "stand"
        except FileNotFoundError as e:
            # 兼容性处理：如果帧文件丢失，回退到 stand
            self.animation_flag = False
            self.animation = "stand"
            raise ValueError(f"Animation '{self.wanted_animation}' cannot be completed because a file is missing.") from e

    def draw(self, surface: pygame.Surface):
        # 从已加载的 frames 中取出当前帧（已被缩放）
        frames = self.frames.get(self.animation) or self.frames.get("stand") or [self.image]
        idx = 0 if self.frame == -1 else min(self.frame, len(frames) - 1)
        img = frames[idx]
        # 更新 rect 保持位置
        self.rect = img.get_rect(topleft=self.rect.topleft)
        surface.blit(img, self.rect)
