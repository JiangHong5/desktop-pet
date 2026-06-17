# # # ...existing code...
# # import pyglet as pgl
# # from pyglet import shapes

# # class InvisibleWindow(pgl.window.Window):
# #     def __init__(self, width, height):
# #         super().__init__(width, height, caption="Invisible Window", visible=False)
# #         self.set_location(100, 100)  # Set the window position

# #     def on_draw(self):
# #         self.clear()  # Clear the window (invisible)
# #         # Draw your shapes here
# #         if hasattr(self, "batch"):
# #             self.batch.draw()
# #         elif hasattr(self, "rect"):
# #             self.rect.draw()

# # window = InvisibleWindow(800, 600)
# # window.set_visible(True)  # Make the window visible after initialization

# # # closes when press Esc
# # @window.event
# # def on_key_press(symbol, modifiers):
# #     if symbol == pgl.window.key.ESCAPE:
# #         window.close()
# #         pgl.app.exit()

# # # Use a Batch so drawing happens in on_draw
# # batch = pgl.graphics.Batch()
# # rect = shapes.Rectangle(100, 100, 200, 150, color=(50, 225, 30), batch=batch)

# # # attach to window so on_draw can find them
# # window.batch = batch
# # window.rect = rect

# # # window.set_visible(False)

# # pgl.app.run()
# # # ...existing code...

# # ...existing code...
# import os
# import ctypes
# import pyglet as pgl
# from pyglet import shapes
# from pyglet import gl

# # ...existing code...
# class InvisibleWindow(pgl.window.Window):
#     def __init__(self, width, height):
#         # 保留原有可见性控制
#         super().__init__(width, height, caption="Invisible Window", visible=False)
#         self.set_location(100, 100)  # Set the window position

#         # 开启混合（绘制时可用 alpha）
#         gl.glEnable(gl.GL_BLEND)
#         gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)

#     def on_draw(self):
#         # 使用色键色（这里用洋红 1.0,0.0,1.0）清屏，随后该颜色会被设为透明
#         gl.glClearColor(1.0, 0.0, 1.0, 1.0)
#         self.clear()
#         if hasattr(self, "batch"):
#             self.batch.draw()
#         elif hasattr(self, "rect"):
#             self.rect.draw()

# # ...existing code...
# window = InvisibleWindow(800, 600)
# window.set_visible(True)  # Make the window visible after initialization

# # 在 Windows 上把窗口设为分层窗口并启用色键透明
# def make_window_colorkey_transparent(win, color=(255, 0, 255)):
#     if os.name != "nt":
#         return
#     # 获取 hwnd（pyglet 不同版本字段可能不同）
#     hwnd = getattr(win, "hwnd", None) or getattr(win, "_hwnd", None)
#     if not hwnd:
#         return
#     user32 = ctypes.windll.user32
#     GWL_EXSTYLE = -20
#     WS_EX_LAYERED = 0x00080000
#     LWA_COLORKEY = 0x00000001

#     # 取当前扩展样式并加入 WS_EX_LAYERED
#     ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
#     user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED)

#     # COLORREF = 0x00bbggrr, 计算方式： r | (g<<8) | (b<<16)
#     r, g, b = color
#     colref = r | (g << 8) | (b << 16)
#     user32.SetLayeredWindowAttributes(hwnd, colref, 0, LWA_COLORKEY)

# # 设定色键为洋红（255,0,255）
# make_window_colorkey_transparent(window, (255, 0, 255))

# # closes when press Esc
# @window.event
# def on_key_press(symbol, modifiers):
#     if symbol == pgl.window.key.ESCAPE:
#         window.close()
#         pgl.app.exit()

# # Use a Batch so drawing happens in on_draw
# batch = pgl.graphics.Batch()
# rect = shapes.Rectangle(100, 100, 200, 150, color=(50, 225, 30), batch=batch)

# # attach to window so on_draw can find them
# window.batch = batch
# window.rect = rect

# pgl.app.run()
# # ...existing code...

# ...existing code...
import ctypes
import pygame
import sys
from pet import Pet

# def make_window_colorkey_transparent(hwnd, color=(255,0,255)):
#     """AI generated cool function, it can make a color on a window become invisible.

#     Args:
#         hwnd (int): the window's handler.
#         color (tuple, optional): the color to make transparent. Defaults to (255,0,255).
#     """
#     user32 = ctypes.windll.user32
#     GWL_EXSTYLE = -20
#     WS_EX_LAYERED = 0x00080000
#     LWA_COLORKEY = 0x00000001

#     ex = user32.GetWindowLongW(hwnd, GWL_EXSTYLE)
#     user32.SetWindowLongW(hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED)

#     r,g,b = color
#     colref = r | (g << 8) | (b << 16)
#     user32.SetLayeredWindowAttributes(hwnd, colref, 0, LWA_COLORKEY)


