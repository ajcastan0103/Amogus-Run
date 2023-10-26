import pygame, os, random, sys
from os import path

pygame.init()

SCREEN_HEIGHT = 600
SCREEN_WIDTH = 1100

HS_FILE = "highscore.txt"

SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

RUNNING = [
    pygame.image.load(os.path.join("Assets/player", "frame0.png")),
    pygame.image.load(os.path.join("Assets/player", "frame1.png")),
    pygame.image.load(os.path.join("Assets/player", "frame2.png")),
    pygame.image.load(os.path.join("Assets/player", "frame3.png")),
]

JUMPING = pygame.image.load(os.path.join("Assets/player", "frame0.png"))

ENEMY = [
    pygame.image.load(os.path.join("Assets/enemy", "enemyp.png")),
    pygame.image.load(os.path.join("Assets/enemy", "enemyb.png")),
    pygame.image.load(os.path.join("Assets/enemy", "enemyy.png")),
]

BG = pygame.image.load(os.path.join("Assets/other", "bgimg.jpg"))

SOUNDS = [
    pygame.mixer.Sound("Assets/other/introSound.mp3"),
    pygame.mixer.Sound("Assets/other/dead.mp3"),
    pygame.mixer.Sound("Assets/other/jump.mp3"),
]

pygame.mixer.music.load("Assets/other/song.mp3")

FONT = pygame.font.Font("Assets/Font/ARCADECLASSIC.ttf", 20)
FONT_MENU = pygame.font.Font("Assets/Font/ARCADECLASSIC.ttf", 30)


# Class Character to display on screen
class Character:
    X_POS = 25
    Y_POS = 310
    JUMP_VEL = 8.5

    def __init__(self):
        self.run_img = RUNNING
        self.jump_img = JUMPING

        self.char_run = True
        self.char_jump = False

        self.step_index = 0
        self.image = self.run_img[0]
        self.jump_vel = self.JUMP_VEL
        self.char_rect = self.image.get_rect()
        self.char_rect.x = self.X_POS
        self.char_rect.y = self.Y_POS

    # Animate character
    def update(self, userInput):
        if self.char_run:
            self.run()
        if self.char_jump:
            self.jump()

        if self.step_index >= 10:
            self.step_index = 0

        if (userInput[pygame.K_UP] or userInput[pygame.K_SPACE]) and not self.char_jump:
            pygame.mixer.Sound.play(SOUNDS[2])
            self.char_run = False
            self.char_jump = True
        elif not self.char_jump:
            self.char_run = True
            self.char_jump = False

    def run(self):
        self.image = self.run_img[self.step_index // 3]
        self.char_rect = self.image.get_rect()
        self.char_rect.x = self.X_POS
        self.char_rect.y = self.Y_POS
        self.step_index += 1

    def jump(self):
        self.image = self.jump_img
        if self.char_jump:
            self.char_rect.y -= self.jump_vel * 4
            self.jump_vel -= 0.8
        if self.jump_vel < -self.JUMP_VEL:
            self.char_jump = False
            self.jump_vel = self.JUMP_VEL

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.char_rect.x, self.char_rect.y))


# Class obstacle for enemies
class Obstacle:
    def __init__(self, image, type):
        self.image = image
        self.type = type
        self.rect = self.image[self.type].get_rect()
        self.rect.x = SCREEN_WIDTH

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image[self.type], self.rect)


class Imposter(Obstacle):
    def __init__(self, image):
        self.type = random.randint(0, 2)
        super().__init__(image, self.type)
        self.rect.y = 305


