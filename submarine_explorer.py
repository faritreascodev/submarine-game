import pygame
import random
import math
import numpy as np
import json
import os
from enum import Enum
from typing import List, Tuple, Optional
from dataclasses import dataclass

# Inicializar Pygame
pygame.init()
pygame.mixer.init()

# Constantes del juego
SCREEN_WIDTH = 1200
SCREEN_HEIGHT = 800
FPS = 60
CELL_SIZE = 40

# Colores temáticos submarinos
COLORS = {
    'water_deep': (15, 45, 85),
    'water_light': (25, 65, 120),
    'coral_pink': (255, 127, 80),
    'coral_red': (220, 100, 60),
    'pearl_white': (255, 255, 240),
    'pearl_shine': (255, 255, 255),
    'giant_pearl': (255, 215, 0),
    'shark_gray': (105, 105, 105),
    'shark_dark': (70, 70, 70),
    'jellyfish_purple': (147, 112, 219),
    'jellyfish_light': (180, 150, 255),
    'bubble_blue': (173, 216, 230),
    'harpoon_silver': (192, 192, 192),
    'diver_blue': (0, 100, 200),
    'diver_orange': (255, 140, 0),
    'text_white': (255, 255, 255),
    'text_gold': (255, 215, 0),
    'danger_red': (255, 100, 100),
    'success_green': (100, 255, 100)
}

class GameState(Enum):
    MENU = "menu"
    PLAYING = "playing"
    PAUSED = "paused"
    GAME_OVER = "game_over"
    VICTORY = "victory"
    INSTRUCTIONS = "instructions"
    HIGH_SCORES = "high_scores"

@dataclass
class GameConfig:
    """Configuración del juego"""
    player_speed: float = 4.0
    shark_speed: float = 2.0
    jellyfish_speed: float = 1.5
    harpoon_duration: int = 300  # 5 segundos a 60 FPS
    bubble_spawn_rate: int = 8
    enemy_count: int = 6
    pearl_count: int = 20
    giant_pearl_count: int = 4
    maze_width: int = 30
    maze_height: int = 20

