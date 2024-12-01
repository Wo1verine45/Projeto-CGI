import pygame
import sys

# Inicializa o Pygame
pygame.init()

# Configurações da janela
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Meu Primeiro Jogo 2D")

# Cores
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Loop principal do jogo
clock = pygame.time.Clock()

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # Atualiza a tela
    screen.fill(BLACK)  # Cor de fundo
    pygame.display.flip()

    # Controle de FPS
    clock.tick(60)
