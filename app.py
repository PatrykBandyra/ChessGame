import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame as pg
from collections.abc import Callable
from typing import Tuple, Union, List
from typing_extensions import Literal
from widgets import MyButton, MyInputBox, MyChatBox, MyMessage
from threading import Thread

# CONST SECTION --------------------------------------------------------------------------------------------------------
WINDOW_TITLE: str = 'Chess'
WINDOW_LOGO_PATH: str = 'resources/logo.png'
WINDOW_START_POS_X: int = 275
WINDOW_START_POS_Y: int = 40
WINDOW_START_WIDTH: int = 800
WINDOW_START_HEIGHT: int = 800
FPS: int = 60
STANDARD_FONT: str = 'Times New Roman'

# END CONST SECTION ----------------------------------------------------------------------------------------------------


class App:
    def __init__(self):
        os.environ[
            'SDL_VIDEO_WINDOW_POS'] = f'{WINDOW_START_POS_X},{WINDOW_START_POS_Y}'  # Starting position of PyGame window
        pg.init()
        self.screen: pg.Surface = pg.display.set_mode((WINDOW_START_WIDTH, WINDOW_START_HEIGHT))
        pg.display.set_caption(WINDOW_TITLE)
        pg.display.set_icon(pg.transform.scale(pg.image.load(WINDOW_LOGO_PATH), (32, 32)))
        self.clock: pg.Clock = pg.time.Clock()
        self.dt: int = 0  # Time since last frame

        self.scene: str = 'main_menu'
        self.scene_drawing: dict[str: Callable] = {'main_menu': self.draw_main_menu}
        self.scene_events: dict[str: Callable] = {'main_menu': self.check_events_main_menu}
        self.scene_widgets: dict[str: List[Union[MyButton, MyInputBox, MyChatBox]]] = {key: [] for key in
                                                                                       self.scene_drawing.keys()}
        # self.args_for_function_calls: dict[MyButton: []] = dict()

    @staticmethod
    def quit() -> None:
        pg.quit()
        sys.exit()

    def run(self) -> None:
        self.create_widgets_main_menu()
        while True:
            self.dt = self.clock.tick(FPS)
            self.check_events()
            self.draw()
            self.check_buttons_readiness_for_function_call()

    def check_events(self) -> None:
        """
        Calls proper check_events function based on current scene. Deals with event closing the app.
        """
        for event in pg.event.get():
            mouse_pos = pg.mouse.get_pos()

            if event.type == pg.QUIT:
                App.quit()

            self.scene_events[self.scene](event, mouse_pos)

    # Functions checking events specific to given scene ----------------------------------------------------------------

    def check_events_main_menu(self, event: pg.event.Event, mouse_pos: Tuple[int, int]) -> None:
        if event.type == pg.MOUSEBUTTONDOWN:
            for widget in self.scene_widgets[self.scene]:
                if widget.is_over(mouse_pos):
                    widget.animate_after_click()

    # End of functions checking events ---------------------------------------------------------------------------------

    def draw(self) -> None:
        """
        Calls proper draw function based on current scene.
        """
        self.scene_drawing[self.scene]()
        for widget in self.scene_widgets[self.scene]:
            if isinstance(widget, MyChatBox):
                widget.draw(self.screen)
            else:
                widget.draw(self.screen, self.dt)
        pg.display.flip()

    # Functions drawing specific scenes ---------------------------------------------------------------------------------

    def draw_main_menu(self) -> None:
        """
        Draws main menu scene onto the screen.
        """
        self.screen.fill(pg.Color('gray'))
        self.draw_text('Chess', STANDARD_FONT, 44, pg.Color('black'), 380, 200, align='center')

    # End of functions drawing specific scenes -------------------------------------------------------------------------

    # Functions creating widgets for specific scene --------------------------------------------------------------------

    def create_widgets_main_menu(self) -> None:
        """
        Creates widgets present in main menu scene.
        """
        font = (STANDARD_FONT, 32)
        self.scene_widgets[self.scene].append(MyButton(70, 400, 200, 40, self.on_play_online_button_clicked,
                                                       'PvP via LAN', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       font, outline_color=(255, 255, 255), outline_width=20))
        self.scene_widgets[self.scene].append(MyButton(300, 400, 200, 40, self.on_play_offline_button_clicked,
                                                       'PvP Offline', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       font, outline_color=(255, 255, 255), outline_width=20))
        self.scene_widgets[self.scene].append(MyButton(530, 400, 200, 40, self.on_play_ai_button_clicked,
                                                       'PvAI', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       font, outline_color=(255, 255, 255), outline_width=20))

    # End of functions creating widgets for specific scene -------------------------------------------------------------

    # Functions called after button clicks -----------------------------------------------------------------------------

    def on_play_online_button_clicked(self) -> None:
        pass

    def on_play_offline_button_clicked(self) -> None:
        pass

    def on_play_ai_button_clicked(self) -> None:
        pass

    # End of functions called after button clicks ----------------------------------------------------------------------

    def check_buttons_readiness_for_function_call(self) -> None:
        """
        If the button has finished its animation after being clicked - call the function assigned to it in.
        """
        # Checking if can call function triggered by widget click
        for widget in self.scene_widgets[self.scene]:
            if isinstance(widget, MyButton):
                if not widget.in_animation and widget.was_clicked:
                    thread = Thread(target=widget.call_function([]))
                    thread.start()

    # Helping functions ------------------------------------------------------------------------------------------------

    def draw_text(self, text: str, font_name: str, size: int, color: Union[Tuple[int, int, int], pg.Color],
                  x: int, y: int, align: Literal['n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center'] = 'nw') -> None:
        """
        Draws text on PyGame surface.

        :param text: string to be displayed
        :param font_name: path to font file
        :param size:
        :param color: tuple of RGB values
        :param x:
        :param y:
        :param align: 'n', 'ne', 'e', 'se', 's', 'sw', 'w', 'nw', 'center' - what part of text rectangle x and y
                      values correspond to
        :return: None
        """
        font = pg.font.SysFont(font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        if align == "nw":
            text_rect.topleft = (x, y)
        if align == "ne":
            text_rect.topright = (x, y)
        if align == "sw":
            text_rect.bottomleft = (x, y)
        if align == "se":
            text_rect.bottomright = (x, y)
        if align == "n":
            text_rect.midtop = (x, y)
        if align == "s":
            text_rect.midbottom = (x, y)
        if align == "e":
            text_rect.midright = (x, y)
        if align == "w":
            text_rect.midleft = (x, y)
        if align == "center":
            text_rect.center = (x, y)
        self.screen.blit(text_surface, text_rect)

    # End of helping functions -----------------------------------------------------------------------------------------


def main() -> None:
    app = App()
    app.run()


if __name__ == '__main__':
    main()
