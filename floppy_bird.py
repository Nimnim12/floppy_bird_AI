import random
import pygame
import os
import neat

WIN_HEIGHT = 800
WIN_WIDTH = 550
pygame.font.init()
GENERATION = 0
BRID_IMGS = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird3.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird2.png"))),
             pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bird1.png")))]
BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "bg.png")))
PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "pipe.png")))
TOP_PIPE_IMG = pygame.transform.flip(PIPE_IMG, False, True)
BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))

SCORE_FONT = pygame.font.SysFont("comicsans", 40)


class Bird:
    MAX_TILT = 25
    TILT_AMMOUNT = 10
    IMAGE_TIME = 10

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.tilt = 0
        self.vel = 0
        self.time = 0
        self.animation_time = 0

    def jump(self):
        self.vel = - 25
        self.time = 0

    def move(self):
        self.time += 1
        ammount_to_move = self.vel + self.time ** 2

        if ammount_to_move > 12:
            ammount_to_move = 12
        self.y += ammount_to_move
        if ammount_to_move < 0:
            self.tilt = self.MAX_TILT
        else:
            if self.tilt > -90:
                self.tilt -= self.TILT_AMMOUNT

    def draw(self, win):
        self.animation_time += 1
        if self.animation_time == 50:
            self.animation_time = 0
        img = self.animation_time // self.IMAGE_TIME
        if self.tilt < - 80:
            img = 1
            self.animation_time = self.IMAGE_TIME
        rotated_image = pygame.transform.rotate(BRID_IMGS[img], self.tilt)
        rect = rotated_image.get_rect(center=BRID_IMGS[img].get_rect(topleft=(self.x, self.y)).center)
        win.blit(rotated_image, rect.topleft)

    def get_mask(self):
        return pygame.mask.from_surface(BRID_IMGS[self.animation_time // self.IMAGE_TIME])


class Pipe:
    VEL = 5
    GAP = 200

    def __init__(self, x):
        self.x = x
        height = random.randrange(50, 450)
        self.top = height - TOP_PIPE_IMG.get_height()
        self.bottom = height + self.GAP
        self.passed = False

    def move(self):
        self.x -= self.VEL

    def draw(self, win):
        win.blit(TOP_PIPE_IMG, (self.x, self.top))
        win.blit(PIPE_IMG, (self.x, self.bottom))

    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(TOP_PIPE_IMG)
        bottom_mask = pygame.mask.from_surface(PIPE_IMG)

        bird_to_top_pipe = (self.x - bird.x, self.top - bird.y)
        bird_to_bottom_pipe = (self.x - bird.x, self.bottom - bird.y)

        top_collision_point = bird_mask.overlap(top_mask, bird_to_top_pipe)
        bottom_collision_point = bird_mask.overlap(bottom_mask, bird_to_bottom_pipe)

        if top_collision_point or bottom_collision_point:
            return True
        return False


class Base:
    VEL = 5

    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = BASE_IMG.get_width()

    def move(self):
        self.x1 -= self.VEL
        self.x2 -= self.VEL

        if self.x1 + BASE_IMG.get_width() < 0:
            self.x1 = self.x2 + BASE_IMG.get_width()
        if self.x2 + BASE_IMG.get_width() < 0:
            self.x2 = self.x1 + BASE_IMG.get_width()

    def draw(self, win):
        win.blit(BASE_IMG, (self.x1, self.y))
        win.blit(BASE_IMG, (self.x2, self.y))


def draw_window(birds, base, pipes, score, gen, win):
    win.blit(BG_IMG, (0, 0))
    for bird in birds:
        bird.draw(win)
    for pipe in pipes:
        pipe.draw(win)
    base.draw(win)

    text = SCORE_FONT.render("Score: " + str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - text.get_width(), 10))
    text_birds = SCORE_FONT.render("Birds: " + str(len(birds)), 1, (255, 255, 255))
    win.blit(text_birds, (10, 10))
    text = SCORE_FONT.render("Gen: " + str(gen), 1, (255, 255, 255))
    win.blit(text, (20 + text_birds.get_width(), 10))


def move_world(birds, base, pipes):
    for bird in birds:
        bird.move()
    base.move()
    for pipe in pipes:
        pipe.move()


def main(genomes, config):
    global GENERATION
    GENERATION += 1
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    birds = []
    nets = []
    ge = []
    for genome_id, genome in genomes:
        genome.fitness = 0
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        birds.append(Bird(100,400))
        ge.append(genome)


    base = Base(WIN_HEIGHT - 100)
    pipes = [Pipe(600)]
    clock = pygame.time.Clock()
    score = 0
    need_new = False


    while True:
        pipe_index = 0
        if len(birds) > 0:
            if len(pipes) > 1 and birds[0].x > pipes[0].x + PIPE_IMG.get_width():
                pipe_index = 1
        else:
            break

        for i, bird in enumerate(birds):
            output = nets[i].activate((bird.y,abs(bird.y - pipes[pipe_index].top), abs(bird.y - pipes[pipe_index].bottom )))
            if output[0] > 0.5:
                bird.jump()



        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        move_world(birds, base, pipes)
        draw_window(birds, base, pipes, score, GENERATION, win)
        removed_pipes = []
        # after bird image rotation we need to add 20 to properly get ground collision
        for pipe in pipes:
            if pipe.x + PIPE_IMG.get_width() < 0:
                removed_pipes.append(pipe)
            for i, bird in enumerate(birds):
                if pipe.collide(bird):
                    ge[i].fitness -= 1
                    del nets[i]
                    del birds[i]
                    del ge[i]
                else:
                    if not pipe.passed and pipe.x < bird.x:
                        pipe.passed = True
                        need_new = True
                    if bird.y + BRID_IMGS[0].get_height() + 20 > base.y or bird.y < 0:  # bird hit ground
                        ge[i].fitness -= 1
                        del nets[i]
                        del birds[i]
                        del ge[i]
        if need_new:
            score += 1
            for g in ge:
                g.fitness += 5
            pipes.append(Pipe(600))
            need_new = False
        for removed_pipe in removed_pipes:
            pipes.remove(removed_pipe)
        clock.tick(30)
        pygame.display.update()


def run(config_file_path):
    config = neat.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_file_path)
    population = neat.Population(config)
    winner = population.run(main, 30)


if __name__ == '__main__':
    pygame.init()
    config_file_path = os.path.join(os.path.dirname(__file__), "config-feedforward.txt")
    run(config_file_path)
