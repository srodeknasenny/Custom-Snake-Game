from enum import Enum
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import random
from matplotlib.patches import Rectangle
import matplotlib.image as mpimg
import numpy as np

TEXTURES = {
    'head_up': mpimg.imread('textures/head_up.png'),
    'head_down': mpimg.imread('textures/head_down.png'),
    'head_left': mpimg.imread('textures/head_left.png'),
    'head_right': mpimg.imread('textures/head_right.png'),
    
    'belly_vertical': mpimg.imread('textures/belly_vertical.png'),
    'belly_horizontal': mpimg.imread('textures/belly_horizontal.png'),
    
    'tail_up': mpimg.imread('textures/tail_up.png'),
    'tail_down': mpimg.imread('textures/tail_down.png'),
    'tail_left': mpimg.imread('textures/tail_left.png'),
    'tail_right': mpimg.imread('textures/tail_right.png'),
    
    'edge_up_right': mpimg.imread('textures/edge_up_right.png'),
    'edge_right_down': mpimg.imread('textures/edge_right_down.png'),
    'edge_down_left': mpimg.imread('textures/edge_down_left.png'),
    'edge_left_up': mpimg.imread('textures/edge_left_up.png'),
    
    'edge_up_left': mpimg.imread('textures/edge_up_left.png'),
    'edge_left_down': mpimg.imread('textures/edge_left_down.png'),
    'edge_down_right': mpimg.imread('textures/edge_down_right.png'),
    'edge_right_up': mpimg.imread('textures/edge_right_up.png'),
    'apple': mpimg.imread('textures/apple.png')
}

BOARD_SIZE = 15

class Direction(Enum):
    UP = (0,1)
    DOWN = (0,-1)
    LEFT = (-1,0)
    RIGHT = (1,0)

