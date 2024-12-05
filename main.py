# FUNCIONALIDADES PRINCIPAIS: 
# TODO: Aposentadoria - Problema principal atual: Toda fase que tem a 
# sala vazia da aposentadoria, a parede do labirinto em cima da saida 
# some por algum motivo, deixando essa fase muito fácil.
# Problema secundário: Algumas vezes tem duas ou mais entradas para a sala
# vazia, mas eu queria que só fosse uma entrada
# Obs: Deixei para a sala vazia nascer toda fase a partir da primeira pra
# ficar mais fácil de testar
# TODO: Buff dos inimigos e do jogador
# TODO: Fazer aparecer armas

#FUNCIONALIDADES SECUNDÁRIAS:
# TODO: Ao invés de fechar o jogo ao morrer, voltar pra fase 1 com 0 pontos e sem arma ou pra tela de início, se for ter. Prestar atenção que vai ter que resetar tudo, 
#como os buffs etc
# TODO: Tela de início/título/menu
# TODO: Fazer o jogador olhar pra direção antes de andar, pra ele não ter que andar pra atirar em uma direção
# TODO: Deixar labirinto maior. Obs.: Não deu muito certo, a saída fica 
# inacessível, ficam paredes grossas em baixo e do lado direito e os 
# botões da janela do jogo somem

#Configurações:
# - Para mudar a velocidade do jogador é só mudar a variável 
# player_speed, quanto MAIOR o VALOR, MENOR a VELOCIDADE

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

def check_player_death():
    for enemy in enemies:
        if enemy["x"] == player["x"] and enemy["y"] == player["y"]:
            print("O jogador foi morto por um inimigo!")
            return True  # Retorna True indicando que o jogador foi morto
    return False  # Retorna False se o jogador não foi morto

# Funções de Tiros
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

