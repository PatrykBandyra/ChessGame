import sys
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame as pg
from collections.abc import Callable
from typing import Tuple, Union, List
from widgets import MyButton, MyInputBox, MyChatBox, MyMessage
from threading import Thread


# CONST SECTION --------------------------------------------------------------------------------------------------------
WINDOW_TITLE: str = 'Chess'
WINDOW_LOGO_PATH: str = 'resources/logo.png'
WINDOW_START_POS_X: int = 275
WINDOW_START_POS_Y: int = 40
WINDOW_START_WIDTH: int = 800
WINDOW_START_HEIGHT: int = 800


# END CONST SECTION ----------------------------------------------------------------------------------------------------


class App:
    def __init__(self):
        os.environ['SDL_VIDEO_WINDOW_POS'] = f'{WINDOW_START_POS_X},{WINDOW_START_POS_Y}'  # Starting position of PyGame window
        pg.init()
        self.screen: pg.Surface = pg.display.set_mode((WINDOW_START_WIDTH, WINDOW_START_HEIGHT))
        pg.display.set_caption(WINDOW_TITLE)
        pg.display.set_icon(pg.transform.scale(pg.image.load(WINDOW_LOGO_PATH), (32, 32)))
        self.clock: pg.Clock = pg.time.Clock()

        self.scene: str = 'main_menu'
        self.scene_drawing: dict[str: Callable] = {'main_menu': self.draw_main_menu}
        self.scene_events: dict[str: Callable] = {'main_menu': self.check_events_main_menu}
        self.scene_widgets: dict[str: List[Union[MyButton, MyInputBox, MyChatBox]]] = {key: [] for key in self.scene_drawing.keys()}
        self.args_for_function_calls: dict[MyButton: []] = dict()

    @staticmethod
    def quit() -> None:
        pg.quit()
        sys.exit()

    def run(self) -> None:
        pass

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

    # Function drawing specific scenes ---------------------------------------------------------------------------------

    def draw_main_menu(self) -> None:
        """
        Draws main menu scene onto the screen.
        """
        self.screen.fill(pg.Color('gray'))

    # End of functions drawing specific scenes -------------------------------------------------------------------------

    def create_widgets_main_menu(self) -> None:
        """
        Creates widgets present in main menu scene.
        """
        # 3 buttons
        pass

    def check_buttons_readiness_for_function_call(self) -> None:
        """
        If the button has finished its animation after being clicked - call the function assigned to it in.
        """
        # Checking if can call function triggered by widget click
        for widget in self.scene_widgets[self.scene]:
            if isinstance(widget, MyButton):
                if not widget.in_animation and widget.was_clicked:
                    thread = Thread(target=widget.call_function(self.args_for_function_calls[widget]))
                    thread.start()


def main() -> None:
    app = App()


if __name__ == '__main__':
    main()