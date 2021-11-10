import random
import pygame
import math
from pygame.locals import *


class ManiacalMaze:
    """Random maze generator and simple navigation"""

    max_x = 6
    max_y = 6
    top_limit = 1000
    map_x = map_y = 0
    top_buffer = 50
    left_buffer = 400
    keep_running = False
    moves = 0
    success = False
    new_map = False
    step_size=5
    # bitwise value names for walls
    bit_u = 1; bit_r = 2; bit_d = 4; bit_l = 8; bit_used = 16
    
    
    def __init__(self):
        # create maze
        self.maze = self.create_maze_array()        
        
        # init screen for graphics
        pygame.init()
        (width, height) = (750, 400)
        self.screen = pygame.display.set_mode((width, height))
        
        self.init_screen()
        pygame.event.clear()
        self.draw_close_map()
        self.update_big_map(True)
        while self.keep_running == False:
            result = self.input_scan()
        # start checking for keyboard presses
    
    def check_valid(self, direction):
        myx = self.map_x; 
        myy = self.map_y
        error = False
        
        if direction == self.bit_u:
            myy-=1
        elif direction == self.bit_r:
            myx+=1            
        elif direction == self.bit_d:
            myy+=1
        elif direction == self.bit_l:
            myx-=1
        
        if myx < 0 or myx > self.max_x-1:
            return False
        elif myy < 0 or myy > self.max_y-1:
            return False
        return True

    def create_maze_array(self):
        # define arrays
        directions = [self.bit_u,self.bit_r,self.bit_d,self.bit_l]
        doors       = [[0 for x in range(self.max_y)] for x in range(self.max_x)] 
        history     = []

        totalnum = self.max_x * self.max_y
        count = 1

        # starting cells
        cur_x = random.randrange(0,self.max_x)
        cur_y = random.randrange(0,self.max_y)

        loopstop = 0

        while count < totalnum:
            loopstop+=1
            if loopstop > 300000:
                print('Loop error!')
                break
            # random exit direction
            loopdir = directions.copy()
            random.shuffle(loopdir)
            # remove any walls that are on the edge and unusable
            for idx, newdoor in enumerate(directions):
                fault = False
                
                # check if edge new direction is outside of the matrix
                if newdoor == 1:
                    if cur_y == 0:
                        loopdir.remove(newdoor)
                    elif doors[cur_x][cur_y-1] > 0:
                        loopdir.remove(newdoor)
                elif newdoor == 2:
                    if cur_x == self.max_x-1:
                        loopdir.remove(newdoor)
                    elif doors[cur_x+1][cur_y] > 0:
                        loopdir.remove(newdoor)
                elif newdoor == 4:
                    if cur_y == self.max_y-1:
                        loopdir.remove(newdoor)
                    elif doors[cur_x][cur_y+1] > 0:
                        loopdir.remove(newdoor)
                elif newdoor == 8:
                    if cur_x == 0:
                        loopdir.remove(newdoor)
                    elif doors[cur_x-1][cur_y] > 0:
                        loopdir.remove(newdoor)
            # If there are valid exit walls, fill in both the door for this 
            # cell and the connected cell

            if len(loopdir) > 0 :
                history.append([cur_x, cur_y])
                count+=1
                doors[cur_x][cur_y] = doors[cur_x][cur_y] | loopdir[0]
                
                if loopdir[0] == self.bit_u:
                    doors[cur_x][cur_y-1] = doors[cur_x][cur_y-1] | self.bit_d
                    cur_y-=1
                elif loopdir[0] == self.bit_r:
                    doors[cur_x+1][cur_y] = doors[cur_x+1][cur_y] | self.bit_l
                    cur_x+=1
                elif loopdir[0] == self.bit_d:
                    doors[cur_x][cur_y+1] = doors[cur_x][cur_y+1] | self.bit_u
                    cur_y+=1
                elif loopdir[0] == self.bit_l:
                    doors[cur_x-1][cur_y] = doors[cur_x-1][cur_y] | self.bit_r
                    cur_x-=1
            else:
                last = history.pop()
                cur_x = last[0]
                cur_y = last[1]
                
        return doors
    
    def draw_cell(self,x,y,celltype):
        
        if celltype == 0:
            rect = Rect( (x*100)+50, (y*100)+50, 100, 100)
            pygame.draw.rect(self.screen, (0,0,0), rect)
        else:
            rect = Rect( (x*100)+50, (y*100)+50, 100, 100)
            # draw background
            pygame.draw.rect(self.screen, (0,0,0), rect)
            
            color = (150,150,150)
            
            if celltype & self.bit_used:
                color = (255,255,255)
                
            #is 0,0?
            if self.map_x+x-1 == 0 and self.map_y+y-1 == 0:
                color = (0,255,0)
            if self.map_x+x == self.max_x and self.map_y+y == self.max_y:
                color = (255,0,0)
                if x==1 and y==1:
                    self.success = True
                
            if x==1 and y==1:
                color = (255,255,0)
            
            #draw floor
            rect = Rect((x*100)+50+10, (y*100)+50+10, 100-20, 100-20)
            pygame.draw.rect(self.screen, color, rect)
            
            
            # doors
            if celltype & self.bit_u:
                rect = Rect((x*100)+50+10, (y*100)+50, 80, 10)
                pygame.draw.rect(self.screen, color, rect)
            if celltype & self.bit_r:
                rect = Rect((x*100)+50+100-10, (y*100)+50+10, 10, 80)
                pygame.draw.rect(self.screen, color, rect)
            if celltype & self.bit_d:
                rect = Rect((x*100)+50+10, (y*100)+50+100-10, 80, 10)
                pygame.draw.rect(self.screen, color, rect)
            if celltype & self.bit_l:
                rect = Rect((x*100)+50, (y*100)+50+10, 10, 80)
                pygame.draw.rect(self.screen, color, rect)
        pygame.display.flip()
        return True

    def draw_dynamic_cell(self,x,y,celltype,top_buffer,left_buffer,cell_x,cell_y,current):
        # draw background        
        quickdraw = False
        if cell_x < 3 or cell_y < 3:
            color = (255,255,255)
            quickdraw = True
        if current:
            color = (255,255,0)
            quickdraw = True
        if quickdraw:
            rect = Rect((self.map_x*cell_x)+left_buffer, (self.map_y*cell_y)+top_buffer, cell_x, cell_y)
            pygame.draw.rect(self.screen, color, rect)
            pygame.display.flip()
            return True
        
        # borders are min 10%
        border = math.ceil(cell_x*.1)        
        
        #draw background        
        color = (0,0,0)
        rect = Rect((self.map_x*cell_x)+left_buffer, (self.map_y*cell_y)+top_buffer, cell_x, cell_y)
        pygame.draw.rect(self.screen, color, rect)
        
        #draw floor
        color = (255,255,255)
        rect = Rect((self.map_x*cell_x)+left_buffer+border, (self.map_y*cell_y)+top_buffer+border, cell_x-(border*2), cell_y-(border*2))
        
        pygame.draw.rect(self.screen, color, rect)
        pygame.display.flip()
        
        # doors
        if celltype & self.bit_u:
            rect = Rect((self.map_x*cell_x)+left_buffer+border, (self.map_y*cell_y)+top_buffer, cell_x-(border*2), border)
            pygame.draw.rect(self.screen, color, rect)
        if celltype & self.bit_r:
            rect = Rect((self.map_x*cell_x)+left_buffer+cell_x-border, (self.map_y*cell_y)+top_buffer+border, border, cell_y-(border*2))
            pygame.draw.rect(self.screen, color, rect)
        if celltype & self.bit_d:
            rect = Rect((self.map_x*cell_x)+left_buffer+border, (self.map_y*cell_y)+top_buffer+cell_x-border, cell_x-(border*2), border)
            pygame.draw.rect(self.screen, color, rect)
        if celltype & self.bit_l:
            rect = Rect((self.map_x*cell_x)+left_buffer, (self.map_y*cell_y)+top_buffer+border, border, cell_y-(border*2))
            pygame.draw.rect(self.screen, color, rect)
        pygame.display.flip()
        
        return True
        
    def draw_close_map(self):
        for y in range(-1,2,1):
            for x in range(-1,2,1):
                if self.map_x+x<0 or self.map_x+x+1>self.max_x or self.map_y+y<0 or self.map_y+y+1 > self.max_y:
                    self.draw_cell(x+1,y+1,0)
                else:
                    self.draw_cell(x+1,y+1,self.maze[self.map_x+x][self.map_y+y])
                    if x==0 and y==0:
                        self.maze[self.map_x+x][self.map_y+y] = self.maze[self.map_x+x][self.map_y+y] | self.bit_used                 
        
        
    def init_screen(self):
        # create screen
        

        # main BG
        self.screen.fill((150,150,150))
        # local map
        self.screen.fill((0,0,0), (50,50,300,300))
        # local map border
        self.screen.fill((0,0,0), (45,45,310,310))
        
        # global map
        self.screen.fill((0,0,0), (400,50,300,300))
        
        font = pygame.font.Font('freesansbold.ttf', 24)
        
        text = font.render('Use wasd or arrow keys to navigate and Enter to reset.', True, (190,190,190))
        textRect = text.get_rect()
        textRect.center = (750 // 2, 20)
        self.screen.blit(text, textRect)
        
        text = font.render('User -= and [] to change maze size by 1 or '+str(self.step_size)+'.', True, (190,190,190))
        textRect = text.get_rect()
        textRect.center = (750 // 2, 380)
        self.screen.blit(text, textRect)
        
        
        
        pygame.display.flip()
    
    def input_scan(self):
        event = pygame.event.wait()
       
        # check for inputs
        if event.type == QUIT:
            self.keep_running = True
            return 'quit'
        elif event.type == KEYDOWN:
            if event.key == 27:
                self.keep_running = True
                return 'quit'
            
            adjust = False;
            
            
            #pressed up



            adj_x = adj_y = 0;
            
            if self.success == False:
                if event.key == 119 or event.key == 1073741906:
                    if( True == self.check_valid(self.bit_u) and self.maze[self.map_x][self.map_y] & self.bit_u ):
                        adj_y = -1
                        adjust = True
                #pressed right
                if event.key == 100 or event.key == 1073741903:
                    if( True == self.check_valid(self.bit_r) and self.maze[self.map_x][self.map_y] & self.bit_r):
                        adj_x = 1
                        adjust = True
                #pressed down
                if event.key == 115 or event.key == 1073741905:
                    if( True == self.check_valid(self.bit_d) and self.maze[self.map_x][self.map_y] & self.bit_d):
                        adj_y = 1
                        adjust = True
                #pressed left
                if event.key == 97 or event.key == 1073741904:
                    if( True == self.check_valid(self.bit_l) and self.maze[self.map_x][self.map_y] & self.bit_l):
                        adj_x = -1
                        adjust = True
                #increase size by 1
                if event.key == 61:
                    if self.max_x+1 <= self.top_limit or self.max_y+1 <= self.top_limit:
                        self.max_x+=1
                        self.max_y+=1
                        adjust = True
                        self.new_map = True
                #decrease size by 1
                if event.key == 45:
                    if self.max_x-1 >= 3 or self.max_y-1 >= 3:
                        self.max_x-=1
                        self.max_y-=1
                        adjust = True
                        self.new_map = True
                #increase size by 5
                if event.key == 93:
                    
                    if self.max_x+self.step_size <= self.top_limit or self.max_y+self.step_size <= self.top_limit:
                        self.max_x+=self.step_size
                        self.max_y+=self.step_size
                        adjust = True
                        self.new_map = True
                #decrease size by 5
                if event.key == 91:
                    
                    if self.max_x-self.step_size >= 3 or self.max_y-self.step_size >= 3:
                        self.max_x-=self.step_size
                        self.max_y-=self.step_size
                        adjust = True
                        self.new_map = True
                
            #restart
            if event.key == 13:
                self.maze = self.create_maze_array()
                self.map_x = 0
                self.map_y = 0
                adjust = True
                self.success = False
                self.init_screen()
            
            if adjust:
                
                self.update_big_map()
                self.map_x += adj_x
                self.map_y += adj_y                
                self.draw_close_map()
                self.update_big_map(True)
                
                if self.success:
                    s = pygame.Surface((1000,750))  # the size of your rect
                    s.set_alpha(200)                # alpha level
                    s.fill((255,255,255))           # this fills the entire surface
                    self.screen.blit(s, (0,0))
                
                    font = pygame.font.Font('freesansbold.ttf', 32)
                    # create a text surface object,
                    # on which text is drawn on it.
                    text = font.render('You win! It took you '+str(self.moves)+' moves!', True, (255,0,0))
                    textRect = text.get_rect()
                    textRect.center = (750 // 2, 400 // 3)
                    self.screen.blit(text, textRect)
                    
                    text = font.render('Press Enter to reset.', True, (255,0,0))
                    textRect = text.get_rect()
                    textRect.center = (750 // 2, (400 // 3)*2)
                    self.screen.blit(text, textRect)
                    
                    pygame.display.flip()
                    
                    self.success = False;
                    self.moves = 0;
                else:
                    self.moves += 1
                                       
                if self.new_map:
                    s = pygame.Surface((1000,750))  # the size of your rect
                    s.set_alpha(255)              # alpha level
                    s.fill((255,255,255))           # this fills the entire surface
                    self.screen.blit(s, (0,0))
                
                    font = pygame.font.Font('freesansbold.ttf', 32)
                    # create a text surface object,
                    # on which text is drawn on it.
                    text = font.render('Generating a new maze, '+str(self.max_x)+' by '+str(self.max_y)+' cells', True, (255,0,0))
                    textRect = text.get_rect()
                    textRect.center = (750 // 2, 400 // 3)
                    self.screen.blit(text, textRect)
                    
                    text = font.render('Press Enter to reset.', True, (255,0,0))
                    textRect = text.get_rect()
                    textRect.center = (750 // 2, (400 // 3)*2)
                    self.screen.blit(text, textRect)
                    
                    pygame.display.flip()
                    
                    self.moves = 0
                    self.new_map = False
            
    def update_big_map(self,current = False):
        cell_x = math.ceil(300/self.max_x)
        cell_y = math.ceil(300/self.max_y)
        
        self.draw_dynamic_cell(self.map_x,self.map_y,self.maze[self.map_x][self.map_y],self.top_buffer,self.left_buffer,cell_x,cell_y,current)

        
maze = ManiacalMaze() 