class ScoreManager:
    """Sistema de gestión de puntuaciones"""
    
    def __init__(self):
        self.scores_file = "submarine_high_scores.json"
        self.high_scores = self.load_scores()
    
    def load_scores(self) -> List[dict]:
        """Carga las puntuaciones desde archivo"""
        try:
            if os.path.exists(self.scores_file):
                with open(self.scores_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    return data.get('scores', [])
        except Exception as e:
            print(f"Error cargando puntuaciones: {e}")
        return []
    
    def save_score(self, score: int, level_completed: bool = False):
        """Guarda una nueva puntuación"""
        import datetime
        new_score = {
            'score': score,
            'date': datetime.datetime.now().strftime("%Y-%m-%d %H:%M"),
            'completed': level_completed
        }
        
        self.high_scores.append(new_score)
        self.high_scores.sort(key=lambda x: x['score'], reverse=True)
        self.high_scores = self.high_scores[:10]  # Top 10
        
        try:
            with open(self.scores_file, 'w', encoding='utf-8') as f:
                json.dump({'scores': self.high_scores}, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Error guardando puntuaciones: {e}")
    
    def get_high_score(self) -> int:
        """Obtiene la puntuación más alta"""
        return self.high_scores[0]['score'] if self.high_scores else 0
    
    def get_top_scores(self, count: int = 10) -> List[dict]:
        """Obtiene las mejores puntuaciones"""
        return self.high_scores[:count]

class ParticleSystem:
    """Sistema de partículas para efectos visuales"""
    
    def __init__(self):
        self.particles = []
    
    def add_bubble(self, x: float, y: float):
        """Añade una burbuja"""
        self.particles.append(Bubble(x, y))
    
    def add_explosion(self, x: float, y: float, color: Tuple[int, int, int]):
        """Añade una explosión de partículas"""
        for _ in range(8):
            self.particles.append(ExplosionParticle(x, y, color))
    
    def update(self):
        """Actualiza todas las partículas"""
        self.particles = [p for p in self.particles if p.update()]
    
    def draw(self, screen: pygame.Surface):
        """Dibuja todas las partículas"""
        for particle in self.particles:
            particle.draw(screen)

class Particle:
    """Clase base para partículas"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        self.x = x
        self.y = y
        self.color = color
        self.life = 1.0
        self.max_life = 1.0
        self.decay = random.uniform(0.01, 0.03)
    
    def update(self) -> bool:
        """Actualiza la partícula, retorna False si debe eliminarse"""
        self.life -= self.decay
        return self.life > 0
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la partícula"""
        if self.life > 0:
            alpha_ratio = self.life / self.max_life
            size = max(1, int(4 * alpha_ratio))
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)

class Bubble(Particle):
    """Burbuja que sube hacia la superficie"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, COLORS['bubble_blue'])
        self.vel_y = random.uniform(-2, -4)
        self.vel_x = random.uniform(-1, 1)
        self.size = random.uniform(3, 8)
        self.wobble = random.uniform(0, 2 * math.pi)
        self.max_life = random.uniform(3, 6)
        self.life = self.max_life
        self.decay = 1 / (self.max_life * FPS)
    
    def update(self) -> bool:
        self.wobble += 0.1
        self.x += self.vel_x + math.sin(self.wobble) * 0.5
        self.y += self.vel_y
        
        # Acelerar hacia arriba
        self.vel_y *= 1.01
        
        return super().update() and self.y > -20
    
    def draw(self, screen: pygame.Surface):
        if self.life > 0:
            alpha_ratio = self.life / self.max_life
            size = max(1, int(self.size * alpha_ratio))
            
            # Burbuja principal
            pygame.draw.circle(screen, self.color, (int(self.x), int(self.y)), size)
            
            # Brillo
            if size > 2:
                highlight_pos = (int(self.x - size//3), int(self.y - size//3))
                pygame.draw.circle(screen, COLORS['pearl_shine'], highlight_pos, max(1, size//3))

class ExplosionParticle(Particle):
    """Partícula de explosión"""
    
    def __init__(self, x: float, y: float, color: Tuple[int, int, int]):
        super().__init__(x, y, color)
        angle = random.uniform(0, 2 * math.pi)
        speed = random.uniform(2, 6)
        self.vel_x = math.cos(angle) * speed
        self.vel_y = math.sin(angle) * speed
        self.max_life = random.uniform(0.5, 1.5)
        self.life = self.max_life
        self.decay = 1 / (self.max_life * FPS)
    
    def update(self) -> bool:
        self.x += self.vel_x
        self.y += self.vel_y
        self.vel_x *= 0.95
        self.vel_y *= 0.95
        return super().update()

class Maze:
    """Generador y manejador del laberinto de coral"""
    
    def __init__(self, width: int, height: int):
        self.width = width
        self.height = height
        self.grid = self.generate_maze()
        self.coral_animations = {}
        self.init_coral_animations()
    
    def generate_maze(self) -> List[List[bool]]:
        """Genera un laberinto usando algoritmo de división recursiva"""
        maze = [[False for _ in range(self.width)] for _ in range(self.height)]
        
        # Crear bordes
        for x in range(self.width):
            maze[0][x] = True
            maze[self.height-1][x] = True
        for y in range(self.height):
            maze[y][0] = True
            maze[y][self.width-1] = True
        
        # Generar estructura interna
        self._divide_maze(maze, 1, 1, self.width-2, self.height-2)
        
        # Crear algunas aberturas adicionales para mejor jugabilidad
        self._create_openings(maze)
        
        return maze
    
    def _divide_maze(self, maze: List[List[bool]], x: int, y: int, width: int, height: int):
        """División recursiva del laberinto"""
        if width < 4 or height < 4:
            return
        
        # Decidir si dividir horizontal o verticalmente
        horizontal = random.choice([True, False]) if width > height else width < height
        
        if horizontal:
            # División horizontal
            wall_y = y + random.randrange(2, height-1, 2)
            for wx in range(x, x + width):
                maze[wall_y][wx] = True
            
            # Crear apertura
            opening = x + random.randrange(0, width, 2) + 1
            maze[wall_y][opening] = False
            
            # Recursión
            self._divide_maze(maze, x, y, width, wall_y - y)
            self._divide_maze(maze, x, wall_y + 1, width, height - (wall_y - y + 1))
        else:
            # División vertical
            wall_x = x + random.randrange(2, width-1, 2)
            for wy in range(y, y + height):
                maze[wy][wall_x] = True
            
            # Crear apertura
            opening = y + random.randrange(0, height, 2) + 1
            maze[opening][wall_x] = False
            
            # Recursión
            self._divide_maze(maze, x, y, wall_x - x, height)
            self._divide_maze(maze, wall_x + 1, y, width - (wall_x - x + 1), height)
    
    def _create_openings(self, maze: List[List[bool]]):
        """Crea aberturas adicionales"""
        openings_created = 0
        max_openings = (self.width * self.height) // 20
        
        while openings_created < max_openings:
            x = random.randint(1, self.width - 2)
            y = random.randint(1, self.height - 2)
            
            if maze[y][x] and random.random() < 0.3:
                maze[y][x] = False
                openings_created += 1
    
    def init_coral_animations(self):
        """Inicializa animaciones de coral"""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]:
                    self.coral_animations[(x, y)] = {
                        'phase': random.uniform(0, 2 * math.pi),
                        'speed': random.uniform(0.02, 0.05),
                        'amplitude': random.uniform(2, 5)
                    }
    
    def is_wall(self, x: float, y: float) -> bool:
        """Verifica si una posición es una pared"""
        grid_x = int(x // CELL_SIZE)
        grid_y = int(y // CELL_SIZE)
        
        if (grid_x < 0 or grid_x >= self.width or 
            grid_y < 0 or grid_y >= self.height):
            return True
        
        return self.grid[grid_y][grid_x]
    
    def get_free_position(self) -> Tuple[float, float]:
        """Obtiene una posición libre en el laberinto"""
        attempts = 0
        while attempts < 100:
            x = random.randint(CELL_SIZE, SCREEN_WIDTH - CELL_SIZE)
            y = random.randint(CELL_SIZE, SCREEN_HEIGHT - CELL_SIZE)
            
            if not self.is_wall(x, y):
                return x, y
            attempts += 1
        
        # Fallback: posición cerca del inicio
        return CELL_SIZE * 2, CELL_SIZE * 2
    
    def update(self):
        """Actualiza animaciones del coral"""
        for pos, anim in self.coral_animations.items():
            anim['phase'] += anim['speed']
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el laberinto con animaciones"""
        for y in range(self.height):
            for x in range(self.width):
                if self.grid[y][x]:
                    rect = pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE)
                    
                    # Animación de coral
                    anim = self.coral_animations.get((x, y), {'phase': 0, 'amplitude': 0})
                    color_offset = int(math.sin(anim['phase']) * anim.get('amplitude', 0))
                    
                    # Color base del coral
                    base_color = COLORS['coral_pink']
                    animated_color = (
                        min(255, max(0, base_color[0] + color_offset)),
                        min(255, max(0, base_color[1] + color_offset//2)),
                        min(255, max(0, base_color[2]))
                    )
                    
                    # Dibujar coral
                    pygame.draw.rect(screen, animated_color, rect)
                    pygame.draw.rect(screen, COLORS['coral_red'], rect, 2)
                    
                    # Añadir textura
                    if random.random() < 0.1:  # Detalles ocasionales
                        detail_rect = pygame.Rect(rect.x + 5, rect.y + 5, 
                                                rect.width - 10, rect.height - 10)
                        pygame.draw.rect(screen, COLORS['coral_red'], detail_rect)

class GameObject:
    """Clase base para objetos del juego"""
    
    def __init__(self, x: float, y: float, size: int):
        self.x = x
        self.y = y
        self.size = size
        self.rect = pygame.Rect(x - size//2, y - size//2, size, size)
        self.active = True
        self.animation_time = 0
    
    def update_rect(self):
        """Actualiza el rectángulo de colisión"""
        self.rect.center = (int(self.x), int(self.y))
    
    def collides_with(self, other: 'GameObject') -> bool:
        """Verifica colisión con otro objeto"""
        return self.active and other.active and self.rect.colliderect(other.rect)
    
    def distance_to(self, other: 'GameObject') -> float:
        """Calcula distancia a otro objeto"""
        return math.sqrt((self.x - other.x)**2 + (self.y - other.y)**2)

class Player(GameObject):
    """Jugador - buzo submarino"""
    
    def __init__(self, x: float, y: float, config: GameConfig):
        super().__init__(x, y, 24)
        self.config = config
        self.speed = config.player_speed
        self.direction = 0  # Ángulo en radianes
        self.velocity_x = 0
        self.velocity_y = 0
        self.has_harpoon = False
        self.harpoon_time = 0
        self.swimming_animation = 0
        self.invulnerable = False
        self.invulnerable_time = 0
        self.max_invulnerable_time = 120  # 2 segundos
    
    def update(self, maze: Maze):
        """Actualiza el jugador"""
        keys = pygame.key.get_pressed()
        
        # Movimiento con aceleración
        target_vel_x = 0
        target_vel_y = 0
        
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            target_vel_x = -self.speed
            self.direction = math.pi
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            target_vel_x = self.speed
            self.direction = 0
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            target_vel_y = -self.speed
            self.direction = -math.pi/2
        if keys[pygame.K_DOWN] or keys[pygame.K_s]:
            target_vel_y = self.speed
            self.direction = math.pi/2
        
        # Movimiento diagonal
        if target_vel_x != 0 and target_vel_y != 0:
            target_vel_x *= 0.707  # sqrt(2)/2
            target_vel_y *= 0.707
            self.direction = math.atan2(target_vel_y, target_vel_x)
        
        # Suavizar movimiento
        self.velocity_x += (target_vel_x - self.velocity_x) * 0.2
        self.velocity_y += (target_vel_y - self.velocity_y) * 0.2
        
        # Verificar colisiones con paredes
        new_x = self.x + self.velocity_x
        new_y = self.y + self.velocity_y
        
        if not maze.is_wall(new_x, self.y):
            self.x = new_x
        else:
            self.velocity_x = 0
            
        if not maze.is_wall(self.x, new_y):
            self.y = new_y
        else:
            self.velocity_y = 0
        
        # Mantener dentro de la pantalla
        self.x = max(self.size//2, min(SCREEN_WIDTH - self.size//2, self.x))
        self.y = max(self.size//2, min(SCREEN_HEIGHT - self.size//2, self.y))
        
        # Actualizar animaciones
        if abs(self.velocity_x) > 0.1 or abs(self.velocity_y) > 0.1:
            self.swimming_animation += 0.3
        
        self.animation_time += 1
        
        # Actualizar arpón
        if self.has_harpoon:
            self.harpoon_time -= 1
            if self.harpoon_time <= 0:
                self.has_harpoon = False
        
        # Actualizar invulnerabilidad
        if self.invulnerable:
            self.invulnerable_time -= 1
            if self.invulnerable_time <= 0:
                self.invulnerable = False
        
        self.update_rect()
    
    def give_harpoon(self):
        """Otorga arpón temporal al jugador"""
        self.has_harpoon = True
        self.harpoon_time = self.config.harpoon_duration
    
    def take_damage(self):
        """El jugador recibe daño"""
        if not self.invulnerable:
            self.invulnerable = True
            self.invulnerable_time = self.max_invulnerable_time
            return True
        return False
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el jugador con animaciones detalladas"""
        # Efecto de parpadeo si es invulnerable
        if self.invulnerable and (self.invulnerable_time // 5) % 2:
            return
        
        # Color base
        base_color = COLORS['diver_orange'] if self.has_harpoon else COLORS['diver_blue']
        
        # Cuerpo principal del buzo
        body_offset_x = math.cos(self.swimming_animation) * 2
        body_offset_y = math.sin(self.swimming_animation * 2) * 1
        
        body_x = int(self.x + body_offset_x)
        body_y = int(self.y + body_offset_y)
        
        # Cuerpo
        pygame.draw.ellipse(screen, base_color, 
                          (body_x - 12, body_y - 8, 24, 16))
        
        # Tanque de oxígeno
        pygame.draw.ellipse(screen, COLORS['shark_gray'], 
                          (body_x - 8, body_y - 12, 6, 20))
        
        # Máscara de buceo
        mask_x = body_x + int(math.cos(self.direction) * 8)
        mask_y = body_y + int(math.sin(self.direction) * 8)
        
        pygame.draw.circle(screen, (50, 50, 50), (mask_x, mask_y), 8)
        pygame.draw.circle(screen, (200, 200, 255), (mask_x, mask_y), 6)
        
        # Aletas con animación
        fin_offset = math.sin(self.swimming_animation) * 3
        fin_x = body_x - int(math.cos(self.direction) * 15)
        fin_y = body_y - int(math.sin(self.direction) * 15) + int(fin_offset)
        
        # Aletas
        fin_points = [
            (fin_x, fin_y - 4),
            (fin_x - 8, fin_y - 2),
            (fin_x - 8, fin_y + 2),
            (fin_x, fin_y + 4)
        ]
        pygame.draw.polygon(screen, (0, 50, 150), fin_points)
        
        # Brazos
        arm_angle = self.direction + math.sin(self.swimming_animation) * 0.3
        arm_x = body_x + int(math.cos(arm_angle) * 10)
        arm_y = body_y + int(math.sin(arm_angle) * 10)
        pygame.draw.circle(screen, base_color, (arm_x, arm_y), 4)
        
        # Arpón si está activo
        if self.has_harpoon:
            harpoon_length = 25
            harpoon_end_x = mask_x + int(math.cos(self.direction) * harpoon_length)
            harpoon_end_y = mask_y + int(math.sin(self.direction) * harpoon_length)
            
            # Mango del arpón
            pygame.draw.line(screen, (139, 69, 19), 
                           (mask_x, mask_y), (harpoon_end_x, harpoon_end_y), 4)
            
            # Punta del arpón
            pygame.draw.line(screen, COLORS['harpoon_silver'], 
                           (mask_x, mask_y), (harpoon_end_x, harpoon_end_y), 2)
            
            # Punta triangular
            tip_points = []
            for angle_offset in [-0.3, 0, 0.3]:
                tip_angle = self.direction + angle_offset
                tip_x = harpoon_end_x + int(math.cos(tip_angle) * 8)
                tip_y = harpoon_end_y + int(math.sin(tip_angle) * 8)
                tip_points.append((tip_x, tip_y))
            
            if len(tip_points) == 3:
                pygame.draw.polygon(screen, COLORS['harpoon_silver'], tip_points)
        
        # Burbujas ocasionales
        if random.random() < 0.1:
            bubble_x = mask_x + random.randint(-5, 5)
            bubble_y = mask_y + random.randint(-5, 5)
            return bubble_x, bubble_y
        
        return None

class Enemy(GameObject):
    """Clase base para enemigos"""
    
    def __init__(self, x: float, y: float, size: int, speed: float, config: GameConfig):
        super().__init__(x, y, size)
        self.config = config
        self.speed = speed
        self.base_speed = speed
        self.direction = random.uniform(0, 2 * math.pi)
        self.change_direction_timer = random.randint(60, 180)
        self.feared = False
        self.fear_timer = 0
        self.fear_distance = 120
        self.patrol_center_x = x
        self.patrol_center_y = y
        self.patrol_radius = 150
        self.stuck_timer = 0
        self.last_x = x
        self.last_y = y
    
    def update(self, maze: Maze, player: Player):
        """Actualiza el enemigo"""
        # Verificar si está atascado
        if abs(self.x - self.last_x) < 1 and abs(self.y - self.last_y) < 1:
            self.stuck_timer += 1
            if self.stuck_timer > 30:  # Atascado por medio segundo
                self.direction += random.uniform(math.pi/2, math.pi)
                self.stuck_timer = 0
        else:
            self.stuck_timer = 0
        
        self.last_x = self.x
        self.last_y = self.y
        
        # Cambiar dirección ocasionalmente
        self.change_direction_timer -= 1
        if self.change_direction_timer <= 0:
            # Tender a volver al área de patrulla
            to_center_x = self.patrol_center_x - self.x
            to_center_y = self.patrol_center_y - self.y
            distance_to_center = math.sqrt(to_center_x**2 + to_center_y**2)
            
            if distance_to_center > self.patrol_radius:
                # Volver hacia el centro
                self.direction = math.atan2(to_center_y, to_center_x)
                self.direction += random.uniform(-0.5, 0.5)
            else:
                # Movimiento aleatorio
                self.direction += random.uniform(-1, 1)
            
            self.change_direction_timer = random.randint(60, 180)
        
        # Comportamiento de miedo al arpón
        distance_to_player = self.distance_to(player)
        
        if player.has_harpoon and distance_to_player < self.fear_distance:
            if not self.feared:
                self.feared = True
                self.fear_timer = 180  # 3 segundos
                # Huir del jugador
                flee_angle = math.atan2(self.y - player.y, self.x - player.x)
                self.direction = flee_angle + random.uniform(-0.3, 0.3)
        
        # Actualizar miedo
        if self.feared:
            self.fear_timer -= 1
            if self.fear_timer <= 0:
                self.feared = False
        
        # Calcular velocidad
        speed_multiplier = 2.5 if self.feared else 1.0
        current_speed = self.speed * speed_multiplier
        
        # Movimiento
        dx = math.cos(self.direction) * current_speed
        dy = math.sin(self.direction) * current_speed
        
        new_x = self.x + dx
        new_y = self.y + dy
        
        # Verificar colisiones con paredes
        if not maze.is_wall(new_x, self.y):
            self.x = new_x
        else:
            self.direction = math.pi - self.direction + random.uniform(-0.3, 0.3)
        
        if not maze.is_wall(self.x, new_y):
            self.y = new_y
        else:
            self.direction = -self.direction + random.uniform(-0.3, 0.3)
        
        # Mantener dentro de la pantalla
        if self.x <= self.size or self.x >= SCREEN_WIDTH - self.size:
            self.direction = math.pi - self.direction
        if self.y <= self.size or self.y >= SCREEN_HEIGHT - self.size:
            self.direction = -self.direction
        
        self.x = max(self.size, min(SCREEN_WIDTH - self.size, self.x))
        self.y = max(self.size, min(SCREEN_HEIGHT - self.size, self.y))
        
        self.animation_time += 1
        self.update_rect()

class Shark(Enemy):
    """Tiburón enemigo"""
    
    def __init__(self, x: float, y: float, config: GameConfig):
        super().__init__(x, y, 35, config.shark_speed, config)
        self.tail_animation = 0
    
    def update(self, maze: Maze, player: Player):
        super().update(maze, player)
        self.tail_animation += 0.2
    
    def draw(self, screen: pygame.Surface):
        """Dibuja el tiburón con animaciones detalladas"""
        color = COLORS['shark_dark'] if self.feared else COLORS['shark_gray']
        
        # Cuerpo principal
        body_length = 35
        body_height = 16
        
        # Animación de natación
        swim_offset = math.sin(self.tail_animation) * 2
        
        body_rect = pygame.Rect(
            int(self.x - body_length//2), 
            int(self.y - body_height//2 + swim_offset), 
            body_length, body_height
        )
        pygame.draw.ellipse(screen, color, body_rect)
        
        # Cabeza más puntiaguda
        head_points = [
            (int(self.x + body_length//2), int(self.y)),
            (int(self.x + body_length//2 - 8), int(self.y - 6)),
            (int(self.x + body_length//2 - 8), int(self.y + 6))
        ]
        pygame.draw.polygon(screen, color, head_points)
        
        # Aleta dorsal
        dorsal_x = self.x - 5
        dorsal_y = self.y - body_height//2 - 8 + swim_offset
        dorsal_points = [
            (int(dorsal_x), int(dorsal_y)),
            (int(dorsal_x - 8), int(dorsal_y - 12)),
            (int(dorsal_x + 8), int(dorsal_y))
        ]
        pygame.draw.polygon(screen, color, dorsal_points)
        
        # Cola con animación
        tail_offset = math.sin(self.tail_animation) * 8
        tail_x = self.x - body_length//2 - 10
        tail_y = self.y + tail_offset
        
        tail_points = [
            (int(tail_x), int(tail_y)),
            (int(tail_x - 12), int(tail_y - 8)),
            (int(tail_x - 8), int(tail_y)),
            (int(tail_x - 12), int(tail_y + 8))
        ]
        pygame.draw.polygon(screen, color, tail_points)
        
        # Aletas pectorales
        pectoral_y_offset = math.sin(self.tail_animation + math.pi/4) * 3
        pectoral_points = [
            (int(self.x + 5), int(self.y + pectoral_y_offset)),
            (int(self.x - 5), int(self.y + 10 + pectoral_y_offset)),
            (int(self.x + 10), int(self.y + 8 + pectoral_y_offset))
        ]
        pygame.draw.polygon(screen, color, pectoral_points)
        
        # Ojo
        eye_x = int(self.x + 8)
        eye_y = int(self.y - 3)
        pygame.draw.circle(screen, (255, 255, 255), (eye_x, eye_y), 3)
        pygame.draw.circle(screen, (0, 0, 0), (eye_x, eye_y), 2)
        
        # Dientes si no tiene miedo
        if not self.feared:
            for i in range(3):
                tooth_x = int(self.x + body_length//2 - 8 + i * 3)
                tooth_y = int(self.y + 2)
                pygame.draw.polygon(screen, (255, 255, 255), [
                    (tooth_x, tooth_y),
                    (tooth_x + 1, tooth_y + 3),
                    (tooth_x + 2, tooth_y)
                ])

class Jellyfish(Enemy):
    """Medusa enemiga"""
    
    def __init__(self, x: float, y: float, config: GameConfig):
        super().__init__(x, y, 28, config.jellyfish_speed, config)
        self.pulse_phase = random.uniform(0, 2 * math.pi)
        self.tentacle_phases = [random.uniform(0, 2 * math.pi) for _ in range(8)]
    
    def update(self, maze: Maze, player: Player):
        super().update(maze, player)
        self.pulse_phase += 0.08
        for i in range(len(self.tentacle_phases)):
            self.tentacle_phases[i] += random.uniform(0.05, 0.15)
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la medusa con animaciones detalladas"""
        base_color = COLORS['jellyfish_light'] if self.feared else COLORS['jellyfish_purple']
        
        # Pulsación de la campana
        pulse = math.sin(self.pulse_phase) * 4
        bell_radius = int(14 + pulse)
        
        # Campana principal
        pygame.draw.circle(screen, base_color, (int(self.x), int(self.y)), bell_radius)
        
        # Gradiente en la campana
        for i in range(3):
            inner_radius = bell_radius - (i + 1) * 3
            if inner_radius > 0:
                alpha_color = tuple(min(255, c + 20 * i) for c in base_color)
                pygame.draw.circle(screen, alpha_color, (int(self.x), int(self.y)), inner_radius)
        
        # Tentáculos animados
        tentacle_count = 8
        for i in range(tentacle_count):
            angle = (i / tentacle_count) * 2 * math.pi
            
            # Posición base del tentáculo
            base_x = self.x + math.cos(angle) * (bell_radius - 2)
            base_y = self.y + math.sin(angle) * (bell_radius - 2)
            
            # Animación del tentáculo
            tentacle_wave = math.sin(self.tentacle_phases[i]) * 15
            tentacle_length = 20 + tentacle_wave
            
            # Dibujar tentáculo como línea ondulada
            segments = 5
            for seg in range(segments):
                t = seg / segments
                
                # Posición del segmento
                seg_angle = angle + math.sin(self.tentacle_phases[i] + t * math.pi) * 0.5
                seg_x = base_x + math.cos(seg_angle) * (tentacle_length * t)
                seg_y = base_y + math.sin(seg_angle) * (tentacle_length * t)
                
                # Siguiente segmento
                next_t = (seg + 1) / segments
                next_seg_angle = angle + math.sin(self.tentacle_phases[i] + next_t * math.pi) * 0.5
                next_seg_x = base_x + math.cos(next_seg_angle) * (tentacle_length * next_t)
                next_seg_y = base_y + math.sin(next_seg_angle) * (tentacle_length * next_t)
                
                # Grosor del tentáculo (más grueso en la base)
                thickness = max(1, int(3 * (1 - t)))
                
                pygame.draw.line(screen, base_color, 
                               (int(seg_x), int(seg_y)), 
                               (int(next_seg_x), int(next_seg_y)), thickness)
        
        # Detalles bioluminiscentes
        if not self.feared:
            for i in range(4):
                detail_angle = (i / 4) * 2 * math.pi + self.pulse_phase
                detail_x = int(self.x + math.cos(detail_angle) * 6)
                detail_y = int(self.y + math.sin(detail_angle) * 6)
                pygame.draw.circle(screen, COLORS['jellyfish_light'], (detail_x, detail_y), 2)

class Pearl(GameObject):
    """Perla normal recolectable"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 14)
        self.shine_phase = random.uniform(0, 2 * math.pi)
        self.points = 10
        self.bob_phase = random.uniform(0, 2 * math.pi)
        self.base_y = y
    
    def update(self):
        """Actualiza la perla"""
        self.shine_phase += 0.1
        self.bob_phase += 0.05
        self.y = self.base_y + math.sin(self.bob_phase) * 3
        self.update_rect()
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la perla con efectos de brillo"""
        # Brillo principal
        shine_intensity = (math.sin(self.shine_phase) + 1) / 2
        shine_color = tuple(int(255 * shine_intensity) for _ in range(3))
        
        # Perla base
        pygame.draw.circle(screen, COLORS['pearl_white'], (int(self.x), int(self.y)), 7)
        
        # Brillo animado
        shine_radius = int(3 + shine_intensity * 2)
        pygame.draw.circle(screen, shine_color, 
                         (int(self.x - 2), int(self.y - 2)), shine_radius)
        
        # Reflejo
        pygame.draw.circle(screen, COLORS['pearl_shine'], 
                         (int(self.x - 3), int(self.y - 3)), 2)
        
        # Partículas de brillo ocasionales
        if random.random() < 0.1:
            for _ in range(2):
                sparkle_x = self.x + random.randint(-10, 10)
                sparkle_y = self.y + random.randint(-10, 10)
                pygame.draw.circle(screen, COLORS['pearl_shine'], 
                                 (int(sparkle_x), int(sparkle_y)), 1)

class GiantPearl(GameObject):
    """Perla gigante que otorga arpón"""
    
    def __init__(self, x: float, y: float):
        super().__init__(x, y, 24)
        self.shine_phase = random.uniform(0, 2 * math.pi)
        self.points = 50
        self.bob_phase = random.uniform(0, 2 * math.pi)
        self.base_y = y
        self.aura_phase = 0
    
    def update(self):
        """Actualiza la perla gigante"""
        self.shine_phase += 0.05
        self.bob_phase += 0.03
        self.aura_phase += 0.1
        self.y = self.base_y + math.sin(self.bob_phase) * 5
        self.update_rect()
    
    def draw(self, screen: pygame.Surface):
        """Dibuja la perla gigante con efectos especiales"""
        # Aura dorada
        aura_radius = int(15 + math.sin(self.aura_phase) * 5)
        aura_color = (*COLORS['giant_pearl'], 50)
        
        # Dibujar múltiples capas de aura
        for i in range(3):
            radius = aura_radius - i * 3
            if radius > 0:
                # Simular transparencia con múltiples círculos
                pygame.draw.circle(screen, COLORS['giant_pearl'], 
                                 (int(self.x), int(self.y)), radius, 1)
        
        # Perla principal
        shine_intensity = (math.sin(self.shine_phase) + 1) / 2
        main_color = tuple(int(c * (0.8 + 0.2 * shine_intensity)) for c in COLORS['giant_pearl'])
        
        pygame.draw.circle(screen, main_color, (int(self.x), int(self.y)), 12)
        
        # Brillo interno
        inner_shine = tuple(min(255, int(c * 1.2)) for c in main_color)
        pygame.draw.circle(screen, inner_shine, (int(self.x), int(self.y)), 8)
        
        # Reflejo principal
        pygame.draw.circle(screen, COLORS['pearl_shine'], 
                         (int(self.x - 4), int(self.y - 4)), 4)
        
        # Destellos
        for i in range(6):
            angle = (i / 6) * 2 * math.pi + self.shine_phase
            sparkle_x = self.x + math.cos(angle) * 18
            sparkle_y = self.y + math.sin(angle) * 18
            pygame.draw.circle(screen, COLORS['pearl_shine'], 
                             (int(sparkle_x), int(sparkle_y)), 2)
        
        # Partículas doradas
        if random.random() < 0.3:
            for _ in range(3):
                particle_angle = random.uniform(0, 2 * math.pi)
                particle_distance = random.uniform(15, 25)
                particle_x = self.x + math.cos(particle_angle) * particle_distance
                particle_y = self.y + math.sin(particle_angle) * particle_distance
                pygame.draw.circle(screen, COLORS['giant_pearl'], 
                                 (int(particle_x), int(particle_y)), 1)

class SubmarineExplorerGame:
    """Clase principal del juego El Explorador Submarino"""
    
    def __init__(self):
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("El Explorador Submarino")
        self.clock = pygame.time.Clock()
        
        # Fuentes
        self.title_font = pygame.font.Font(None, 72)
        self.menu_font = pygame.font.Font(None, 48)
        self.game_font = pygame.font.Font(None, 36)
        self.small_font = pygame.font.Font(None, 24)
        
        # Configuración del juego
        self.config = GameConfig()
        
        # Estado del juego
        self.state = GameState.MENU
        self.score_manager = ScoreManager()
        self.particle_system = ParticleSystem()
        
        # Variables del juego
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_time = 0
        
        # Objetos del juego
        self.player = None
        self.maze = None
        self.enemies = []
        self.pearls = []
        
        # Efectos y animaciones
        self.menu_animation_time = 0
        self.background_bubbles = []
        self.screen_shake = 0
        
        self.init_background_effects()
    
    def init_background_effects(self):
        """Inicializa efectos de fondo"""
        # Crear burbujas de fondo para el menú
        for _ in range(20):
            x = random.randint(0, SCREEN_WIDTH)
            y = random.randint(0, SCREEN_HEIGHT)
            self.background_bubbles.append(Bubble(x, y))
    
    def reset_game(self):
        """Reinicia el juego"""
        self.score = 0
        self.lives = 3
        self.level = 1
        self.game_time = 0
        self.screen_shake = 0
        
        # Crear laberinto
        self.maze = Maze(self.config.maze_width, self.config.maze_height)
        
        # Crear jugador
        start_x, start_y = self.maze.get_free_position()
        self.player = Player(start_x, start_y, self.config)
        
        # Crear enemigos
        self.enemies = []
        for _ in range(self.config.enemy_count):
            enemy_x, enemy_y = self.maze.get_free_position()
            # Asegurar que no aparezcan muy cerca del jugador
            while self.player.distance_to(GameObject(enemy_x, enemy_y, 1)) < 100:
                enemy_x, enemy_y = self.maze.get_free_position()
            
            if random.choice([True, False]):
                self.enemies.append(Shark(enemy_x, enemy_y, self.config))
            else:
                self.enemies.append(Jellyfish(enemy_x, enemy_y, self.config))
        
        # Crear perlas
        self.pearls = []
        
        # Perlas normales
        for _ in range(self.config.pearl_count):
            pearl_x, pearl_y = self.maze.get_free_position()
            self.pearls.append(Pearl(pearl_x, pearl_y))
        
        # Perlas gigantes
        for _ in range(self.config.giant_pearl_count):
            giant_pearl_x, giant_pearl_y = self.maze.get_free_position()
            self.pearls.append(GiantPearl(giant_pearl_x, giant_pearl_y))
        
        # Limpiar sistema de partículas
        self.particle_system = ParticleSystem()
    
    def handle_events(self):
        """Maneja eventos del juego"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            if event.type == pygame.KEYDOWN:
                if self.state == GameState.MENU:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.PLAYING
                        self.reset_game()
                    elif event.key == pygame.K_i:
                        self.state = GameState.INSTRUCTIONS
                    elif event.key == pygame.K_h:
                        self.state = GameState.HIGH_SCORES
                    elif event.key == pygame.K_ESCAPE:
                        return False
                
                elif self.state == GameState.INSTRUCTIONS:
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                        self.state = GameState.MENU
                
                elif self.state == GameState.HIGH_SCORES:
                    if event.key in [pygame.K_ESCAPE, pygame.K_SPACE]:
                        self.state = GameState.MENU
                
                elif self.state == GameState.PLAYING:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PAUSED
                
                elif self.state == GameState.PAUSED:
                    if event.key == pygame.K_ESCAPE:
                        self.state = GameState.PLAYING
                    elif event.key == pygame.K_m:
                        self.state = GameState.MENU
                
                elif self.state in [GameState.GAME_OVER, GameState.VICTORY]:
                    if event.key == pygame.K_SPACE:
                        self.state = GameState.MENU
                    elif event.key == pygame.K_r:
                        self.state = GameState.PLAYING
                        self.reset_game()
        
        return True
    
    def update(self):
        """Actualiza la lógica del juego"""
        # Actualizar animaciones globales
        self.menu_animation_time += 0.05
        
        # Actualizar burbujas de fondo
        self.background_bubbles = [b for b in self.background_bubbles if b.update()]
        
        # Añadir nuevas burbujas de fondo
        if len(self.background_bubbles) < 15:
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 10
            self.background_bubbles.append(Bubble(x, y))
        
        # Actualizar según el estado
        if self.state == GameState.PLAYING:
            self.update_game()
        
        # Actualizar sistema de partículas
        self.particle_system.update()
        
        # Reducir screen shake
        if self.screen_shake > 0:
            self.screen_shake -= 1
    
    def update_game(self):
        """Actualiza la lógica del juego principal"""
        self.game_time += 1
        
        # Actualizar laberinto
        self.maze.update()
        
        # Actualizar jugador
        self.player.update(self.maze)
        
        # Generar burbujas del jugador
        bubble_pos = self.player.draw(self.screen)
        if bubble_pos and random.random() < 0.3:
            self.particle_system.add_bubble(bubble_pos[0], bubble_pos[1])
        
        # Actualizar enemigos
        for enemy in self.enemies:
            enemy.update(self.maze, self.player)
        
        # Actualizar perlas
        for pearl in self.pearls:
            pearl.update()
        
        # Verificar colisiones con perlas
        for pearl in self.pearls[:]:
            if self.player.collides_with(pearl):
                self.score += pearl.points
                
                # Efectos especiales para perla gigante
                if isinstance(pearl, GiantPearl):
                    self.player.give_harpoon()
                    self.particle_system.add_explosion(pearl.x, pearl.y, COLORS['giant_pearl'])
                    self.screen_shake = 10
                else:
                    self.particle_system.add_explosion(pearl.x, pearl.y, COLORS['pearl_white'])
                
                self.pearls.remove(pearl)
        
        # Verificar colisiones con enemigos
        for enemy in self.enemies:
            if self.player.collides_with(enemy):
                if self.player.take_damage():
                    self.lives -= 1
                    self.particle_system.add_explosion(self.player.x, self.player.y, COLORS['danger_red'])
                    self.screen_shake = 15
                    
                    if self.lives <= 0:
                        self.score_manager.save_score(self.score, False)
                        self.state = GameState.GAME_OVER
                        return
        
        # Verificar victoria (todas las perlas recolectadas)
        if not self.pearls:
            bonus_score = 1000 + (self.lives * 200)
            self.score += bonus_score
            self.score_manager.save_score(self.score, True)
            self.state = GameState.VICTORY
        
        # Generar burbujas ambientales
        if self.game_time % self.config.bubble_spawn_rate == 0:
            x = random.randint(0, SCREEN_WIDTH)
            y = SCREEN_HEIGHT + 10
            self.particle_system.add_bubble(x, y)
    
    def draw_background(self):
        """Dibuja el fondo submarino"""
        # Gradiente de agua
        for y in range(SCREEN_HEIGHT):
            ratio = y / SCREEN_HEIGHT
            color = (
                int(COLORS['water_deep'][0] + (COLORS['water_light'][0] - COLORS['water_deep'][0]) * ratio),
                int(COLORS['water_deep'][1] + (COLORS['water_light'][1] - COLORS['water_deep'][1]) * ratio),
                int(COLORS['water_deep'][2] + (COLORS['water_light'][2] - COLORS['water_deep'][2]) * ratio)
            )
            pygame.draw.line(self.screen, color, (0, y), (SCREEN_WIDTH, y))
        
        # Burbujas de fondo
        for bubble in self.background_bubbles:
            bubble.draw(self.screen)
    
    def draw_menu(self):
        """Dibuja el menú principal"""
        self.draw_background()
        
        # Título con animación
        title_y = 150 + math.sin(self.menu_animation_time) * 10
        title_text = self.title_font.render("EL EXPLORADOR", True, COLORS['text_gold'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, title_y))
        self.screen.blit(title_text, title_rect)
        
        subtitle_text = self.title_font.render("SUBMARINO", True, COLORS['text_gold'])
        subtitle_rect = subtitle_text.get_rect(center=(SCREEN_WIDTH//2, title_y + 80))
        self.screen.blit(subtitle_text, subtitle_rect)
        
        # Decoración del título
        for i in range(5):
            angle = self.menu_animation_time + i * (2 * math.pi / 5)
            deco_x = SCREEN_WIDTH//2 + math.cos(angle) * 200
            deco_y = title_y + 40 + math.sin(angle) * 30
            pygame.draw.circle(self.screen, COLORS['pearl_white'], (int(deco_x), int(deco_y)), 4)
        
        # Menú de opciones
        menu_options = [
            ("ESPACIO - Jugar", COLORS['text_white']),
            ("I - Instrucciones", COLORS['text_white']),
            ("H - Puntuaciones", COLORS['text_white']),
            ("ESC - Salir", COLORS['text_white'])
        ]
        
        start_y = 400
        for i, (option, color) in enumerate(menu_options):
            option_y = start_y + i * 50 + math.sin(self.menu_animation_time + i) * 5
            option_text = self.menu_font.render(option, True, color)
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, option_y))
            self.screen.blit(option_text, option_rect)
        
        # Puntuación más alta
        high_score = self.score_manager.get_high_score()
        if high_score > 0:
            high_score_text = self.small_font.render(
                f"Mejor Puntuación: {high_score}", True, COLORS['text_gold']
            )
            high_score_rect = high_score_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 50))
            self.screen.blit(high_score_text, high_score_rect)
    
    def draw_instructions(self):
        """Dibuja las instrucciones del juego"""
        self.draw_background()
        
        title_text = self.menu_font.render("INSTRUCCIONES", True, COLORS['text_gold'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        instructions = [
            "OBJETIVO:",
            "• Recolecta todas las perlas del arrecife de coral",
            "• Evita a los tiburones y medusas",
            "",
            "CONTROLES:",
            "• WASD o Flechas - Mover buzo",
            "• ESC - Pausar juego",
            "",
            "ELEMENTOS DEL JUEGO:",
            "• Perlas blancas: +10 puntos",
            "• Perlas doradas: +50 puntos + Arpón temporal",
            "• El arpón ahuyenta a los enemigos",
            "• Tienes 3 vidas",
            "",
            "ENEMIGOS:",
            "• Tiburones: Rápidos y agresivos",
            "• Medusas: Lentas pero impredecibles",
            "",
            "ESPACIO - Volver al menú"
        ]
        
        start_y = 180
        for i, instruction in enumerate(instructions):
            color = COLORS['text_gold'] if instruction.endswith(":") else COLORS['text_white']
            font = self.game_font if instruction.endswith(":") else self.small_font
            
            instruction_text = font.render(instruction, True, color)
            instruction_rect = instruction_text.get_rect(center=(SCREEN_WIDTH//2, start_y + i * 25))
            self.screen.blit(instruction_text, instruction_rect)
    
    def draw_high_scores(self):
        """Dibuja las mejores puntuaciones"""
        self.draw_background()
        
        title_text = self.menu_font.render("MEJORES PUNTUACIONES", True, COLORS['text_gold'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 100))
        self.screen.blit(title_text, title_rect)
        
        scores = self.score_manager.get_top_scores()
        
        if not scores:
            no_scores_text = self.game_font.render("No hay puntuaciones registradas", True, COLORS['text_white'])
            no_scores_rect = no_scores_text.get_rect(center=(SCREEN_WIDTH//2, 300))
            self.screen.blit(no_scores_text, no_scores_rect)
        else:
            start_y = 180
            for i, score_data in enumerate(scores):
                rank = i + 1
                score = score_data['score']
                date = score_data['date']
                completed = score_data.get('completed', False)
                
                # Número de ranking
                rank_text = self.game_font.render(f"{rank}.", True, COLORS['text_gold'])
                rank_rect = rank_text.get_rect(right=SCREEN_WIDTH//2 - 200, y=start_y + i * 40)
                self.screen.blit(rank_text, rank_rect)
                
                # Puntuación
                score_text = self.game_font.render(f"{score:,}", True, COLORS['text_white'])
                score_rect = score_text.get_rect(left=SCREEN_WIDTH//2 - 180, y=start_y + i * 40)
                self.screen.blit(score_text, score_rect)
                
                # Indicador de nivel completado
                if completed:
                    complete_text = self.small_font.render("★ COMPLETADO", True, COLORS['success_green'])
                    complete_rect = complete_text.get_rect(left=SCREEN_WIDTH//2 - 50, y=start_y + i * 40 + 5)
                    self.screen.blit(complete_text, complete_rect)
                
                # Fecha
                date_text = self.small_font.render(date, True, COLORS['text_white'])
                date_rect = date_text.get_rect(right=SCREEN_WIDTH//2 + 200, y=start_y + i * 40 + 5)
                self.screen.blit(date_text, date_rect)
        
        # Instrucción para volver
        back_text = self.small_font.render("ESPACIO - Volver al menú", True, COLORS['text_white'])
        back_rect = back_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT - 100))
        self.screen.blit(back_text, back_rect)
    
    def draw_game(self):
        """Dibuja el juego principal"""
        # Aplicar screen shake
        shake_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Fondo
        self.draw_background()
        
        # Crear superficie temporal para el shake
        game_surface = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        
        # Dibujar laberinto
        self.maze.draw(game_surface)
        
        # Dibujar perlas
        for pearl in self.pearls:
            pearl.draw(game_surface)
        
        # Dibujar enemigos
        for enemy in self.enemies:
            enemy.draw(game_surface)
        
        # Dibujar jugador
        self.player.draw(game_surface)
        
        # Dibujar partículas
        self.particle_system.draw(game_surface)
        
        # Aplicar shake y dibujar en pantalla principal
        self.screen.blit(game_surface, (shake_x, shake_y))
        
        # HUD
        self.draw_hud()
    
    def draw_hud(self):
        """Dibuja la interfaz de usuario"""
        # Panel de información
        hud_surface = pygame.Surface((300, 150))
        hud_surface.set_alpha(200)
        hud_surface.fill((0, 0, 0))
        self.screen.blit(hud_surface, (10, 10))
        
        # Puntuación
        score_text = self.game_font.render(f"Puntuación: {self.score:,}", True, COLORS['text_white'])
        self.screen.blit(score_text, (20, 20))
        
        # Vidas
        lives_text = self.game_font.render(f"Vidas: {self.lives}", True, COLORS['text_white'])
        self.screen.blit(lives_text, (20, 50))
        
        # Perlas restantes
        pearls_remaining = len(self.pearls)
        pearls_text = self.game_font.render(f"Perlas: {pearls_remaining}", True, COLORS['text_white'])
        self.screen.blit(pearls_text, (20, 80))
        
        # Tiempo de arpón
        if self.player.has_harpoon:
            harpoon_ratio = self.player.harpoon_time / self.player.config.harpoon_duration
            harpoon_text = self.small_font.render(f"Arpón: {harpoon_ratio:.0%}", True, COLORS['harpoon_silver'])
            self.screen.blit(harpoon_text, (20, 110))
            
            # Barra de arpón
            bar_width = 100
            bar_height = 8
            bar_rect = pygame.Rect(20, 130, bar_width, bar_height)
            pygame.draw.rect(self.screen, COLORS['shark_gray'], bar_rect)
            
            fill_width = int(bar_width * harpoon_ratio)
            fill_rect = pygame.Rect(20, 130, fill_width, bar_height)
            pygame.draw.rect(self.screen, COLORS['harpoon_silver'], fill_rect)
        
        # Indicador de invulnerabilidad
        if self.player.invulnerable:
            invuln_text = self.small_font.render("INVULNERABLE", True, COLORS['success_green'])
            self.screen.blit(invuln_text, (20, 140))
        
        # Mini mapa (opcional)
        self.draw_minimap()
    
    def draw_minimap(self):
        """Dibuja un mini mapa"""
        minimap_size = 150
        minimap_surface = pygame.Surface((minimap_size, minimap_size))
        minimap_surface.set_alpha(180)
        minimap_surface.fill((0, 0, 50))
        
        # Escala del mini mapa
        scale_x = minimap_size / SCREEN_WIDTH
        scale_y = minimap_size / SCREEN_HEIGHT
        
        # Dibujar paredes del laberinto
        for y in range(self.maze.height):
            for x in range(self.maze.width):
                if self.maze.grid[y][x]:
                    mini_x = int(x * CELL_SIZE * scale_x)
                    mini_y = int(y * CELL_SIZE * scale_y)
                    mini_size = max(1, int(CELL_SIZE * scale_x))
                    pygame.draw.rect(minimap_surface, COLORS['coral_pink'], 
                                   (mini_x, mini_y, mini_size, mini_size))
        
        # Dibujar jugador
        player_x = int(self.player.x * scale_x)
        player_y = int(self.player.y * scale_y)
        pygame.draw.circle(minimap_surface, COLORS['diver_blue'], (player_x, player_y), 3)
        
        # Dibujar enemigos
        for enemy in self.enemies:
            enemy_x = int(enemy.x * scale_x)
            enemy_y = int(enemy.y * scale_y)
            color = COLORS['shark_gray'] if isinstance(enemy, Shark) else COLORS['jellyfish_purple']
            pygame.draw.circle(minimap_surface, color, (enemy_x, enemy_y), 2)
        
        # Dibujar perlas
        for pearl in self.pearls:
            pearl_x = int(pearl.x * scale_x)
            pearl_y = int(pearl.y * scale_y)
            color = COLORS['giant_pearl'] if isinstance(pearl, GiantPearl) else COLORS['pearl_white']
            pygame.draw.circle(minimap_surface, color, (pearl_x, pearl_y), 1)
        
        # Dibujar mini mapa en pantalla
        minimap_pos = (SCREEN_WIDTH - minimap_size - 10, 10)
        self.screen.blit(minimap_surface, minimap_pos)
        
        # Marco del mini mapa
        pygame.draw.rect(self.screen, COLORS['text_white'], (*minimap_pos, minimap_size, minimap_size), 2)
    
    def draw_pause(self):
        """Dibuja la pantalla de pausa"""
        self.draw_game()
        
        # Overlay semi-transparente
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(150)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Texto de pausa
        pause_text = self.menu_font.render("JUEGO PAUSADO", True, COLORS['text_white'])
        pause_rect = pause_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 100))
        self.screen.blit(pause_text, pause_rect)
        
        # Opciones
        options = [
            "ESC - Continuar",
            "M - Menú principal"
        ]
        
        for i, option in enumerate(options):
            option_text = self.game_font.render(option, True, COLORS['text_white'])
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, SCREEN_HEIGHT//2 - 20 + i * 40))
            self.screen.blit(option_text, option_rect)
    
    def draw_game_over(self):
        """Dibuja la pantalla de fin de juego"""
        self.draw_background()
        
        # Título
        title_text = self.menu_font.render("JUEGO TERMINADO", True, COLORS['danger_red'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, 200))
        self.screen.blit(title_text, title_rect)
        
        # Puntuación final
        score_text = self.game_font.render(f"Puntuación Final: {self.score:,}", True, COLORS['text_white'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 300))
        self.screen.blit(score_text, score_rect)
        
        # Estadísticas
        pearls_collected = self.config.pearl_count + self.config.giant_pearl_count - len(self.pearls)
        total_pearls = self.config.pearl_count + self.config.giant_pearl_count
        
        stats_text = self.small_font.render(
            f"Perlas recolectadas: {pearls_collected}/{total_pearls}", 
            True, COLORS['text_white']
        )
        stats_rect = stats_text.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(stats_text, stats_rect)
        
        # Mejor puntuación
        high_score = self.score_manager.get_high_score()
        if self.score == high_score and high_score > 0:
            new_record_text = self.game_font.render("¡NUEVO RÉCORD!", True, COLORS['text_gold'])
            new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH//2, 400))
            self.screen.blit(new_record_text, new_record_rect)
        else:
            best_text = self.small_font.render(f"Mejor puntuación: {high_score:,}", True, COLORS['text_gold'])
            best_rect = best_text.get_rect(center=(SCREEN_WIDTH//2, 400))
            self.screen.blit(best_text, best_rect)
        
        # Opciones
        options = [
            "R - Jugar de nuevo",
            "ESPACIO - Menú principal"
        ]
        
        for i, option in enumerate(options):
            option_text = self.game_font.render(option, True, COLORS['text_white'])
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, 500 + i * 40))
            self.screen.blit(option_text, option_rect)
    
    def draw_victory(self):
        """Dibuja la pantalla de victoria"""
        self.draw_background()
        
        # Título animado
        title_y = 200 + math.sin(self.menu_animation_time * 2) * 10
        title_text = self.menu_font.render("¡NIVEL COMPLETADO!", True, COLORS['success_green'])
        title_rect = title_text.get_rect(center=(SCREEN_WIDTH//2, title_y))
        self.screen.blit(title_text, title_rect)
        
        # Efectos de celebración
        for i in range(10):
            angle = self.menu_animation_time * 2 + i * (2 * math.pi / 10)
            star_x = SCREEN_WIDTH//2 + math.cos(angle) * 100
            star_y = title_y + math.sin(angle) * 50
            pygame.draw.circle(self.screen, COLORS['text_gold'], (int(star_x), int(star_y)), 3)
        
        # Puntuación final con bonus
        bonus_score = 1000 + (self.lives * 200)
        score_text = self.game_font.render(f"Puntuación Final: {self.score:,}", True, COLORS['text_white'])
        score_rect = score_text.get_rect(center=(SCREEN_WIDTH//2, 320))
        self.screen.blit(score_text, score_rect)
        
        bonus_text = self.small_font.render(f"Bonus por completar: +{bonus_score:,}", True, COLORS['success_green'])
        bonus_rect = bonus_text.get_rect(center=(SCREEN_WIDTH//2, 350))
        self.screen.blit(bonus_text, bonus_rect)
        
        # Estadísticas perfectas
        perfect_text = self.game_font.render("¡ARRECIFE COMPLETAMENTE EXPLORADO!", True, COLORS['text_gold'])
        perfect_rect = perfect_text.get_rect(center=(SCREEN_WIDTH//2, 400))
        self.screen.blit(perfect_text, perfect_rect)
        
        # Mejor puntuación
        high_score = self.score_manager.get_high_score()
        if self.score == high_score:
            new_record_text = self.game_font.render("¡NUEVO RÉCORD MUNDIAL!", True, COLORS['text_gold'])
            new_record_rect = new_record_text.get_rect(center=(SCREEN_WIDTH//2, 450))
            self.screen.blit(new_record_text, new_record_rect)
        
        # Opciones
        options = [
            "R - Jugar de nuevo",
            "ESPACIO - Menú principal"
        ]
        
        for i, option in enumerate(options):
            option_text = self.game_font.render(option, True, COLORS['text_white'])
            option_rect = option_text.get_rect(center=(SCREEN_WIDTH//2, 550 + i * 40))
            self.screen.blit(option_text, option_rect)
    
    def draw(self):
        """Dibuja según el estado actual del juego"""
        if self.state == GameState.MENU:
            self.draw_menu()
        elif self.state == GameState.INSTRUCTIONS:
            self.draw_instructions()
        elif self.state == GameState.HIGH_SCORES:
            self.draw_high_scores()
        elif self.state == GameState.PLAYING:
            self.draw_game()
        elif self.state == GameState.PAUSED:
            self.draw_pause()
        elif self.state == GameState.GAME_OVER:
            self.draw_game_over()
        elif self.state == GameState.VICTORY:
            self.draw_victory()
        
        pygame.display.flip()
    
    def run(self):
        """Bucle principal del juego"""
        running = True
        
        print("* Iniciando el juego \n Espera, por favor...")
        print("* Cargando recursos...")
        print("* Diviértete!")

        while running:
            running = self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)
        
        print("¡Gracias por jugar El Explorador Submarino!")
        pygame.quit()

# Función principal para ejecutar el juego
def main():
    """Función principal del juego"""
    try:
        # Verificar que pygame esté correctamente inicializado
        if not pygame.get_init():
            print("Error: Pygame no se pudo inicializar correctamente")
            return
        
        # Crear y ejecutar el juego
        game = SubmarineExplorerGame()
        game.run()
        
    except Exception as e:
        print(f"Error crítico en el juego: {e}")
        import traceback
        traceback.print_exc()
    finally:
        pygame.quit()

# Ejecutar el juego
if __name__ == "__main__":
    main()