#     # 将窗口设为始终置顶
# def set_window_always_on_top(hwnd, on_top=True):
#     user32 = ctypes.windll.user32
#     HWND_TOPMOST = -1
#     HWND_NOTOPMOST = -2
#     SWP_NOSIZE = 0x0001
#     SWP_NOMOVE = 0x0002
#     SWP_SHOWWINDOW = 0x0040
#     hpos = HWND_TOPMOST if on_top else HWND_NOTOPMOST
#     user32.SetWindowPos(hwnd, hpos, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)

# ...existing code...
import os
import ctypes
import ctypes.wintypes

def make_window_colorkey_transparent(hwnd, color=(255,0,255)):
    if hwnd is None or os.name != "nt":
        return
    user32 = ctypes.windll.user32
    GWL_EXSTYLE = -20
    WS_EX_LAYERED = 0x00080000
    LWA_COLORKEY = 0x00000001

    # 在 64-bit 上优先使用 *Ptr 版本
    try:
        GetWindowLongPtr = user32.GetWindowLongPtrW
        SetWindowLongPtr = user32.SetWindowLongPtrW
    except AttributeError:
        GetWindowLongPtr = user32.GetWindowLongW
        SetWindowLongPtr = user32.SetWindowLongW

    ex = GetWindowLongPtr(hwnd, GWL_EXSTYLE)
    SetWindowLongPtr(hwnd, GWL_EXSTYLE, ex | WS_EX_LAYERED)

    r, g, b = color
    colref = r | (g << 8) | (b << 16)
    user32.SetLayeredWindowAttributes(hwnd, colref, 0, LWA_COLORKEY)

def set_window_always_on_top(hwnd, on_top=True):
    if hwnd is None or os.name != "nt":
        return
    user32 = ctypes.windll.user32
    HWND_TOPMOST = ctypes.wintypes.HWND(-1)
    HWND_NOTOPMOST = ctypes.wintypes.HWND(-2)
    SWP_NOSIZE = 0x0001
    SWP_NOMOVE = 0x0002
    SWP_SHOWWINDOW = 0x0040
    hpos = HWND_TOPMOST if on_top else HWND_NOTOPMOST
    user32.SetWindowPos(hwnd, hpos, 0, 0, 0, 0, SWP_NOMOVE | SWP_NOSIZE | SWP_SHOWWINDOW)
# ...existing code...

def main():
    pygame.init()
    size = (400, 400)
    # NOFRAME 创建无栏窗口
    info = pygame.display.Info()
    screen = pygame.display.set_mode((info.current_w, info.current_h), pygame.NOFRAME)

    # 创建宠物实例
    pet = Pet("stickman1", pos=(300, 100), scale=(2, 2))
    pygame.display.set_caption("透明示例")

    # 获取 hwnd（pygame 版本不同键名不同）
    info = pygame.display.get_wm_info()
    hwnd = info.get('window') or info.get('hwnd') or None
    if not hwnd:
        print("无法获取 HWND（只在 Windows 上支持）")
        return

    # 首次填充为色键色（洋红），然后绘制内容
    magenta = (255, 0, 255)
    screen.fill(magenta)

    # # 在一个带 alpha 的 surface 上绘制不透明图像，再 blit 到屏幕
    # surf = pygame.Surface((300, 300), pygame.SRCALPHA)
    # pygame.draw.circle(surf, (0, 200, 100, 255), (150,150), 120)  # 不透明圆
    # image = pygame.image.load("assets/stickman1/stand.png")
    # #放大，从30x30到100*100
    # image = pygame.transform.scale(image, (100, 100))
    # screen.blit(surf, (50,50))
    # screen.blit(image, (100,100))
    # pygame.display.update()

    # 把窗口设为分层并启用色键透明
    make_window_colorkey_transparent(hwnd, magenta)

    # 设为置顶；若想取消置顶调用 set_window_always_on_top(hwnd, False)
    set_window_always_on_top(hwnd, True)

    clock = pygame.time.Clock()
    running = True
    while running:
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                running = False
                print("Quitting... (by clicking on the 'x' button)")
            elif e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                print("Quitting... (by pressing Esc)")
                running = False

        # 如果需要动画，每帧重绘（背景要是色键色）
        screen.fill(magenta)
        # screen.fill((0, 0, 0, 0))  # change the color makes window not invisible
        pet.update()
        # print(pet.animation, pet.wanted_animation)
        pet.draw(screen)
        pygame.display.update()

        clock.tick(60)

    pygame.quit()
    # sys.exit()

if __name__ == "__main__":
    try:
        # raise SystemExit(0)  # 临时代码，模拟正常退出
        main()
    except SystemExit as e:
        print("Oh. Someone raised a SystemExit with code", e.code, ". That was not expected. (except exit())")
        exit(e.code)
    except Exception as e:
        import traceback
        print(f"Error occurred: {e}")
        traceback.print_exc()