def main():
    # Read highscore from txt file
    global game_speed, x_pos_bg, y_pos_bg, points, highscore, obstacles

    game_speed = 14
    x_pos_bg = 0
    y_pos_bg = 390
    points = 0
    with open(path.join(path.dirname(__file__), HS_FILE), "r") as f:
        try:
            highscore = int(f.read())
        except:
            highscore = 0
    obstacles = []

    death_count = 0
    run = True
    clock = pygame.time.Clock()
    player = Character()

    pygame.mixer.Sound.stop(SOUNDS[0])
    pygame.mixer.music.play(-1)

    # loop background asset
    def background():
        global x_pos_bg, y_pos_bg
        image_width = BG.get_width()
        SCREEN.blit(BG, (x_pos_bg, y_pos_bg))
        SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
        if x_pos_bg <= -image_width:
            SCREEN.blit(BG, (image_width + x_pos_bg, y_pos_bg))
            x_pos_bg = 0
        x_pos_bg -= game_speed

    # Display score
    def score():
        global points, game_speed, highscore
        points += 1
        if points % 100 == 0:
            game_speed += 1

        score_txt = FONT.render("Score   " + str(points), True, (0, 0, 0))
        score_txtRect = score_txt.get_rect()
        score_txtRect.center = (1000, 40)
        SCREEN.blit(score_txt, score_txtRect)

        hs_txt = FONT.render("High score   " + str(highscore), True, (0, 0, 0))
        hs_txtRect = hs_txt.get_rect()
        hs_txtRect.center = (1000, 60)
        SCREEN.blit(hs_txt, hs_txtRect)

    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()

        SCREEN.fill((80, 80, 80))
        userInput = pygame.key.get_pressed()

        player.draw(SCREEN)
        player.update(userInput)
        if len(obstacles) == 0:
            obstacles.append(Imposter(ENEMY))

        for elem in obstacles:
            elem.draw(SCREEN)
            elem.update()

            if player.char_rect.colliderect(elem.rect):
                if points > highscore:
                    highscore = points
                    with open(path.join(path.dirname(__file__), HS_FILE), "w") as f:
                        f.write(str(points))
                pygame.mixer.music.stop()
                pygame.mixer.Sound.play(SOUNDS[1])
                pygame.time.delay(500)
                death_count += 1
                menu(death_count)

        # Update as gameplay resumes
        background()
        score()
        clock.tick(30)
        pygame.display.update()


def menu(death_count):
    global points
    global highscore
    with open(path.join(path.dirname(__file__), HS_FILE), "r") as f:
        try:
            highscore = int(f.read())
        except:
            highscore = 0
    run = True
    step_index = 0
    delay_counter = 0

    while run:
        SCREEN.fill((255, 255, 255))

        # If game just opened, show title screen
        if death_count == 0:
            title = FONT_MENU.render("AMOGUS  RUN", True, (0, 0, 0))
            status = FONT_MENU.render("Press  the  spacebar  to  start", True, (0, 0, 0))
            hstext = FONT_MENU.render("High score  " + str(highscore), True, (0, 0, 0))
            hsRect = hstext.get_rect()
            hsRect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 50)
            pygame.mixer.Sound.play(SOUNDS[0])

        # Otherwise, show game over screen
        elif death_count > 0:
            title = FONT_MENU.render("Game  over", True, (0, 0, 0))
            status = FONT_MENU.render("Press  the spacebar  to  Restart", True, (0, 0, 0))
            score = FONT_MENU.render("Score  " + str(points), True, (0, 0, 0))
            scoreRect = score.get_rect()
            scoreRect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 50)
            hstext = FONT_MENU.render("High score  " + str(highscore), True, (0, 0, 0))
            hsRect = hstext.get_rect()
            hsRect.center = (SCREEN_WIDTH // 2, (SCREEN_HEIGHT // 2) + 100)
            SCREEN.blit(score, scoreRect)

        # Display running animation for title/end screen
        delay_counter += 1
        if delay_counter >= 60:
            step_index += 1
            delay_counter = 0
            if step_index >= len(RUNNING):
                step_index = 0
        SCREEN.blit(
            RUNNING[step_index],
            (
                SCREEN_WIDTH // 2 - RUNNING[step_index].get_width() // 2,
                SCREEN_HEIGHT // 2 - 140,
            ),
        )

        # Display menu text
        titleRect = title.get_rect()
        titleRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 250)
        SCREEN.blit(title, titleRect)
        statusRect = status.get_rect()
        statusRect.center = (SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2)
        SCREEN.blit(status, statusRect)
        SCREEN.blit(hstext, hsRect)
        pygame.display.update()

        # Check user input to start/restart game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    main()

menu(death_count=0)
