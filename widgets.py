import sys
import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
from collections.abc import Callable
from typing import Tuple, Union, List
import pygame as pg
from threading import Thread

"""
This file contains my custom widgets for PyGame application.
"""


class MyWidget:
    """
    Base class for my custom widgets.
    """

    def __init__(self):
        # Set by draw method
        self.x: int = 0
        self.y: int = 0
        self.width: int = 0
        self.height: int = 0

    def update_size(self, x: int, y: int, width: int, height: int) -> None:
        """
        Updates size of a button.

        :param x: top left corner
        :param y: top left corner (the highest the value the lower it gets on the surface)
        :param width:
        :param height:
        :return: None
        """
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def is_over(self, pos: Tuple[int, int]) -> bool:
        """
        Checks if the given position is inside button.

        :param pos: tuple with coordinates (x, y)
        :return: True if is over
        """
        return True if pg.Rect(self.x, self.y, self.width, self.height).collidepoint(pos[0], pos[1]) else False


class MyButton(MyWidget):
    """
    Class representing custom button to be drawn in Pygame application. It has default animation that
    can be triggered after the click.

    Usage order:
    1. Main loop: Detect if button was clicked - check event and if mouse position is over the button by calling is_over()
    2. If clicked - call animate_after_click()
    3. Main loop: draw the button by calling draw()
    4. Main loop (end): check if animation was finished and button was clicked - if yes, then call call_function()
    """

    ANIMATION_SCALE_FACTOR: float = 0.9
    ANIMATION_TIME: int = 300  # Time in milliseconds

    def __init__(self, function: Callable, text: str, text_color: Union[Tuple[int, int, int], pg.Color],
                 color: Union[Tuple[int, int, int], pg.Color],
                 font: Tuple[Union[str, None], int]):

        super().__init__()
        self.function = function
        self.text = text
        self.text_color = text_color
        self.color = color
        self.font_name, self.font_size = font

        # Animation after click
        self.was_clicked: bool = False
        self.current_animation_time: int = 0
        self.in_animation: bool = False

    def draw(self, surface: pg.Surface, x: int, y: int, width: int, height: int, time_since_prev_frame: int,
             outline_color: Union[Tuple[int, int, int], pg.Color] = None, outline_width: int = 0) -> None:
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

        self.update_size(x, y, width, height)

        if self.current_animation_time < MyButton.ANIMATION_TIME:
            self.current_animation_time += time_since_prev_frame
        else:
            self.current_animation_time = 0
            self.in_animation = False

        animation_scale_factor: float = MyButton.ANIMATION_SCALE_FACTOR if self.was_clicked else 1

        text_surface = pg.font.Font(self.font_name, int(self.font_size * animation_scale_factor)) \
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
            surface.blit(text_surface, ((x + int((width // 2 - text_surface.get_width() // 2)) - (x - x)),
                                        y + int((height // 2 - text_surface.get_height() // 2)) - (y - y)))

    def animate_after_click(self) -> None:
        """
        Creates pop up animation for a button.

        :return: None
        """
        if self.was_clicked:
            self.was_clicked = False
            self.current_animation_time = 0
        self.was_clicked = True
        self.in_animation = True

    def call_function(self, args) -> None:
        """
        Calls function that was passed as argument in __init__ method.

        :return: None
        """
        self.was_clicked = False
        self.function(*args)


class MyInputBox(MyWidget):
    """
    Class representing custom input box.
    """

    ANIMATION_TIME: int = 500  # Time in milliseconds
    DIST_TEXT_CURSOR = 10
    DIST_CURSOR_FIELD_END = 8
    DIST_CURSOR_FIELD_TOP = 4
    MAX_LETTER_WIDTH = 20  # In pixels

    def __init__(self, text_color: Union[Tuple[int, int, int], pg.Color],
                 color_active: Union[Tuple[int, int, int], pg.Color],
                 color_passive: Union[Tuple[int, int, int], pg.Color], font: Tuple[Union[str, None], int],
                 outline_width: int, text: str = '', min_width: int = 100, max_width: int = 200, cursor_width: int = 2,
                 cursor_color: Union[Tuple[int, int, int], pg.Color] = pg.Color('white')):
        super().__init__()
        self.text = text
        self.visible_text: str = text
        self.text_color = text_color
        self.color_active = color_active
        self.color_passive = color_passive
        self.font_name, self.font_size = font
        self.outline_width = outline_width
        self.min_width = min_width
        self.max_width = max_width
        self.cursor_width = cursor_width
        self.cursor_color = cursor_color

        self.active: bool = False
        self.current_animation_time: int = 0
        self.show_cursor: bool = True
        self.deleting: bool = False

    def draw(self, surface: pg.Surface, x: int, y: int, width: int, height: int, time_since_prev_frame: int) -> None:
        """
        Draws input box with entered text onto the screen.

        :param surface:
        :param x: top left corner
        :param y: top left corner (the highest the value the lower it gets on the surface)
        :param width:
        :param height:
        :param time_since_prev_frame: time in milliseconds (for animation purposes)
        :return: None
        """
        self.update_size(x, y, width, height)

        color = self.color_active if self.active else self.color_passive
        font = pg.font.Font(self.font_name, self.font_size)
        visible_text_surface = font.render(self.visible_text, True, self.text_color)

        # Update width to accommodate more letters
        dist = MyInputBox.DIST_TEXT_CURSOR + self.cursor_width + MyInputBox.DIST_CURSOR_FIELD_END
        visible_text_width = visible_text_surface.get_width()
        self.width = min(max(self.min_width, visible_text_width + dist), self.max_width)

        if self.width == self.max_width:
            self.visible_text = self.visible_text[1:]
        elif self.deleting and self.width == self.min_width:
            try:
                self.deleting = False
                num = self.width // MyInputBox.MAX_LETTER_WIDTH
                self.visible_text = self.text[-num:]
            except IndexError:
                pass

        pg.draw.rect(surface, color, (self.x, self.y, self.width, self.height), self.outline_width)
        surface.blit(visible_text_surface, (self.x + 5, self.y + 5))

        # Draw cursor
        if self.active:
            font_width, font_height = font.size(self.visible_text)
            x = self.x + font_width + MyInputBox.DIST_TEXT_CURSOR
            y = self.y + MyInputBox.DIST_CURSOR_FIELD_TOP
            self.draw_cursor(surface, x, y, font_height, time_since_prev_frame)

        # Remember to flip the screen at the end of main loop

    def draw_cursor(self, surface: pg.Surface, x: int, y: int, height: int, time_since_prev_frame: int) -> None:
        """
        Draws the cursor in the input field if active. Animates the cursor.

        :param surface:
        :param x: top left corner
        :param y: top left corner (the highest the value the lower it gets on the surface):param y:
        :param height:
        :param time_since_prev_frame: time in milliseconds (for animation purposes)
        :return: None
        """

        if self.show_cursor and self.current_animation_time < MyInputBox.ANIMATION_TIME:
            self.current_animation_time += time_since_prev_frame
            pg.draw.rect(surface, self.cursor_color, (x, y, self.cursor_width, height))
        elif not self.show_cursor and self.current_animation_time < MyInputBox.ANIMATION_TIME:
            self.current_animation_time += time_since_prev_frame
        else:
            self.current_animation_time = 0
            self.show_cursor = not self.show_cursor

    def add_letter(self, event: pg.event.Event) -> None:
        self.text += event.unicode
        self.visible_text += event.unicode

    def remove_letter(self) -> None:
        self.deleting = True
        self.text = self.text[:-1]
        self.visible_text = self.visible_text[:-1]

    def animate_after_click(self) -> None:
        """
        Causes the change of color of the outline.

        :return: None
        """
        self.active = True

    def deactivate(self) -> None:
        """
        Deactivates the input box.

        :return: None
        """
        self.active = False


class MyMessage:
    """
    Class representing custom messages that shall be stored in MyChatBox object.
    """

    DEFAULT_FONT: Tuple[Union[str, None], int] = (None, 24)
    DEFAULT_TEXT_COLOR: Union[Tuple[int, int, int], pg.Color] = pg.Color('white')
    DISTANCE_BETWEEN_TEXT_LINES: int = 4  # In pixels

    def __init__(self, text: str, author: str, font: Tuple[Union[str, None], int] = DEFAULT_FONT,
                 text_color: Union[Tuple[int, int, int], pg.Color] = DEFAULT_TEXT_COLOR):
        self.text = text
        self.author = author
        self.font_name, self.font_size = font
        self.text_color = text_color
        self.message: List[str] = list()  # Message split into lines
        self.text_height: int = 0
        self.is_prepared: bool = False

    def draw(self, surface: pg.Surface, x: int, y: int, max_height: int) -> Tuple[bool, int, int]:
        """
        Draws message on a given surface.

        :param surface:
        :param x:
        :param y:
        :param max_height:
        :return: Tuple: first value tells if there was enough space and message was drawn onto the surface;
        Second value tells how much vertical space left. Third value tells how much height was used.
        """
        # Check if there is enough space for drawing
        lines = len(self.message)
        needed_height = lines * self.text_height + lines * MyMessage.DISTANCE_BETWEEN_TEXT_LINES
        if needed_height > max_height - MyChatBox.PADDING_Y:
            return False, max_height, 0
        else:
            font = pg.font.Font(self.font_name, self.font_size)
            additional_y = 0
            for line in self.message:
                text_surface = font.render(line, True, self.text_color)
                surface.blit(text_surface, (x, y + additional_y))
                additional_y += self.text_height + MyMessage.DISTANCE_BETWEEN_TEXT_LINES
            return True, max_height - additional_y, additional_y

        # Remember to flip the screen at the end of main loop

    def prepare_message(self, max_width: int) -> None:
        """
        Prepares message separating it into lines if needed.

        :param max_width: max width of line in pixels
        :return: None
        """
        font = pg.font.Font(self.font_name, self.font_size)
        message = f'{self.author}: {self.text}'
        text_surface = font.render(message, True, self.text_color)
        text_total_width, self.text_height = text_surface.get_size()

        if text_total_width < max_width - MyChatBox.PADDING_X:
            self.message.append(message)  # One-liner
        else:
            current_line = ''
            for word in message.split():
                if font.render(current_line + word, False,
                               self.text_color).get_width() < max_width - MyChatBox.PADDING_X:
                    current_line += f'{word} '
                else:
                    self.message.append(current_line)
                    current_line = f'{word} '
            self.message.append(current_line)
        self.is_prepared = True


class MyChatBox:
    PADDING_X: int = 5
    PADDING_Y: int = 5

    def __init__(self, outline_width: int = 2,
                 outline_color: Union[Tuple[int, int, int], pg.Color] = pg.Color('white')):
        self.messages: List[MyMessage] = list()
        self.outline_width = outline_width
        self.outline_color = outline_color

    def draw(self, surface: pg.Surface, x: int, y: int, width: int, height: int) -> None:
        # Draw outline
        pg.draw.rect(surface, self.outline_color, (x, y, width, height), self.outline_width)

        available_height = height - 2 * MyChatBox.PADDING_Y
        additional_height = 0
        for message in self.messages:
            was_drawn, available_height, used_height = message.draw(surface, x + MyChatBox.PADDING_X,
                                                                          y + MyChatBox.PADDING_Y + additional_height,
                                                                          available_height)
            additional_height += used_height

            if not was_drawn:
                self.messages.pop(0)
                break

    def add_message(self, message: MyMessage) -> None:
        self.messages.append(message)


def on_add_button_clicked(chat_box: MyChatBox, input_box: MyInputBox):
    message = MyMessage(input_box.text, 'Ja')
    message.prepare_message(200)
    chat_box.add_message(message)


def change_color(widget):
    widget.color = pg.Color('blue')


if __name__ == '__main__':

    MIN_SCREEN_WIDTH = MIN_SCREEN_HEIGHT = 400

    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((800, 800))

    base_font = (None, 32)
    button = MyButton(change_color, 'Hello', tuple(pg.Color('white')), tuple(pg.Color('red')), base_font)
    button2 = MyButton(on_add_button_clicked, 'Welcome', tuple(pg.Color('white')), tuple(pg.Color('red')), base_font)
    input_box = MyInputBox(pg.Color('white'), pg.Color('lightskyblue3'), pg.Color('gray15'), (None, 32), 4)

    chat_box = MyChatBox()
    msg1 = MyMessage('Hello World', 'Patryk')
    msg1.prepare_message(200)
    chat_box.add_message(msg1)
    msg2 = MyMessage(
        'I really enjoy beating the hell out of my sons in order for them to be more resistant to physical and mental pain. I am good father lol',
        'Greg')
    msg2.prepare_message(200)
    chat_box.add_message(msg2)
    msg3 = MyMessage('Hejka', 'Adam')
    msg3.prepare_message(200)
    chat_box.add_message(msg3)

    widgets = [button, button2, input_box]
    args_for_function_calls = {key: [] for key in widgets if isinstance(key, MyButton)}

    args_for_function_calls[button] = [button]
    args_for_function_calls[button2] = [chat_box, input_box]

    while True:
        for event in pg.event.get():

            mouse_pos = pg.mouse.get_pos()

            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            # MOUSE EVENTS
            if event.type == pg.MOUSEBUTTONDOWN:
                if event.button == 3:
                    print(f'Visible: {input_box.visible_text}')
                elif event.button == 2:
                    print(f'Text: {input_box.text}')
                    pg.display.set_mode((400, 400))
                for widget in widgets:
                    if widget.is_over(mouse_pos):
                        widget.animate_after_click()
                    else:
                        if isinstance(widget, MyInputBox):
                            widget.deactivate()

            # KEYBOARD EVENTS
            if event.type == pg.KEYDOWN:
                for widget in widgets:
                    if isinstance(widget, MyInputBox):
                        if widget.active:
                            if event.key == pg.K_BACKSPACE:
                                widget.remove_letter()
                            else:
                                widget.add_letter(event)

        dt = clock.tick(60)  # Milliseconds since the previous frame

        # Drawing
        screen.fill((0, 0, 0))
        button.draw(screen, screen.get_width() // 4, int(screen.get_height() * 1 / 4), int(screen.get_width() * 1 / 4),
                    int(screen.get_height() * 1 / 32), dt, outline_color=(255, 255, 255), outline_width=20)
        button2.draw(screen, int(screen.get_width() * 3 / 4), int(screen.get_height() * 3 / 4),
                     int(screen.get_width() * 1 / 8),
                     int(screen.get_height() * 1 / 32), dt)

        input_box.draw(screen, 200, 600, 140, 32, dt)
        chat_box.draw(screen, 400, 400, 200, 300)

        pg.display.flip()

        # Getting args for function calls
        # TODO: for example getting input from input box

        # Checking if can call function triggered by widget click
        for widget in widgets:
            if isinstance(widget, MyButton):
                if not widget.in_animation and widget.was_clicked:
                    thread = Thread(target=widget.call_function(args_for_function_calls[widget]))
                    thread.start()