def draw_bullets():
    # Desenha todos os projéteis na tela
    for bullet in bullets:
        pygame.draw.rect(SCREEN, YELLOW, (bullet["x"] * TILE_SIZE + TILE_SIZE // 4, bullet["y"] * TILE_SIZE + TILE_SIZE // 4, TILE_SIZE // 2, TILE_SIZE // 2))

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

def add_room_to_maze(maze, quadrant):
    """
    Adiciona uma sala vazia no labirinto em um dos quadrantes permitidos.
    A sala é 7x7, com um interior de 5x5, aproveitando paredes do labirinto.
    """
    width = len(maze[0])
    height = len(maze)
    
    room_size = 7
    inner_size = 5
    
    # Determina os limites para posicionar a sala no quadrante correto
    if quadrant == 2:  # Superior direito
        x_start = width - room_size
        y_start = 0
        use_labyrinth_wall = ("top", "right")
    elif quadrant == 3:  # Inferior esquerdo
        x_start = 0
        y_start = height - room_size
        use_labyrinth_wall = ("left", "bottom")

    # Preenche o interior da sala (5x5)
    for y in range(y_start + 1, y_start + 1 + inner_size):
        for x in range(x_start + 1, x_start + 1 + inner_size):
            maze[y][x] = 0  # Marca como espaço vazio

    # Cria as paredes externas necessárias
    if "top" not in use_labyrinth_wall:  # Constrói a parede superior
        for x in range(x_start, x_start + room_size):
            maze[y_start][x] = 1
    if "bottom" not in use_labyrinth_wall:  # Constrói a parede inferior
        for x in range(x_start, x_start + room_size):
            maze[y_start + room_size - 1][x] = 1
    if "left" not in use_labyrinth_wall:  # Constrói a parede esquerda
        for y in range(y_start, y_start + room_size):
            maze[y][x_start] = 1
    if "right" not in use_labyrinth_wall:  # Constrói a parede direita
        for y in range(y_start, y_start + room_size):
            maze[y][x_start + room_size - 1] = 1

    # Adiciona uma única entrada na parede construída
    possible_entrances = []
    if "top" not in use_labyrinth_wall:  # Entrada na parede superior
        for x in range(x_start + 1, x_start + 1 + inner_size):
            if maze[y_start - 1][x] == 0:
                possible_entrances.append((x, y_start))
    if "bottom" not in use_labyrinth_wall:  # Entrada na parede inferior
        for x in range(x_start + 1, x_start + 1 + inner_size):
            if maze[y_start + room_size][x] == 0:
                possible_entrances.append((x, y_start + room_size - 1))
    if "left" not in use_labyrinth_wall:  # Entrada na parede esquerda
        for y in range(y_start + 1, y_start + 1 + inner_size):
            if maze[y][x_start - 1] == 0:
                possible_entrances.append((x_start, y))
    if "right" not in use_labyrinth_wall:  # Entrada na parede direita
        for y in range(y_start + 1, y_start + 1 + inner_size):
            if maze[y][x_start + room_size] == 0:
                possible_entrances.append((x_start + room_size - 1, y))

    if possible_entrances:
        entrance_x, entrance_y = random.choice(possible_entrances)
        maze[entrance_y][entrance_x] = 0  # Marca a entrada como caminho livre

    return maze

def is_path_clear(maze, start, targets):
    """
    Verifica se há um caminho claro entre o ponto de início e qualquer um dos alvos.
    """
    height = len(maze)
    width = len(maze[0])
    visited = [[False] * width for _ in range(height)]
    queue = deque([start])
    visited[start[1]][start[0]] = True

    while queue:
        x, y = queue.popleft()
        if (x, y) in targets:
            return True  # Alvo alcançado

        # Movimentos possíveis (cima, baixo, esquerda, direita)
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]
        for dx, dy in directions:
            nx, ny = x + dx, y + dy
            if 0 <= nx < width and 0 <= ny < height and not visited[ny][nx] and maze[ny][nx] == 0:
                visited[ny][nx] = True
                queue.append((nx, ny))
    
    return False

def ensure_paths(maze, player_start, room_entrance, exit_pos):
    """
    Garante que há caminhos entre o jogador, a entrada da sala e a saída.
    """
    all_points = [room_entrance, exit_pos]
    for target in all_points:
        if not is_path_clear(maze, player_start, [target]):
            create_path(maze, player_start, target)

def create_path(maze, start, end):
    """
    Cria um caminho direto entre dois pontos (start e end) no labirinto.
    """
    x1, y1 = start
    x2, y2 = end

    while (x1, y1) != (x2, y2):
        if x1 < x2:
            x1 += 1
        elif x1 > x2:
            x1 -= 1
        elif y1 < y2:
            y1 += 1
        elif y1 > y2:
            y1 -= 1
        maze[y1][x1] = 0  # Torna o tile parte do caminho

def add_room_to_maze_with_validation(maze, quadrant, player_start, exit_pos):
    """
    Adiciona uma sala vazia ao labirinto, garantindo conectividade.
    """
    maze = add_room_to_maze(maze, quadrant)  # Cria a sala
    room_entrance = find_room_entrance(maze, quadrant)  # Determina a entrada da sala
    ensure_paths(maze, player_start, room_entrance, exit_pos)  # Garante os caminhos
    ensure_exit_persistence(maze, exit_pos)  # Garante que a saída permaneça
    return maze

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

def ensure_exit_persistence(maze, exit_pos):
    """
    Garante que a saída permaneça no labirinto.
    """
    x, y = exit_pos
    if maze[y][x] != 2:  # Se a saída foi alterada
        maze[y][x] = 2  # Recoloca a saída no lugar correto


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

        # Verifica se o jogador chegou à saída
        if maze[player["y"]][player["x"]] == 2:
            pontos += 1
            print(f"Você completou um labirinto! Pontos: {pontos}")
            maze = generate_maze(SCREEN_WIDTH // TILE_SIZE, SCREEN_HEIGHT // TILE_SIZE)
            
            if pontos % 1 == 0:  # Verifica se o jogador está em uma fase múltipla de 5
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