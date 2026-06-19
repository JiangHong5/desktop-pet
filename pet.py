import ctypes
import pygame
import sys


class Pet:
    """Represents a pet that can be controlled and animated. It can be moved, rotated, and scaled.
    You can also toggle if we simulate physics for the pet.
    """

    def __init__(self, name, pos=(0, 0), scale=(1, 1)):
        self.name = name
        self.scale = scale
        self.path = f"assets/{name}/"
        self.image = pygame.image.load(self.path + "stand.png").convert_alpha()
        self.rect = self.image.get_rect(topleft=pos)
        self.velocity = pygame.Vector2(0, 0)
        self.gravity = 0.5
        self.physics_enabled = True
        
        self.dragging = False
        self.mouse_offset: tuple[int, int] = (0, 0)

        # ground 常量（按需要调整）
        self.GROUND_Y = pygame.display.get_surface().get_height() - 50  # 假设地面在窗口底部上方 50 像素处

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

    def update(self):
        # 先记录上一次状态
        self.prev_on_ground = self.on_ground

        if not self.dragging and not self.on_ground:
            self.setup_animation('fall')

        # 物理更新
        if self.physics_enabled and not self.dragging:
            # self.setup_animation('fall', 1)
            if not self.on_ground:
                self.velocity.y += self.gravity
                self.rect.y += self.velocity.y

            if self.rect.bottom >= self.GROUND_Y:
                self.rect.bottom = self.GROUND_Y
                self.on_ground = True
                self.velocity.y = 0
            else:
                self.on_ground = False

        # 落地瞬间触发落地动画（从空中变为着地）
        if not self.prev_on_ground and self.on_ground:
            # 示例参数：总时长 20 帧，逐帧三帧，每帧时长分别为 6、7、7
            print("landed!")
            self.setup_animation("land", has_frame=True, frame_during=[6,7,7])

        # 拖拽逻辑……
        print(pygame.mouse.get_pressed(), pygame.mouse.get_pos(), self.rect)
        if pygame.mouse.get_pressed()[0] and self.rect.collidepoint(pygame.mouse.get_pos()):
            self.dragging = True
            mouse_x, mouse_y = pygame.mouse.get_pos()
            # self.mouse_offset = (self.rect.centerx - mouse_x, self.rect.centery - mouse_y)
        else:
            self.dragging = False
        if self.dragging:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            self.rect.center = (mouse_x + self.mouse_offset[0], mouse_y + self.mouse_offset[1]) 
            if self.rect.bottom >= self.GROUND_Y:
                self.rect.bottom = self.GROUND_Y
                self.on_ground = True
            else:
                self.on_ground = False
            self.velocity.y = 0

        # 每帧处理动画
        self.do_animation()

    def setup_animation(self, name: str = "stand", has_frame: bool = False, frame_during: list[int]=[]):
        """Set up an animation. Execute it by `do_animation`.

        Args:
            name (str, optional): The name of the animation (Decides by the file name). Defaults to "stand".
            has_frame (bool, optional): Whether the animation has specific frames. Defaults to False.
            frame_during (list[int], optional): A list of durations for each frame. Please guarantee that the frames really exists, or maybe we'll raise an error in `do_animation`(I know that's not good). Defaults to [].
        
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
        # 不要在这里再直接调用 self.do_animation()，让 update 统一调用

    def do_animation(self):
        """Execute the animation.
        Raises:
            ValueError: If the animation or the frames set up in the `setup_animation` doesn't exist.
        """
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
            print(f"Animation file not found: {e.filename}")
            self.animation_flag = False
            self.animation = "stand"
            raise ValueError(f"Animation '{self.wanted_animation}' with frame {self.frame} does not exist. Please check the file name and the frame setup.") from e

    def draw(self, surface: pygame.Surface):
        # 修正文件名拼接，避免语法错误
        suffix = "" if self.frame == -1 else f"_{self.frame}"
        fname = self.path + f"{self.animation}{suffix}.png"
        # print(f"Drawing animation: {self.animation}, frame: {self.frame}, file name: {fname}")
        self.image = pygame.image.load(fname).convert_alpha()
        self.rect = self.image.get_rect(topleft=self.rect.topleft)
        self.image = pygame.transform.scale(
            self.image,
            (int(self.rect.width * self.scale[0]), int(self.rect.height * self.scale[1]))
        )
        self.rect = self.image.get_rect(topleft=self.rect.topleft)
        pygame.draw.rect(surface, (255, 0, 0), self.rect, 1)  # 调试用，画出边框
        surface.blit(self.image, self.rect)
