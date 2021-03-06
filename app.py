import sys
import os
import threading

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame as pg
from collections.abc import Callable
from typing import Tuple, Union, List, Iterable
from typing_extensions import Literal
from widgets import MyButton, MyInputBox, MyChatBox, MyMessage, MyLobbyBox, MyPlayerWidget
from player import Player
from threading import Thread
from collections import Counter

"""
Main file containing entry point of the application. Responsible for GUI functionalities.
"""

# CONST SECTION --------------------------------------------------------------------------------------------------------
WINDOW_TITLE: str = 'Chess'
WINDOW_LOGO_PATH: str = 'resources/logo.png'
WINDOW_START_POS_X: int = 375
WINDOW_START_POS_Y: int = 40
WINDOW_START_WIDTH: int = 800
WINDOW_START_HEIGHT: int = 600
FPS: int = 30
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
        self.scene_drawing: dict[str: Callable] = {'main_menu': self.draw_main_menu,
                                                   'enter_name_menu': self.draw_enter_name_menu,
                                                   'lobby_menu': self.draw_lobby_menu}
        self.scene_events: dict[str: Callable] = {'main_menu': self.check_events_main_menu,
                                                  'enter_name_menu': self.check_events_enter_name_menu,
                                                  'lobby_menu': self.check_events_lobby_menu}
        self.scene_widgets: dict[str: List[Union[MyButton, MyInputBox, MyChatBox]]] = {key: [] for key in
                                                                                       self.scene_drawing.keys()}
        self.scene_assets: dict[str: List] = {key: [] for key in self.scene_drawing.keys()}

        self.banner: pg.Surface = pg.Surface((WINDOW_START_WIDTH, WINDOW_START_HEIGHT))
        self.banner.fill((30, 30, 30))
        self.do_render_banner: bool = False
        self.banner_text: str = ''
        self.display_error_info: bool = False
        self.lobby_full: bool = False
        self.name_in_use: bool = False

        self.chat_box: Union[MyChatBox, None] = None  # If there is a chat box in a scene - assign reference
        self.player: Union[Player, None] = None   # Player instance will be created while joining lobby
        self.lobby_box: Union[MyLobbyBox, None] = None  # If there is a lobby box in a scene - assign reference

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
                self.close_connections()
                App.quit()

            self.scene_events[self.scene](event, mouse_pos)

    def check_events_disabled(self, event: pg.event.Event, mouse_pos: Tuple[int, int]) -> None:
        """
        Call this function to not check events in a specific scene.
        """
        pass

    # Functions checking events specific to given scene ----------------------------------------------------------------

    def check_events_main_menu(self, event: pg.event.Event, mouse_pos: Tuple[int, int]) -> None:
        if event.type == pg.MOUSEBUTTONDOWN:
            for widget in self.scene_widgets[self.scene]:
                if widget.is_over(mouse_pos):
                    widget.animate_after_click()

    def check_events_enter_name_menu(self, event: pg.event.Event, mouse_pos: Tuple[int, int]) -> None:
        if event.type == pg.MOUSEBUTTONDOWN:
            for widget in self.scene_widgets[self.scene]:
                if widget.is_over(mouse_pos):
                    widget.animate_after_click()
                else:
                    if isinstance(widget, MyInputBox):
                        widget.deactivate()

        if event.type == pg.KEYDOWN:
            for widget in self.scene_widgets[self.scene]:
                if isinstance(widget, MyInputBox):
                    if widget.active:
                        if event.key == pg.K_BACKSPACE:
                            widget.remove_letter()
                        else:
                            widget.add_letter(event)

    def check_events_lobby_menu(self, event: pg.event.Event, mouse_pos: Tuple[int, int]) -> None:
        if event.type == pg.MOUSEBUTTONDOWN:
            for widget in self.scene_widgets[self.scene]:
                if isinstance(widget, MyLobbyBox):
                    player_widget = widget.if_over_return_player_widget(mouse_pos)
                    if player_widget is not None:
                        button = player_widget.if_over_return_button(mouse_pos)
                        if button is not None:
                            button.animate_after_click()
                else:
                    if not isinstance(widget, MyChatBox):
                        if widget.is_over(mouse_pos):
                            widget.animate_after_click()
                        else:
                            if isinstance(widget, MyInputBox):
                                widget.deactivate()

        if event.type == pg.KEYDOWN:
            for widget in self.scene_widgets[self.scene]:
                if isinstance(widget, MyInputBox):
                    if widget.active:
                        if event.key == pg.K_BACKSPACE:
                            widget.remove_letter()
                        else:
                            widget.add_letter(event)

        self.check_server_events()

    def check_server_events(self):
        if not self.player.received_message_queue.empty():
            message = self.player.received_message_queue.get()
            message_widget = MyMessage(message['text'], message['author'])
            message_widget.prepare_message(350)
            self.chat_box.add_message(message_widget)

        # Lobby Players
        if not App.compare_two_iterables(self.player.lobby_names, self.lobby_box.player_names):
            if len(self.player.lobby_names) > len(self.lobby_box.player_names):  # Player has entered the lobby
                for name in self.player.lobby_names:
                    if name not in self.lobby_box.player_names:
                        if name == self.player.name:
                            self.lobby_box.add_player_widget(name, self.on_accept_button_clicked, self.on_invite_button_clicked, add_buttons=False, my_player=True)
                        else:
                            self.lobby_box.add_player_widget(name, self.on_accept_button_clicked, self.on_invite_button_clicked)
            else:  # Player has quited
                for name in self.lobby_box.player_names:
                    if name not in self.player.lobby_names:
                        self.lobby_box.remove_player_widget(name)

        # Connection error in lobby
        if not self.player.connected:
            # Close lobby
            self.display_error_info = True
            self.on_return_from_lobby_menu_clicked()

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
        if self.do_render_banner:
            self.render_banner()
        pg.display.flip()

    # Functions drawing specific scenes ---------------------------------------------------------------------------------

    def draw_main_menu(self) -> None:
        """
        Draws main menu scene onto the screen.
        """
        self.screen.fill(pg.Color('gray'))
        self.draw_text('Chess', STANDARD_FONT, 44, pg.Color('black'), 400, 250, align='center')
        self.draw_text('by Patryk Bandyra', STANDARD_FONT, 16, pg.Color('white'), 470, 280, align='center')
        self.screen.blit(self.scene_assets[self.scene][0],
                         (self.screen.get_width()//2 - self.scene_assets[self.scene][0].get_width()//2, 50))

    def draw_enter_name_menu(self) -> None:
        self.screen.fill(pg.Color('gray'))
        self.draw_text('Enter your name', STANDARD_FONT, 44, pg.Color('black'), 400, 150, align='center')
        self.draw_text('Maximum 20 characters', STANDARD_FONT, 16, pg.Color('black'), 100, 230, align='w')
        chars: int = 0
        for widget in self.scene_widgets['enter_name_menu']:
            if isinstance(widget, MyInputBox):
                chars = widget.char_counter
        self.draw_text(f'Characters: {chars}', STANDARD_FONT, 16, pg.Color('black'), 620, 320, align='w')
        if self.display_error_info:
            self.draw_text('Connection error', STANDARD_FONT, 22, pg.Color('red'), 400, 100, align='center')
        elif self.lobby_full:
            self.draw_text('Lobby is full', STANDARD_FONT, 22, pg.Color('red'), 400, 100, align='center')
        elif self.name_in_use:
            self.draw_text('Name already in use in the lobby - choose other', STANDARD_FONT, 22, pg.Color('red'), 400, 100, align='center')

    def draw_lobby_menu(self) -> None:
        self.screen.fill(pg.Color('gray'))
        self.draw_text('Lobby Chat', STANDARD_FONT, 14, pg.Color('black'), 200, 10, align='center')
        self.draw_text(f'Lobby Players {len(self.lobby_box.player_widgets) if self.lobby_box is not None else 0}/6',
                       STANDARD_FONT, 14, pg.Color('black'), 600, 10, align='center')

    # End of functions drawing specific scenes -------------------------------------------------------------------------

    # Functions creating widgets for specific scene --------------------------------------------------------------------

    def create_widgets_main_menu(self) -> None:
        """
        Creates widgets present in main menu scene. Loads needed assets like images.
        """
        font = (STANDARD_FONT, 32)
        scene_name = 'main_menu'
        self.scene_widgets[scene_name].append(MyButton(50, 400, 200, 40, self.on_play_online_button_clicked,
                                                       'PvP via LAN', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       font, outline_color=pg.Color('white'), outline_width=20))
        self.scene_widgets[scene_name].append(MyButton(300, 400, 200, 40, self.on_play_offline_button_clicked,
                                                       'PvP Offline', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       font, outline_color=pg.Color('white'), outline_width=20))
        self.scene_widgets[scene_name].append(MyButton(550, 400, 200, 40, self.on_play_ai_button_clicked,
                                                       'PvAI', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       font, outline_color=pg.Color('white'), outline_width=20))
        self.scene_assets[scene_name].append(pg.image.load('resources/logo.png'))

    def create_widgets_enter_name_menu(self) -> None:
        font = (STANDARD_FONT, 32)
        small_font = (STANDARD_FONT, 18)
        scene_name = 'enter_name_menu'  # self.scene shall be changed after creating widgets
        self.scene_widgets[scene_name].append(MyButton(350, 400, 100, 40, self.on_enter_name_clicked,
                                                       'OK', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       font, outline_color=(255, 255, 255), outline_width=20))
        self.scene_widgets[scene_name].append(MyInputBox(100, 250, 600, 46, pg.Color('white'),
                                                         pg.Color('lightskyblue3'), pg.Color('gray15'),
                                                         font, 4, max_chars=20))
        self.scene_widgets[scene_name].append(MyButton(685, 545, 100, 40, self.on_return_from_enter_name_clicked,
                                                       'Return', tuple(pg.Color('white')), tuple(pg.Color('black')),
                                                       font, outline_color=pg.Color('white'), outline_width=20))
        self.scene_widgets[scene_name].append(MyButton(720, 257, 50, 32, self.on_clear_input_box_clicked,
                                                       'Clear', tuple(pg.Color('red')), tuple(pg.Color('dark gray')),
                                                       small_font, outline_color=pg.Color('red'), outline_width=10))

    def create_widgets_lobby_menu(self) -> None:
        scene_name = 'lobby_menu'
        self.chat_box = MyChatBox(10, 20, 400, 500)
        self.scene_widgets[scene_name].append(self.chat_box)
        self.scene_widgets[scene_name].append(MyInputBox(10, 530, 330, 36, pg.Color('white'),
                                                         pg.Color('lightskyblue3'), pg.Color('gray15'),
                                                         (STANDARD_FONT, 24), 4, max_chars=80))
        self.scene_widgets[scene_name].append(MyButton(355, 534, 50, 28, self.on_clear_input_box_clicked,
                                                       'Clear', tuple(pg.Color('red')), tuple(pg.Color('dark gray')),
                                                       (STANDARD_FONT, 18), outline_color=pg.Color('red'),
                                                       outline_width=10))
        self.scene_widgets[scene_name].append(MyButton(80, 572, 200, 24, self.on_send_message_button_clicked,
                                                       'Send', tuple(pg.Color('white')), tuple(pg.Color('dark gray')),
                                                       (STANDARD_FONT, 18), outline_color=pg.Color('white'),
                                                       outline_width=2))
        self.scene_widgets[scene_name].append(MyButton(685, 545, 100, 40, self.on_return_from_lobby_menu_clicked,
                                                       'Return', tuple(pg.Color('white')), tuple(pg.Color('black')),
                                                       (STANDARD_FONT, 32), outline_color=pg.Color('white'),
                                                       outline_width=20))
        self.lobby_box = MyLobbyBox(420, 20, 370, 500)
        self.scene_widgets[scene_name].append(self.lobby_box)

    # End of functions creating widgets for specific scene -------------------------------------------------------------

    # Functions called after button clicks -----------------------------------------------------------------------------
    # Main Menu ********************************************************************************************************
    def on_play_online_button_clicked(self) -> None:
        self.scene_widgets[self.scene].clear()  # Delete widgets of previous menu
        self.create_widgets_enter_name_menu()
        self.scene = 'enter_name_menu'

    def on_play_offline_button_clicked(self) -> None:
        pass

    def on_play_ai_button_clicked(self) -> None:
        pass

    # End of Main Menu *************************************************************************************************
    # Enter Name Menu **************************************************************************************************

    def on_enter_name_clicked(self) -> None:
        # 1. Start new thread to connect to the server
        # 2. Meanwhile display banner - "Connecting to server..."

        self.lobby_full = False
        self.display_error_info = False
        self.name_in_use = False

        self.do_render_banner = True
        self.banner_text = 'Connecting...'
        self.scene_events[self.scene] = self.check_events_disabled

        name = ''
        for widget in self.scene_widgets[self.scene]:
            if isinstance(widget, MyInputBox):
                name = widget.text.strip()

        lobby_connection_thread = threading.Thread(target=self.connect_to_lobby, args=[name])
        lobby_connection_thread.start()

    def connect_to_lobby(self, name: str):
        self.player = Player(name)
        self.scene_events[self.scene] = self.check_events_enter_name_menu
        self.do_render_banner = False
        if self.player.connected:
            self.display_error_info = False
            self.lobby_full = False
            self.scene_widgets[self.scene].clear()
            self.create_widgets_lobby_menu()
            self.scene = 'lobby_menu'
            receive_thread = threading.Thread(target=self.player.receive)
            send_thread = threading.Thread(target=self.player.send)
            receive_thread.start()
            send_thread.start()
        else:
            if self.player.lobby_full:
                self.lobby_full = True
            elif self.player.name_in_use:
                self.name_in_use = True
            else:
                self.display_error_info = True
            self.player = None

    def on_return_from_enter_name_clicked(self) -> None:
        self.display_error_info = False
        self.lobby_full = False
        self.name_in_use = False
        self.scene_widgets[self.scene].clear()
        self.create_widgets_main_menu()
        self.scene = 'main_menu'

    # Used as well in lobby menu
    def on_clear_input_box_clicked(self) -> None:
        for widget in self.scene_widgets[self.scene]:
            if isinstance(widget, MyInputBox):
                widget.text = ''
                widget.visible_text = ''
                widget.char_counter = 0

    # End of Enter Name Menu *******************************************************************************************
    # Lobby Menu *******************************************************************************************************

    def on_send_message_button_clicked(self) -> None:
        message = ''
        for widget in self.scene_widgets[self.scene]:
            if isinstance(widget, MyInputBox):
                message = widget.text
        if message != '':
            self.player.message_to_send = message

    def on_return_from_lobby_menu_clicked(self) -> None:
        self.close_connections()
        self.scene_widgets[self.scene].clear()
        self.create_widgets_enter_name_menu()
        self.scene = 'enter_name_menu'

    def on_accept_button_clicked(self) -> None:
        pass

    def on_invite_button_clicked(self) -> None:
        pass

    # End of Lobby Menu
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

        if self.lobby_box is not None:
            for widget in self.lobby_box.player_widgets:
                if not widget.invite_button.in_animation and widget.invite_button.was_clicked:
                    thread = Thread(target=widget.invite_button.call_function([]))
                    thread.start()

                elif not widget.accept_button.in_animation and widget.accept_button.was_clicked:
                    thread = Thread(target=widget.accept_button.call_function([]))
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

    def render_banner(self):
        self.banner.fill((30, 30, 30))
        self.screen.blit(self.banner, (0, 0), special_flags=pg.BLEND_MULT)
        self.draw_text(self.banner_text, STANDARD_FONT, 44, pg.Color('red'), 400, 300, align='center')

    @staticmethod
    def compare_two_iterables(one: Iterable, two: Iterable):
        return Counter(one) == Counter(two)

    def close_connections(self):
        if self.player is not None:
            self.player.stop_thread = True
            self.player.connected = False
            self.player.client.close()
            self.player = None

    # End of helping functions -----------------------------------------------------------------------------------------


def main() -> None:
    app = App()
    app.run()


if __name__ == '__main__':
    main()