import pygame
import sys
import random
from collections import deque

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
YELLOW = (255, 215, 0)

# Tamanho dos tiles
TILE_SIZE = 40

# Jogador
player = {"x": 1, "y": 1, "last_direction": (0, 0)}  # Adicionada última direção para controlar o disparo

# Inimigos
enemies = []

# Tiros
bullets = []  # Lista para armazenar os projéteis

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

    # Assegura que a saída está correta após a geração
    maze[height - 2][width - 2] = 2  # Recoloca a saída caso tenha sido sobrescrita
    return maze

#Labirinto
def draw_maze(maze):
    for y, row in enumerate(maze):
        for x, cell in enumerate(row):
            # Define a cor do tile com base no valor de `cell`
            if cell == 0:  # Espaço vazio
                color = WHITE
            elif cell == 1:  # Parede
                color = BLACK
            elif cell == 2:  # Saída normal em verde
                color = GREEN
            elif cell == 3:  # Saída azul clara
                color = (173, 216, 230)  # Azul claro
            else:
                color = WHITE  # Caso padrão (não esperado)

            # Desenha o tile no labirinto
            pygame.draw.rect(SCREEN, color, (x * TILE_SIZE, y * TILE_SIZE, TILE_SIZE, TILE_SIZE))

# Funções do Jogador
def draw_player():
    pygame.draw.rect(SCREEN, BLUE, (player["x"] * TILE_SIZE, player["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

#Jogador
def move_player(maze, dx, dy):
    new_x = player["x"] + dx
    new_y = player["y"] + dy
    if maze[new_y][new_x] == 0 or maze[new_y][new_x] == 2 or maze[new_y][new_x] == 3:
        player["x"] = new_x
        player["y"] = new_y
        # Atualiza a última direção em que o jogador se moveu
        player["last_direction"] = (dx, dy)

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
    print("Arma pega!")
    return True  # Marca que o jogador pegou a arma (essa função pode ser expandida para incluir uma lógica de poder de ataque, por exemplo)

# Funções dos Inimigos
def draw_enemies():
    for enemy in enemies:
        pygame.draw.rect(SCREEN, RED, (enemy["x"] * TILE_SIZE, enemy["y"] * TILE_SIZE, TILE_SIZE, TILE_SIZE))

#Inimigos
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

#Inimigos
def check_player_death():
    for enemy in enemies:
        if enemy["x"] == player["x"] and enemy["y"] == player["y"]:
            print("O jogador foi morto por um inimigo!")
            return True  # Retorna True indicando que o jogador foi morto
    return False  # Retorna False se o jogador não foi morto

# Funções de Tiros da arma
def shoot_bullet():
    # Verifica se o jogador possui uma última direção válida para atirar
    if "last_direction" in player and player["last_direction"] != (0, 0):
        # Cria um projétil na posição do jogador e na direção indicada
        bullets.append({
            "x": player["x"],
            "y": player["y"],
            "dx": player["last_direction"][0],
            "dy": player["last_direction"][1]
        })
        # Mensagem no console confirmando que o tiro foi disparado
        print(f"Tiro disparado! Posição inicial: ({player['x']}, {player['y']}), Direção: {player['last_direction']}")
    else:
        # Mensagem no console indicando por que o tiro não foi disparado
        print("Falha ao disparar o tiro: última direção inválida ou não definida.")

#arma
def draw_bullets():
    # Desenha todos os projéteis na tela
    for bullet in bullets:
        pygame.draw.rect(SCREEN, YELLOW, (bullet["x"] * TILE_SIZE + TILE_SIZE // 4, bullet["y"] * TILE_SIZE + TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))

#arma
def move_bullets(maze):
    # Move os projéteis e verifica colisões
    for bullet in bullets[:]:
        # Atualiza a posição do projétil
        bullet["x"] += bullet["dx"]
        bullet["y"] += bullet["dy"]
        # Verifica se o projétil colidiu com uma parede
        if maze[bullet["y"]][bullet["x"]] == 1:
            bullets.remove(bullet)
            print(f"Tiro removido! Colisão com parede em ({bullet['x']}, {bullet['y']})")
        # Verifica colisão com inimigos
        for enemy in enemies[:]:
            if bullet["x"] == enemy["x"] and bullet["y"] == enemy["y"]:
                enemies.remove(enemy)
                bullets.remove(bullet)
                print(f"Tiro atingiu inimigo em ({bullet['x']}, {bullet['y']})!")
                break

#Aposentadoria
def add_room_to_maze(maze, quadrant, exit_pos=None):
    """
    Adiciona uma sala vazia no labirinto em um dos quadrantes permitidos.
    A sala é 7x7, com um interior de 5x5, e somente um tile azul claro no centro.
    """
    width = len(maze[0])
    height = len(maze)
    
    room_size = 7
    inner_size = 5
    
    # Determina os limites para posicionar a sala no quadrante correto
    if quadrant == 2:  # Superior direito
        x_start = width - room_size
        y_start = 0
    elif quadrant == 3:  # Inferior esquerdo
        x_start = 0
        y_start = height - room_size

    # Preenche o interior da sala (5x5) com tiles vazios
    for y in range(y_start + 1, y_start + 1 + inner_size):
        for x in range(x_start + 1, x_start + 1 + inner_size):
            maze[y][x] = 0  # Marca como espaço vazio
    
    # Adiciona a saída azul clara no centro da sala (posição [2, 2])
    maze[y_start + 2][x_start + 2] = 3  # 3 representa a nova saída azul clara
    
    # Adiciona as paredes ao redor da sala (mas não dentro dela)
    for y in range(y_start, y_start + room_size):
        maze[y][x_start] = 1  # Parede esquerda
        maze[y][x_start + room_size - 1] = 1  # Parede direita
    
    for x in range(x_start, x_start + room_size):
        maze[y_start][x] = 1  # Parede superior
        maze[y_start + room_size - 1][x] = 1  # Parede inferior

    return maze

#Aposentadoria
def ensure_paths(maze, start_pos, room_entrance, exit_pos):
    """
    Garante caminhos livres entre o jogador, a entrada da sala e a saída.
    """
    def carve_path(maze, start, end):
        """Cria um caminho livre entre dois pontos."""
        x1, y1 = start
        x2, y2 = end
        while (x1, y1) != (x2, y2):
            maze[y1][x1] = 0  # Marca como caminho livre
            if x1 < x2:
                x1 += 1
            elif x1 > x2:
                x1 -= 1
            elif y1 < y2:
                y1 += 1
            elif y1 > y2:
                y1 -= 1
        maze[y2][x2] = 0  # Garante que o ponto final seja caminho

    # Garante caminho entre o jogador e a entrada da sala
    carve_path(maze, start_pos, room_entrance)
    
    # Garante caminho entre a entrada da sala e a saída
    carve_path(maze, room_entrance, exit_pos)

    # Garante que a saída esteja livre após criar os caminhos
    ensure_exit_walls(maze, exit_pos)

#Labirinto
def ensure_exit_walls(maze, exit_pos):
    """
    Garante que as paredes ao redor da saída estejam intactas e que a saída não seja bloqueada.
    """
    exit_x, exit_y = exit_pos

    # Restaurar a parede acima da saída (linha completa)
    if exit_y > 0:  # Apenas se houver espaço para uma parede acima
        for x in range(len(maze[0])):  # Itera horizontalmente
            if maze[exit_y - 1][x] != 0:  # Apenas paredes, não caminhos
                maze[exit_y - 1][x] = 1

    # Garante que a saída em si seja livre
    maze[exit_y][exit_x] = 0

    # Garante que nenhum tile diretamente em frente à saída esteja bloqueado
    for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
        adj_x, adj_y = exit_x + dx, exit_y + dy
        if 0 <= adj_x < len(maze[0]) and 0 <= adj_y < len(maze):
            if (dx, dy) == (0, 1):  # Apenas para a posição diretamente em frente à saída
                maze[adj_y][adj_x] = 0

#Aposentadoria
def add_room_to_maze_with_validation(maze, quadrant, player_start, exit_pos):
    maze = add_room_to_maze(maze, quadrant, exit_pos)
    room_entrance = find_room_entrance(maze, quadrant)
    ensure_paths(maze, player_start, room_entrance, exit_pos)
    ensure_exit_persistence(maze, exit_pos)  # Garante consistência da saída
    return maze

#Aposentadoria
def find_room_entrance(maze, quadrant):
    """
    Determina a entrada da sala no labirinto.
    """
    # O cálculo da entrada permanece o mesmo; adaptado à posição da sala
    # Exemplo (simplificado):
    if quadrant == 2:  # Superior direito
        return len(maze[0]) - 4, 3
    elif quadrant == 3:  # Inferior esquerdo
        return 3, len(maze) - 4

#Labirinto
def ensure_exit_persistence(maze, exit_pos):
    x, y = exit_pos

    # Assegura que o tile da saída é mantido
    maze[y][x] = 2

    # Reforça as paredes ao redor da saída, se necessário
    if y > 0:  # Linha acima
        maze[y - 1][x] = 1
    if y < len(maze) - 1:  # Linha abaixo
        maze[y + 1][x] = 1
    if x < len(maze[0]) - 1:  # Coluna à direita
        maze[y][x + 1] = 1

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
            # Verifica se o jogador pressionou a barra de espaço para atirar
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    if weapon_picked_up:
                        print("Tentando disparar...")
                        shoot_bullet()
                    else:
                        print("Você precisa pegar a arma primeiro!")

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

        # Move os projéteis
        move_bullets(maze)

        # Verifica se o jogador foi morto
        if check_player_death():
            print("Fim de jogo!")  # Mensagem no console
            pygame.quit()
            sys.exit()  # Encerra o jogo

        # Verifica se o jogador chegou à nova saída azul clara
        if maze[player["y"]][player["x"]] == 3:  # Se o jogador estiver na posição da nova saída
            print("Você encontrou a saída azul clara! O jogo terminou.")
            pontos += 1
            print(f"Pontos: {pontos}")
            # Pode adicionar mais lógica aqui, como reiniciar o labirinto ou fechar o jogo
            pygame.quit()
            sys.exit()  # Isso finaliza o loop e encerra o jogo

        # Verifica se o jogador chegou à saída
        if maze[player["y"]][player["x"]] == 2:
            pontos += 1
            print(f"Você completou um labirinto! Pontos: {pontos}")
            maze = generate_maze(SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE)
            
            ensure_exit_persistence(maze, (len(maze[0]) - 2, len(maze) - 2))  # Valida saída

            if pontos % 5 == 0:  # Verifica se o jogador está em uma fase múltipla de 5
                available_quadrants = [2, 3]  # Apenas superior direito e inferior esquerdo
                selected_quadrant = random.choice(available_quadrants)
                maze = add_room_to_maze_with_validation(maze, selected_quadrant, player_start=(1, 1), exit_pos=(len(maze[0]) - 2, len(maze) - 2))
                print(f"Sala adicionada no quadrante {selected_quadrant}!")
            
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
        draw_bullets()
        if not weapon_picked_up:
            draw_weapon(weapon_x, weapon_y)  # Desenha a arma na tela se não tiver sido pega


        pygame.display.flip()
        CLOCK.tick(FPS)

if __name__ == "__main__":
    main()