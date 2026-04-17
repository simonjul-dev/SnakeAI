import pygame #load main library to create the game
import random #to generate random numbers for the food position
from enum import Enum #to create an enumeration for the direction of the snake
from collections import namedtuple #to create a named tuple for the point class which will represent the position of the snake and the food
import numpy as np

pygame.init() #initialize the pygame library
font = pygame.font.SysFont('arial.ttf', 25)#create a font object to display the score on the screen

class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4

Point = namedtuple('Point', 'x, y')

#MANUAL OR AUTOMATIC CONTROL
isManual = False #set to True for manual control, False for automatic control

#COLOR DEFINITION IN RGB
WHITE = (255, 255, 255)
RED = (200,0,0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0,0,0)

BLOCK_SIZE = 20 #size of the blocks that make up the snake and the food
SPEED =  10#speed of the game

class SnakeGameAI:
    def _update_ui(self):
        self.display.fill(BLACK) #fill the background with black
        for pt in self.snake: #draw the snake on the screen
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE)) #draw the head of the snake
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x+4, pt.y+4, 12, 12)) #draw the body of the snake

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE)) #draw the food on the screen

        text = font.render("Score: " + str(self.score), True, WHITE) #render the score text
        self.display.blit(text, [0, 0]) #display the score on the screen
        pygame.display.flip() #update the display


    def __init__(self, w=640, h=480):
        self.w = w #width of the game window
        self.h = h #height of the game window
        self.display = pygame.display.set_mode((self.w, self.h)) #create the game window
        pygame.display.set_caption('Snake') #set the title of the game window
        self.clock = pygame.time.Clock() #create a clock object to control the frame rate of the game
        self.reset() #reset the game to its initial state

    def reset(self):
        self.direction = Direction.RIGHT #initial direction of the snake
        self.head = Point(self.w/2, self.h/2) #initial position of the snake's 
        self.snake = [self.head, 
                      Point(self.head.x-BLOCK_SIZE, self.head.y), 
                      Point(self.head.x-(2*BLOCK_SIZE), self.head.y)] #initial position of the snake's body
        self.score = 0 #initial score
        self.food = None #initial position of the food
        self._place_food() #place the food on the screen

    def _place_food(self):
        x = random.randint(0, (self.w-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE #generate a random x position for the food
        y = random.randint(0, (self.h-BLOCK_SIZE )//BLOCK_SIZE )*BLOCK_SIZE #generate a random y position for the food
        self.food = Point(x, y) #set the position of the food

        if self.food in self.snake: #if the food is placed on the snake, place it again
            self._place_food()

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        #check if the snake collides with itself
        if pt in self.snake[1:]:
            return True
        #check if the snake collides with the walls
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        return False

    def play_step(self, action=None):
        #collect user input
        if action is None:
            action = [1, 0, 0]  # default action
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                #quit()
                raise SystemExit
            if event.type == pygame.KEYDOWN:
                if isManual:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        if self.direction == Direction.UP:
                            action = [0, 0, 1]  # turn left
                        elif self.direction == Direction.DOWN:
                            action = [0, 1, 0]  # turn right
                        else:
                             action = [1, 0, 0]  # go straight
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        if self.direction == Direction.UP:
                            action = [0, 1, 0]  # turn right
                        elif self.direction == Direction.DOWN:
                            action = [0, 0, 1]  # turn left
                        else:
                            action = [1, 0, 0]  # go straight
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        if self.direction == Direction.RIGHT:
                            action = [0, 0, 1]  # turn left
                        elif self.direction == Direction.LEFT:
                            action = [0, 1, 0]  # turn right
                        else:
                            action = [1, 0, 0]  # go straight
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        if self.direction == Direction.RIGHT:
                            action = [0, 1, 0]  # turn right
                        elif self.direction == Direction.LEFT:
                            action = [0, 0, 1]  # turn left
                        else:
                            action = [1, 0, 0]  # go straight                            
                else:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        action = [0, 0, 1]  # turn left
                    elif event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        action = [0, 1, 0]  # turn right
                    elif event.key == pygame.K_UP or event.key == pygame.K_w:
                        action = [1, 0, 0]  # go straight
                    elif event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        action = [1, 0, 0]  # go straight

        #move the snake
        self._move(action) #update the head of the snake based on the action
        self.snake.insert(0, self.head) #insert the new head position at the beginning of the snake list

        #check if the snake has collided with itself or the walls
        reward = 0
        game_over = False
        if self.is_collision():
            game_over = True
            reward = -10
            return reward, game_over, self.score

        #check if the snake has eaten the food
        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food() #place a new food on the screen
        else:
            self.snake.pop() #remove the last segment of the snake if it hasn't eaten the food

        #update the UI and clock
        self._update_ui()
        self.clock.tick(SPEED)
        return reward, game_over, self.score

    def _move(self, action):
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP] #list of directions in clockwise order
        idx = clock_wise.index(self.direction) #get the index of the current direction
        if np.array_equal(action, [1, 0, 0]):
            new_dir = clock_wise[idx] #no change in direction
        elif np.array_equal(action, [0, 1, 0]):
            next_idx = (idx + 1) % 4 #turn right
            new_dir = clock_wise[next_idx]
        else: # [0, 0, 1]
            next_idx = (idx - 1) % 4 #turn left
            new_dir = clock_wise[next_idx]
        self.direction = new_dir

        x = self.head.x
        y = self.head.y
        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        self.head = Point(x, y)
        
if __name__ == '__main__':
    game = SnakeGameAI()
    while True:
        reward, game_over, score = game.play_step()
        if game_over:
            break
    pygame.quit()
    print('Final score:', score)