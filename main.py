# FUNCIONALIDADES PRINCIPAIS: 
# TODO: Fazer o player atirar na direção da última direção que ele andou
# TODO: Fazer o tiro matar o inimigo
# TODO: Fazer o inimigo matar o jogador (Isso tem que ser depois que o player
# conseguir matar o inimigo)

#FUNCIONALIDADES SECUNDÁRIAS:
# TODO: Fazer aparecer armas
# TODO: Deixar labirinto maior. Obs.: Não deu muito certo, a saída fica 
# inacessível, ficam paredes grossas em baixo e do lado direito e os 
# botões da janela do jogo somem

#Configurações:
# - Para mudar a velocidade do jogador é só mudar a variável 
# player_speed, quanto MAIOR o VALOR, MENOR a VELOCIDADE

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
enemies = []

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

# Função para gerar a arma
def spawn_weapon(maze, player_x, player_y):
    while True:
        weapon_x = random.randint(1, len(maze[0]) - 2)
        weapon_y = random.randint(1, len(maze) - 2)
        # A arma não pode nascer dentro de uma parede e perto do jogador (distância mínima de 5)
        if maze[weapon_y][weapon_x] == 0 and abs(player_x - weapon_x) < 3 and abs(player_y - weapon_y) < 3 and (weapon_x != player_x or weapon_y != player_y):
            return weapon_x, weapon_y


# Função para desenhar a arma
def draw_weapon(weapon_x, weapon_y):
    pygame.draw.rect(SCREEN, (255, 215, 0), (weapon_x * TILE_SIZE, weapon_y * TILE_SIZE, TILE_SIZE, TILE_SIZE))  # Arma amarela

# Função para o jogador pegar a arma
def pickup_weapon():
    return True  # Marca que o jogador pegou a arma (essa função pode ser expandida para incluir uma lógica de poder de ataque, por exemplo)


# Funções dos Inimigos
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(SCREEN, RED, (enemy["x"] * TILE_SIZE, enemy["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

def move_enemies(maze, last_enemy_move_times, enemy_speed):
    current_time = pygame.time.get_ticks()  # Obtém o tempo atual
    for i, enemy in enumerate(enemies):
        # Verifica se é a hora do inimigo i se mover
        if current_time - last_enemy_move_times[i] >= enemy_speed:
            moved = False
            while not moved:
                direction = random.randint(1, 4)  # Sorteia uma direção: 1 = cima, 2 = direita, 3 = baixo, 4 = esquerda
                dx, dy = 0, 0

                if direction == 1:  # Cima
                    dx, dy = 0, -1
                elif direction == 2:  # Direita
                    dx, dy = 1, 0
                elif direction == 3:  # Baixo
                    dx, dy = 0, 1
                elif direction == 4:  # Esquerda
                    dx, dy = -1, 0

                new_x = enemy["x"] + dx
                new_y = enemy["y"] + dy

                # Verifica se a nova posição é válida
                if maze[new_y][new_x] == 0:  # Caminho livre
                    # Faz um novo sorteio para decidir se o inimigo vai andar ou não
                    if random.choice([True, False]):  # 50% de chance de andar
                        enemy["x"], enemy["y"] = new_x, new_y
                    moved = True  # Movimento concluído

            last_enemy_move_times[i] = current_time  # Atualiza o último movimento do inimigo i
    return last_enemy_move_times

# Função para gerar a posição inicial dos inimigos
def spawn_enemy(maze, player_x, player_y):
    width = len(maze[0])
    height = len(maze)
    
    # Gerar uma posição válida
    while True:
        enemy_x = random.randint(1, width - 2)
        enemy_y = random.randint(1, height - 2)
        
        # Verifica se a posição não é uma parede e está longe do jogador
        if maze[enemy_y][enemy_x] == 0 and (abs(enemy_x - player_x) > 5 or abs(enemy_y - player_y) > 5):
            return {"x": enemy_x, "y": enemy_y}

def main():
    # Gera o labirinto inicial
    maze = generate_maze(SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE)
    pontos = 0

    player_speed = 125  # Tempo em milissegundos entre movimentos
    last_move_time = 0  # Momento do último movimento

    weapon_x, weapon_y = spawn_weapon(maze, player["x"], player["y"])  # Gera a arma perto do jogador

    weapon_picked_up = False  # Marca se a arma foi pegada ou não

    enemy_speed = 500  # Tempo em milissegundos entre movimentos dos inimigos
    last_enemy_move_times = []  # Momento do último movimento de cada inimigo

    # Gera inimigos em posições aleatórias válidas
    enemies.clear()  # Limpa a lista de inimigos antes de adicionar
    num_enemies = random.randint(1, 12)  # Número aleatório de inimigos entre 1 e 12

    # Adiciona os inimigos
    for _ in range(num_enemies):
        enemies.append(spawn_enemy(maze, player["x"], player["y"]))
        last_enemy_move_times.append(0)  # Inicializa o tempo de movimento para cada inimigo

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

        # Movimento dos inimigos
        last_enemy_move_times = move_enemies(maze, last_enemy_move_times, enemy_speed)

        # Movimento do jogador
        keys = pygame.key.get_pressed()
        current_time = pygame.time.get_ticks()  # Obtém o tempo atual
        if current_time - last_move_time >= player_speed:
            if keys[pygame.K_UP]:
                move_player(maze, 0, -1)
                last_move_time = current_time  # Atualiza o último movimento
            if keys[pygame.K_DOWN]:
                move_player(maze, 0, 1)
                last_move_time = current_time
            if keys[pygame.K_LEFT]:
                move_player(maze, -1, 0)
                last_move_time = current_time
            if keys[pygame.K_RIGHT]:
                move_player(maze, 1, 0)
                last_move_time = current_time

        # Verifica se o jogador apertou a barra de espaço para pegar a arma
        keys = pygame.key.get_pressed()
        if keys[pygame.K_SPACE] and player["x"] == weapon_x and player["y"] == weapon_y and not weapon_picked_up:
            weapon_picked_up = pickup_weapon()

        # Verifica se o jogador chegou à saída
        if maze[player["y"]][player["x"]] == 2:
            pontos += 1
            print(f"Você completou um labirinto! Pontos: {pontos}")
            maze = generate_maze(SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE)
            player["x"], player["y"] = 1, 1
            # Gera novos inimigos
            enemies.clear()
            last_enemy_move_times.clear()
            num_enemies = random.randint(1, 12)
            for _ in range(num_enemies):
                enemies.append(spawn_enemy(maze, player["x"], player["y"]))
                last_enemy_move_times.append(0)

        # Desenho
        SCREEN.fill(BLACK)
        draw_maze(maze)
        draw_player()
        draw_enemies()

        if not weapon_picked_up:
            draw_weapon(weapon_x, weapon_y)  # Desenha a arma na tela se não tiver sido pega


        pygame.display.flip()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()