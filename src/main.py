# main.py
import pygame


def main() -> None:
    pygame.init()

    surface = pygame.display.set_mode((400, 300))
    color = (255, 0, 255)

    run = True
    while run:
        for event in pygame.event.get():

            if event.type == pygame.QUIT:
                run = False

        pygame.draw.rect(surface, color, pygame.Rect(30, 30, 60, 60))
        pygame.display.flip()

    pygame.quit()


if __name__ == "__main__":
    main()
