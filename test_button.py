import pygame as pg
import sys
from typing import Tuple, Union


class MyButton:
    """
    Class representing custom button to be drawn in Pygame application.
    """

    ANIMATION_SCALE_FACTOR: float = 0.9
    ANIMATION_TIME: int = 300  # Time in milliseconds

    def __init__(self, text: str, text_color: Tuple[int, int, int],
                 color: Tuple[int, int, int], font: Tuple[Union[str, None], int],
                 min_width: Union[int, None] = None, max_width: Union[int, None] = None,
                 min_height: Union[int, None] = None, max_height: Union[int, None] = None):

        self.text = text
        self.text_color = text_color
        self.color = color
        self.font_name, self.font_size = font

        # Set by draw method
        self.x = 0
        self.y = 0
        self.width = 0
        self.height = 0

        self.min_width = min_width
        self.max_width = max_width
        self.min_height = min_height
        self.max_height = max_height

        # Animation after click
        self.was_clicked: bool = False
        self.current_animation_time: int = 0

    def draw(self, surface: pg.Surface, x: int, y: int, width: int, height: int, time_since_prev_frame: int,
             outline_color: Tuple[int, int, int] = None, outline_width: int = 0) -> None:
        """
        Draws the button on the given surface.

        :param surface: screen/surface for button to be drawn onto
        :param x: top left corner
        :param y: top left corner (the highest the value the lower it gets on the surface)
        :param width:
        :param height:
        :param outline_color: color of outline in RGB values
        :param outline_width: width of button outline in pixels
        :param time_since_prev_frame: time in milliseconds (for animation purposes)
        :return: None
        """

        self.update_size(surface, x, y, width, height, outline_width)

        if self.current_animation_time < MyButton.ANIMATION_TIME:
            self.current_animation_time += time_since_prev_frame
        else:
            self.current_animation_time = 0
            self.was_clicked = False

        animation_scale_factor: float = MyButton.ANIMATION_SCALE_FACTOR if self.was_clicked else 1

        rendered_text = pg.font.Font(self.font_name, int(self.font_size * animation_scale_factor))\
            .render(self.text, True, self.text_color)

        if animation_scale_factor <= 1:  # Making button smaller
            x: int = int(self.x + (self.width - self.width * animation_scale_factor))
            x -= (x - self.x) // 2
            y: int = int(self.y + (self.height - self.height * animation_scale_factor))
            y -= (y - self.y) // 2
            width: int = int(self.width * animation_scale_factor)
            height: int = int(self.height * animation_scale_factor)
        else:  # Making button bigger
            x: int = int(self.x + (self.width - self.width * animation_scale_factor))
            x += (self.x - x) // 2
            y: int = int(self.y + (self.height - self.height * animation_scale_factor))
            y += (self.y - y) // 2
            width: int = int(self.width * animation_scale_factor)
            height: int = int(self.height * animation_scale_factor)

        if outline_color:
            pg.draw.rect(surface, outline_color,
                         (int(x - outline_width // 2 * animation_scale_factor),
                          int(y - outline_width // 2 * animation_scale_factor),
                          width + int(outline_width * animation_scale_factor),
                          height + int(outline_width * animation_scale_factor)))
        pg.draw.rect(surface, self.color, (x, y, width, height))

        if self.text != '':
            surface.blit(rendered_text, ((x + int((width // 2 - rendered_text.get_width() // 2)) - (x - x)),
                                         y + int((height // 2 - rendered_text.get_height() // 2)) - (y - y)))

    def update_size(self, surface: pg.Surface, x: int, y: int, width: int, height: int, outline_width: int) -> None:
        """
        Updates size of a button.

        :param surface:
        :param x: top left corner
        :param y: top left corner (the highest the value the lower it gets on the surface)
        :param width:
        :param height:
        :param outline_width:
        :return: None
        """
        self.x = x
        self.y = y
        if width + x <= surface.get_width():
            self.width = self.min_width if self.min_width is not None and width < self.min_width \
                else self.max_width if self.max_width is not None and width > self.max_width else width
        else:
            self.width = surface.get_width() - x - outline_width

        if height + y <= surface.get_height():
            self.height = self.min_height if self.min_height is not None and height < self.min_height \
                else self.max_height if self.max_height is not None and height > self.max_height else height
        else:
            self.height = surface.get_height() - y - outline_width

    def is_over(self, pos: Tuple[int, int]) -> bool:
        """
        Checks if the given position is inside button.

        :param pos: tuple with coordinates (x, y)
        :return: True if is over
        """
        return True if pg.Rect(self.x, self.y, self.width, self.height).collidepoint(pos[0], pos[1]) else False

    def animate_after_click(self) -> None:
        """
        Creates pop up animation for a button.

        :return: None
        """
        if self.was_clicked:
            self.was_clicked = False
            self.current_animation_time = 0
        self.was_clicked = True


if __name__ == '__main__':

    MIN_SCREEN_WIDTH = MIN_SCREEN_HEIGHT = 400

    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((800, 800), pg.RESIZABLE)

    base_font = (None, 32)
    button = MyButton('Hello', tuple(pg.Color('white')), tuple(pg.Color('red')), base_font, max_width=1000)

    while True:
        for event in pg.event.get():

            mouse_pos = pg.mouse.get_pos()

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if button.is_over(mouse_pos):
                    button.animate_after_click()

            if event.type == pg.VIDEORESIZE:
                width = max(event.w, MIN_SCREEN_WIDTH)
                height = max(event.h, MIN_SCREEN_HEIGHT)
                surface = pg.display.set_mode((width, height), pg.RESIZABLE)

        dt = clock.tick(60)  # Milliseconds since the previous frame

        screen.fill((0, 0, 0))
        button.draw(screen, screen.get_width() // 4, screen.get_height() * 1 / 4, screen.get_width() * 1 / 4,
                    screen.get_height() * 1 / 32, dt, outline_color=(255, 255, 255), outline_width=20)

        pg.display.flip()
