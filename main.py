import pygame
import sys
import random

# Inicializa o Pygame
pygame.init()

# Configurações principais
SCREEN_WIDTH, SCREEN_HEIGHT = 800, 600
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
CLOCK = pygame.time.Clock()
FPS = 60

# Cores
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
RED = (255, 0, 0)

# Tamanho dos tiles
TILE_SIZE = 40

# Jogador
player = {"x": 1, "y": 1}

# Inimigos
enemies = [{"x": 5, "y": 5}]

# Funções do Labirinto
def generate_maze(width, height):
    maze = [[1 for _ in range(width)] for _ in range(height)]

    def carve_path(x, y):
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]
        random.shuffle(directions)
        for dx, dy in directions:
            nx, ny = x + dx * 2, y + dy * 2
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and maze[ny][nx] == 1:
                maze[y + dy][x + dx] = 0
                maze[ny][nx] = 0
                carve_path(nx, ny)

    # Define início e saída
    maze[1][1] = 0  # Início
    maze[height - 2][width - 2] = 2  # Saída

    # Gera o labirinto com caminho garantido
    carve_path(1, 1)

    # Garante conexão entre o início e a saída
    path = [(1, 1)]
    visited = set(path)

    while path:
        x, y = path.pop()
        if (x, y) == (width - 2, height - 2):
            break
        for dx, dy in [(0, 1), (1, 0), (0, -1), (-1, 0)]:
            nx, ny = x + dx, y + dy
            if 1 <= nx < width - 1 and 1 <= ny < height - 1 and (nx, ny) not in visited and maze[ny][nx] != 1:
                visited.add((nx, ny))
                path.append((nx, ny))

    return maze

def draw_maze(maze):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            color = WHITE if cell == 0 else BLACK
            if cell == 2:
                color = GREEN  # Saída em verde
            pygame.draw.rect(SCREEN, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Funções do Jogador
def draw_player():
    pygame.draw.rect(SCREEN, BLUE, (player["x"] * TILE_SIZE, player["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def move_player(maze, dx, dy):
    new_x = player["x"] + dx
    new_y = player["y"] + dy
    if maze[new_y][new_x] == 0 or maze[new_y][new_x] == 2:
        player["x"] = new_x
        player["y"] = new_y

# Funções dos Inimigos
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(SCREEN, RED, (enemy["x"] * TILE_SIZE, enemy["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def main():
    # Gera o labirinto inicial
    maze = generate_maze(SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE)
    pontos = 0

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movimento do jogador
        keys = pygame.key.get_pressed()
        if keys[pygame.K_UP]:
            move_player(maze, 0, -1)
        if keys[pygame.K_DOWN]:
            move_player(maze, 0, 1)
        if keys[pygame.K_LEFT]:
            move_player(maze, -1, 0)
        if keys[pygame.K_RIGHT]:
            move_player(maze, 1, 0)

        # Verifica se o jogador chegou à saída
        if maze[player["y"]][player["x"]] == 2:
            pontos += 1
            print(f"Você completou um labirinto! Pontos: {pontos}")
            maze = generate_maze(SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE)
            player["x"], player["y"] = 1, 1

        # Desenho
        SCREEN.fill(BLACK)
        draw_maze(maze)
        draw_player()
        draw_enemies()

        pygame.display.flip()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()