class Snake:
    def __init__(self, start_pos = (BOARD_SIZE//2, BOARD_SIZE//2)):
        self.body = [start_pos, ((start_pos[0]), start_pos[1] - 1), ((start_pos[0]), start_pos[1] - 2)]
        self.direction = Direction.UP
        self.score = 1

    def move(self):
        head_pos_x, head_pos_y = self.body[0]
        dx, dy = self.direction.value
        new_head_pos = (head_pos_x + dx, head_pos_y + dy)
        self.body.insert(0, new_head_pos)

    def update_body(self, food_eaten = False):
        if not food_eaten:
            self.body.pop()
        else: 
            self.score+=1

    def change_direction(self, new_direction):
        current_dx, current_dy = self.direction.value
        new_dx, new_dy = new_direction.value
        is_opposite = (new_dx == -current_dx) and (new_dy == -current_dy)
        if not is_opposite:
            self.direction = new_direction

    def _direction_from_positions(self, pos1, pos2):
        dx, dy = pos2[0] - pos1[0], pos2[1] - pos1[1]
        if dx == 1: return Direction.RIGHT
        if dx == -1: return Direction.LEFT
        if dy == 1: return Direction.UP
        if dy == -1: return Direction.DOWN
        return None
    
    def get_texture_info(self, index):
        n = len(self.body)
        if index == 0: 
            return f'head_{self.direction.name.lower()}'

        elif index == n - 1:
            if n > 1:
                tail_dir = self._direction_from_positions(self.body[index], self.body[index-1])
                return f'tail_{tail_dir.name.lower()}'
            return 'tail_up'
        
        else:
            prev_dir = self._direction_from_positions(self.body[index-1], self.body[index])
            next_dir = self._direction_from_positions(self.body[index], self.body[index+1])
            
            if prev_dir and next_dir and prev_dir != next_dir:
                return f'edge_{prev_dir.name.lower()}_{next_dir.name.lower()}'
            
            if next_dir in [Direction.UP, Direction.DOWN]:
                return 'belly_vertical'
            return 'belly_horizontal'
        
class Food:
    def __init__(self, snake):
        self.snake = snake
        max_coord = BOARD_SIZE - 1
        new_pos = (random.randint(0,max_coord), random.randint(0,max_coord))
        while new_pos in snake.body:
            new_pos = (random.randint(0,max_coord), random.randint(0,max_coord))
        self.position = new_pos
    
    def eaten(self):
        return self.position == self.snake.body[0]
    
    def generate_new_position(self):
        max_coord = BOARD_SIZE - 1
        new_pos = (random.randint(0,max_coord), random.randint(0,max_coord))
        while new_pos in self.snake.body:
            new_pos = (random.randint(0,max_coord), random.randint(0,max_coord))
        self.position = new_pos

class Board:
    def __init__(self):
        self.snake = Snake()
        self.input_queue = []
        self.food = Food(self.snake)
        self.game_over = False

    def check_for_death(self):
        head_pos = self.snake.body[0]
        head_x, head_y = head_pos
        if head_x < 0 or head_x >= BOARD_SIZE or \
           head_y < 0 or head_y >= BOARD_SIZE:
            self.game_over = True
            return True

        if head_pos in self.snake.body[1:]:
            self.game_over = True
            return True

        return False    

    def update_board(self):
        if self.game_over:
            return
        if self.input_queue:
            intended_direction = self.input_queue.pop(0) 
            self.snake.change_direction(intended_direction)
        self.snake.move()
        if self.check_for_death():
            return
        food_eaten = self.food.eaten()
        self.snake.update_body(food_eaten=food_eaten)
        if food_eaten:
            self.food.generate_new_position()

    def draw_rectangle_snake(self, ax):
        for (x,y) in self.snake.body:
            snake_rect = Rectangle((x, y), 1, 1, facecolor='green')
            ax.add_patch(snake_rect)

    def draw_rectangle_food(self, ax):
        food_rect = Rectangle(self.food.position, 1, 1, facecolor = 'red')
        ax.add_patch(food_rect)

    def _direction_from_positions(self, pos1, pos2):
        dx, dy = pos2[0] - pos1[0], pos2[1] - pos1[1]
        if dx == 1: return Direction.RIGHT
        if dx == -1: return Direction.LEFT
        if dy == 1: return Direction.UP
        if dy == -1: return Direction.DOWN
        return None
    
    def get_texture_info(self, index):
        if index == 0: 
            return ('head', self.direction)
        n = len(self.body)
        if index == n - 1:
            if n > 1:
                tail_dir = self._direction_from_positions(self.body[index], self.body[index-1])
                return ('tail', tail_dir)
            return ('tail', None)
        
        prev_dir = self._direction_from_positions(self.body[index], self.body[index-1])
        next_dir = self._direction_from_positions(self.body[index+1], self.body[index])
        
        if prev_dir and next_dir and prev_dir != next_dir:
            return ('edge', (prev_dir, next_dir))
        
        return ('belly', next_dir)
    
    def draw_food_texture(self, ax):
        texture = TEXTURES.get('apple')
        apple_pos = self.food.position
        x, y = apple_pos
        if texture is not None:
            ax.imshow(texture, extent=[x, x+1, y, y+1],
                        aspect='equal', origin='upper', interpolation='nearest')
        else:
                ax.add_patch(Rectangle((x, y), 1, 1, facecolor='red'))

    
    def draw_snake_textures(self, ax):
        for i, (x, y) in enumerate(self.snake.body):
            texture_info = self.snake.get_texture_info(i) 
            texture_key = None

            if isinstance(texture_info, str):
                texture_key = texture_info
            
            elif isinstance(texture_info, tuple):
                
                seg_type = texture_info[0]
                
                if seg_type == 'edge':
                    prev_dir, next_dir = texture_info[1]
                    texture_key = f'edge_{prev_dir.name.lower()}_{next_dir.name.lower()}'
                
                elif seg_type in ['head', 'tail']:
                    direction = texture_info[1]
                    if direction:
                        texture_key = f'{seg_type}_{direction.name.lower()}'
                        texture_key = f'{seg_type}_up'

            texture = TEXTURES.get(texture_key)
            
            if texture is not None:
                ax.imshow(texture, extent=[x, x+1, y, y+1],
                          aspect='equal', origin='upper', interpolation='nearest')
            else:
                 ax.add_patch(Rectangle((x, y), 1, 1, facecolor='magenta'))

def initialize_board():
    global board
    board = Board()
    return board

def plot_settings(ax):
    ax.set_xlim(0, BOARD_SIZE)
    ax.set_ylim(0, BOARD_SIZE)
    ax.set_xticks(range(BOARD_SIZE + 1))
    ax.set_yticks(range(BOARD_SIZE + 1))
    ax.grid(True, linestyle='-', linewidth=0.5, color='gray')
    ax.set_aspect('equal')
    ax.set_xticklabels([])
    ax.set_yticklabels([])
    ax.tick_params(axis='x', length=0)
    ax.tick_params(axis='y', length=0)

def on_key_press(event):
    global board, fig, ax, ani, game_over_text
    
    if board.game_over and (event.key == 'r' or event.key == 'R'):
        for p in reversed(ax.patches):
             p.remove()
        initialize_board()
        ani.event_source.start()
        game_over_text.set_visible(False) 
        return 

    if not board.game_over:
        new_direction = None
        if event.key == 'up' or event.key == 'w':
            new_direction = Direction.UP
        elif event.key == 'down' or event.key == 's':
            new_direction = Direction.DOWN
        elif event.key == 'left' or event.key == 'a':
            new_direction = Direction.LEFT
        elif event.key == 'right' or event.key == 'd':
            new_direction = Direction.RIGHT
            
        if new_direction and (not board.input_queue or board.input_queue[-1] != new_direction):
            board.input_queue.append(new_direction)
        

def animate_retro(frame):
    global game_over_text
    board.update_board()

    ax.clear()

    plot_settings(ax)
        
    board.draw_rectangle_snake(ax)
    board.draw_rectangle_food(ax)
    ax.set_title(f"Wynik: {board.snake.score}")

    if board.game_over:
        ani.event_source.stop() 
        game_over_text = ax.text(BOARD_SIZE/2, BOARD_SIZE/2, "GAME OVER", 
                fontsize=30, ha='center', color='red')
        plt.draw() 

    return []

def animate(frame):
    global game_over_text
    board.update_board()

    ax.clear()

    plot_settings(ax)
        
    board.draw_snake_textures(ax)
    board.draw_food_texture(ax)
    ax.set_title(f"Wynik: {board.snake.score}")

    if board.game_over:
        ani.event_source.stop() 
        game_over_text = ax.text(BOARD_SIZE/2, BOARD_SIZE/2, "GAME OVER", 
                fontsize=30, ha='center', color='red')
        plt.draw() 

    return []

def init():
    return []

def run():
    plt.rcParams['keymap.save'].remove('s')
    board = Board()
    fig, ax = plt.subplots(figsize=(8, 8))
    plot_settings(ax)
    fig.canvas.mpl_connect('key_press_event', on_key_press)
    

    ani = FuncAnimation(fig, 
                        animate,
                        init_func=init, 
                        frames=500,
                        interval=150, 
                        blit=False)

    plt.show()