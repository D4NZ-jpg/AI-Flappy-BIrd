import pygame
import neat
import time
import os
import random
import sys

#Loads Images
bird_img = [
    pygame.image.load(os.path.join("Assets","Bird1.png")),
    pygame.image.load(os.path.join("Assets","Bird2.png")),
    pygame.image.load(os.path.join("Assets","Bird3.png"))
    ]

bg_img = pygame.image.load(os.path.join("Assets","Background.png"))
Floor_img = pygame.image.load(os.path.join("Assets","Floor.png"))
pipe_img = pygame.image.load(os.path.join("Assets","Pipe.png"))

#Set Window size depending on the size of the background Image
win_w = bg_img.get_width()
win_h = bg_img.get_height()

#Define the class for the Bird
class Bird:
    imgs = bird_img
    max_rotation = 25
    rot_vel = 2
    animation_time = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.tick_count = 0
        self.vel = 0
        self.height = self.y
        self.img_num = 0
        self.img = self.imgs[0]

    #Makes the Bird Jump
    def Jump(self):
        self.vel = -3.5
        self.tick_count = 0
        self.height = self.y

    #Move the bird in the y coords
    def Move(self):
        self.tick_count += 1
        d = self.vel*self.tick_count + .5*self.tick_count**2

        if d >= 8: 
            d = 8

        if d < 0:
            d -= 2

        self.y = self.y + d

        if d < 0 or self.y < self.height + 25:
            if self.tilt < self.max_rotation:
                self.tilt = self.max_rotation
            else:
                if self.tilt > -90:
                    self.tilt -= self.rot_vel

    #Draws the bird with its rotation and the correct sprite
    def Draw(self, win):
        self.img_num += 1

        if self.img_num < self.animation_time:
            self.img = self.imgs[0]
        elif self.img_num < self.animation_time * 2:
            self.img = self.imgs[1]
        elif self.img_num < self.animation_time * 3:
            self.img = self.imgs[2]
        elif self.img_num < self.animation_time * 4:
            self.img = self.imgs[1]
        elif self.img_num == self.animation_time * 4 + 1:
            self.img = self.imgs[0]
            self.img_num = 0

        if self.tilt <= -80:
            self.img = self.bird_img[1]
            self.img_num = self.animation_time * 2

        rotated_img = pygame.transform.rotate(self.img, self.tilt)
        new_rect = rotated_img.get_rect(center=self.img.get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_img, new_rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(self.img)

#Defines the class for the Pipes
class Pipe:
    gap = 90
    vel = 3


    def __init__(self, x):
        self.x = x
        self.height = 0

        self.top = 0
        self.bottom = 0
        self.Pipe_Top = pygame.transform.flip(pipe_img, False, True)
        self.Pipe_Bottom = pipe_img

        self.passed = False
        self.set_height()

    #Selects a random height for the Pipes
    def set_height(self):
        self.height = random.randrange(192,320)
        self.top = self.height - self.Pipe_Top.get_height()
        self.bottom = self.height + self.gap

    #Moves the pipes
    def Move(self):
        self.x -= self.vel

    #Draws the Pipes in the correct positions
    def Draw(self, win):
        win.blit(self.Pipe_Top, (self.x, self.top))
        win.blit(self.Pipe_Bottom, (self.x, self.bottom))

    #Detects pixel perfect Collitions
    def Collition(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.Pipe_Top)
        bottom_mask = pygame.mask.from_surface(self.Pipe_Bottom)

        top_offset = (int(self.x - bird.x), int(self.top - round(bird.y)))         
        bottom_offset = (int(self.x - bird.x), int(self.bottom - round(bird.y)))

        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        t_point = bird_mask.overlap(top_mask, top_offset)

        if b_point or t_point:
            return True

        return False

#Define the class for the Floor
class Floor:
    vel = 3
    width = Floor_img.get_width()
    img = Floor_img

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.width

    #Makes the Images for the floor Loop
    def Move(self):
        self.x1 -= self.vel
        self.x2 -= self.vel

        if self.x1 + self.width < 0:
            self.x1 = self.x2 + self.width

        if self.x2 + self.width < 0:
            self.x2 = self.x1 + self.width

    #Draws the Floors in their positions
    def Draw(self, win):
        win.blit(self.img, (self.x1, self.y))
        win.blit(self.img, (self.x2, self.y))

#Draws the window of the game
def draw_win(win, birds, pipes, floor, score):
    win.blit(bg_img, (0,0))

    for bird in birds:
        bird.Draw(win)

    for pipe in pipes:
        pipe.Draw(win)

    floor.Draw(win)
    pygame.display.update()

#The main Loop
def main(genomes, config):
    nets = []
    ge = []
    birds = []

    for _,g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        birds.append(Bird(win_w/4, win_h/2))
        g.fitness = 0        
        ge.append(g)


    floor = Floor(480)
    pipes = [Pipe(350)]
    win = pygame.display.set_mode((win_w, win_h))
    clock = pygame.time.Clock()
    score = 0

    run = True
    while(run):
        clock.tick(30)
        #Checks to Close Window
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:    
                    bird.Jump()    


        pipe_ind = 0
        if len(birds) > 0:
            if len(pipes) > 0 and birds[0].x > pipes[0].Pipe_Top.get_height():
                pipe_ind = 1
        else:
            run = False


        for x , bird in enumerate(birds):
            bird.Move()
            ge[x].fitness +=0.1

            output = nets[x].activate((bird.y, abs(bird.y-pipes[pipe_ind].height), abs(bird.y-pipes[pipe_ind].bottom)))

            if output[0] > 0.5:
                bird.Jump()


        bird.Move()
        New_Pipe = False
        removed = []


        for pipe in pipes:
            for x, bird in enumerate(birds):
                #Detects Collitions of Pipes with Bird
                if pipe.Collition(bird):
                    ge[x].fitness -=1
                    birds.pop(x)
                    nets.pop(x)
                    ge.pop(x)

                #Checks if the Pipe have been Passed
                if not pipe.passed and pipe.x < bird.x:
                    pipe.passed = True
                    New_Pipe = True

            #Detects if the pipe is outside the screen
            if pipe.x + pipe.Pipe_Top.get_width() < 0:
                removed.append(pipe)

            pipe.Move()


        if New_Pipe:
            score +=1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(288))


        for remove in removed:
            pipes.remove(remove)


        floor.Move()
        draw_win(win,birds, pipes, floor, score)


        #Checks if hit Ground
        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= floor.y or bird.y < 0:
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)

    pygame.quit()

def run(config_path):

    #Loads configuration
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction, 
        neat.DefaultSpeciesSet, neat.DefaultStagnation, config_path)

    #Defines the population
    p = neat.Population(config)

    #Prints information about the generation and the AI
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)

    winner = p.run(main,50)

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-feedforward.txt")
    run(config_path)