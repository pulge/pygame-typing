import pygame as pg
import colors as c
import os

class TextBox:
    def __init__(self, x: int, y: int, w: int, max_length: int = 10, center: bool = False, text: str = ''):
        font_path = os.path.join('assets', 'font', 'PressStart2P-Regular.ttf')
        self.FONT = pg.font.Font(font_path, 18)
        self.rect = pg.Rect(x, y, w, 32)
        self.color = c.WHITE
        self.text = text
        self.txt_surface = self.FONT.render(text, True, self.color)
        self.active = True
        self.returned = ''
        self.max_length = max_length
        self.center = center

    def handle_event(self, event: pg.event.EventType) -> None:
        if event.type == pg.MOUSEBUTTONDOWN:
            if self.rect.collidepoint(event.pos):
                self.active = True

        if event.type == pg.KEYDOWN and self.active:
            if event.key == pg.K_RETURN:
                if self.text.strip():  # Only return if not empty
                    self.returned = self.text
                    self.text = ''
            elif event.key == pg.K_BACKSPACE:
                self.text = self.text[:-1]
            elif event.key == pg.K_ESCAPE:
                self.text = ''
            elif len(self.text) < self.max_length:
                self.text += event.unicode

            self.txt_surface = self.FONT.render(self.text, True, self.color)



    def update(self) -> None:
        # Optional: auto-resize if needed
        width = max(200, self.txt_surface.get_width() + 10)
        self.rect.w = width

    def draw(self, screen: pg.Surface) -> None:
        pg.draw.rect(screen, self.color, self.rect, 2)

        # Save current clipping region
        prev_clip = screen.get_clip()
        clip_rect = self.rect.inflate(-10, -10)
        screen.set_clip(clip_rect)

        if self.center:
            text_x = self.rect.x + (self.rect.w - self.txt_surface.get_width()) // 2
        else:
            text_x = self.rect.x + 5

        screen.blit(self.txt_surface, (text_x, self.rect.y + 5))
        screen.set_clip(prev_clip)

    def get_returned(self) -> str:
        return self.returned
