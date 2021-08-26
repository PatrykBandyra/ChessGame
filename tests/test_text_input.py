import pygame as pg
import sys


if __name__ == '__main__':
    pg.init()
    clock = pg.time.Clock()
    screen = pg.display.set_mode((800, 800))
    base_font = pg.font.Font(None, 32)
    user_text = ''

    input_rect = pg.Rect(200, 200, 140, 32)
    color_active = pg.Color('lightskyblue3')
    color_passive = pg.Color('gray15')
    color = color_passive

    active = False

    while True:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                pg.quit()
                sys.exit()

            if event.type == pg.MOUSEBUTTONDOWN:
                if input_rect.collidepoint(event.pos):
                    active = True
                else:
                    active = False

            if event.type == pg.KEYDOWN:
                if active:
                    if event.key == pg.K_BACKSPACE:
                        user_text = user_text[:-1]
                    else:
                        user_text += event.unicode

        screen.fill((0, 0, 0))

        if active:
            color = color_active
        else:
            color = color_passive

        pg.draw.rect(screen, color, input_rect, 2)

        text_surface = base_font.render(user_text, True, (255, 255, 255))
        screen.blit(text_surface, (input_rect.x + 5, input_rect.y + 5))

        input_rect.w = max(200, text_surface.get_width() + 10)

        pg.display.flip()
        clock.tick()
