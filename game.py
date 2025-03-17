# Made by Richard & Temesgem

import pygame
import random
import json
import sys

# Initialize pygame
pygame.init()

# Screen settings
WIDTH, HEIGHT = 900, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Catch Frenzy")

# Load images
background = pygame.image.load("game_bkg.jpg")
background = pygame.transform.scale(background, (WIDTH, HEIGHT))

opening_background = pygame.image.load("opening_page_bkg.jpg")
opening_background = pygame.transform.scale(opening_background, (WIDTH, HEIGHT))

basket_image = pygame.image.load("ccc.jpg")
basket_image = pygame.transform.scale(basket_image, (100, 100))

basket = pygame.image.load("ccc.jpg")
basket = pygame.transform.scale(basket, (100, 100))

# Load Sound Effects
catch_sound = pygame.mixer.Sound("catch.wav")
# miss_sound = pygame.mixer.Sound("miss.wav")
game_over_sound = pygame.mixer.Sound("gameover.wav")

# Load Background Music
pygame.mixer.music.load("background_music.wav")
pygame.mixer.music.set_volume(0.5)
pygame.mixer.music.play(-1)  # Loop forever

# Colors
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
GOLD = (255, 215, 0)  # Color for golden apple (shield power-up)
BLACK = (0, 0, 0)
BROWN = (139, 69, 19)  # Brown color for menu buttons
DARK_BACKGROUND = (30, 30, 30)  # Dark background for name input and help screens

# Game settings
basket_width, basket_height = 100, 100
basket_x = WIDTH // 2 - basket_width // 2
basket_y = HEIGHT - 120
basket_speed = 10

# Object settings
object_radius = 15  # Smaller size for both red and green circles
falling_objects = []
fall_speed = 7  # Increased speed for more difficulty
spawn_rate = 10  # Increased spawn rate for more difficulty

# Score
score = 0
player_name = ""
high_scores = []
shield_active = False
shield_timer = 0
font = pygame.font.Font(None, 40)  # Smaller text for buttons
bold_font = pygame.font.Font(None, 72)  # Bold and large font for title

MENU, DIFFICULTY_SELECT, PLAYING, GAME_OVER, HIGHEST_SCORE, HELP, NAME_INPUT = "menu", "difficulty_select", "playing", "game_over", "highest_score", "help", "name_input"
game_state = MENU

difficulty_settings = {
    "easy": {"fall_speed": 7, "spawn_rate": 6, "shield_enabled": False},  # No shield in easy mode
    "medium": {"fall_speed": 10, "spawn_rate": 5, "shield_enabled": True}, # Shield available
    "hard": {"fall_speed": 12, "spawn_rate": 2, "shield_enabled": True}  # Shield available
}
difficulty = "medium"

# Load highest scores
def load_highest_scores():
    global high_scores
    try:
        with open("highest_score.json", "r") as f:
            data = json.load(f)
            if isinstance(data, list):  # Ensure data is a list
                high_scores = data
            else:
                high_scores = []  # Reset if data is not a list
    except FileNotFoundError:
        high_scores = []

# Save highest scores
def save_highest_scores():
    global high_scores
    if not isinstance(high_scores, list):
        high_scores = []  # Ensure high_scores is always a list
    
    high_scores.append({"name": player_name, "score": score, "level": difficulty})
    high_scores = sorted(high_scores, key=lambda x: x["score"], reverse=True)[:3]  # Keep only top 3 scores

    with open("highest_score.json", "w") as f:
        json.dump(high_scores, f)


# Function to display text
def draw_text(text, x, y, color=WHITE, font_type=font):
    text_surface = font_type.render(text, True, color)
    screen.blit(text_surface, (x, y))

# Button function
def draw_button(text, x, y, w, h, action=None):
    mouse = pygame.mouse.get_pos()
    click = pygame.mouse.get_pressed()
    pygame.draw.rect(screen, BROWN, (x, y, w, h), border_radius=10)
    draw_text(text, x + w//4, y + 10, WHITE)
    if x < mouse[0] < x + w and y < mouse[1] < y + h:
        if click[0] and action:
            pygame.time.delay(150)
            action()

# Select difficulty
def select_difficulty(diff):
    global game_state, difficulty, fall_speed, spawn_rate
    difficulty = diff
    fall_speed = difficulty_settings[diff]["fall_speed"]
    spawn_rate = difficulty_settings[diff]["spawn_rate"]
    game_state = NAME_INPUT

# Show difficulty selection
def show_difficulty_selection():
    global game_state
    game_state = DIFFICULTY_SELECT

# Start new game
def start_new_game():
    global game_state, score, falling_objects, basket_x, player_name
    game_state = NAME_INPUT
    score = 0
    falling_objects = []
    basket_x = WIDTH // 2 - basket_width // 2
    player_name = ""

# Play the game after name input
def play_game():
    global game_state, falling_objects, score, basket_x
    game_state = PLAYING
    score = 0
    falling_objects = []
    basket_x = WIDTH // 2 - basket_width // 2

# Replay game function
def replay_game():
    global game_state, score, falling_objects, basket_x
    game_state = PLAYING
    score = 0
    falling_objects = []
    basket_x = WIDTH // 2 - basket_width // 2

# Show highest score
def show_highest_score():
    global game_state
    game_state = HIGHEST_SCORE

# Show help menu
def show_help():
    global game_state
    game_state = HELP

# Return to menu
def return_to_menu():
    global game_state
    game_state = MENU

# Game over function
def game_over():
    global game_state
    save_highest_scores()
    game_state = GAME_OVER

# Load highest scores initially
load_highest_scores()

# Animated Sprite Class for Falling Objects
# class FallingObject(pygame.sprite.Sprite):
#     def __init__(self, x, y, color, obj_type):
#         super().__init__()
#         self.image = pygame.Surface((object_radius * 2, object_radius * 2))
#         self.image.fill(color)
#         self.rect = self.image.get_rect(center=(x, y))
#         self.color = color
#         self.obj_type = obj_type
#         self.animation_frame = 0

#     def update(self):
#         self.rect.y += fall_speed
#         if self.rect.y > HEIGHT:
#             miss_sound.play()
#             self.kill()

# Basket Class for Smooth Animation
class Basket(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = basket_image
        self.rect = self.image.get_rect(topleft=(x, y))
        self.speed = basket_speed

    def update(self, keys):
        if keys[pygame.K_LEFT] and self.rect.x > 0:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] and self.rect.x < WIDTH - basket_width:
            self.rect.x += self.speed

# Initialize Basket
basket = Basket(basket_x, basket_y)

# Main loop
running = True
clock = pygame.time.Clock()
while running:
    screen.fill(WHITE)
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        if game_state == NAME_INPUT and event.type == pygame.KEYDOWN:
            if event.key == pygame.K_RETURN and player_name.strip():
                play_game()
            elif event.key == pygame.K_BACKSPACE:
                player_name = player_name[:-1]
            elif event.unicode.isprintable():
                player_name += event.unicode

    if game_state == MENU:
        screen.blit(opening_background, (0, 0))
        draw_text("Catch Frenzy", WIDTH // 2 - 150, HEIGHT // 7, WHITE, bold_font)
        draw_button("Start New Game", WIDTH // 2 - 100, HEIGHT // 2 - 30, 300, 60, show_difficulty_selection)
        draw_button("Highest Scores", WIDTH // 2 - 100, HEIGHT // 2 + 50, 300, 60, show_highest_score)
        draw_button("Help", WIDTH // 2 - 100, HEIGHT // 2 + 130, 300, 60, show_help)
    
    elif game_state == DIFFICULTY_SELECT:
        screen.blit(opening_background, (0, 0))
        draw_text("Select Difficulty", WIDTH // 2 - 150, HEIGHT // 7, WHITE, bold_font)
        draw_button("Easy", WIDTH // 2 - 100, HEIGHT // 2 - 90, 300, 60, lambda: select_difficulty("easy"))
        draw_button("Medium", WIDTH // 2 - 100, HEIGHT // 2, 300, 60, lambda: select_difficulty("medium"))
        draw_button("Hard", WIDTH // 2 - 100, HEIGHT // 2 + 90, 300, 60, lambda: select_difficulty("hard"))
        draw_button("Back to Menu", WIDTH // 2 - 100, HEIGHT // 2 + 180, 300, 60, return_to_menu)
    
    elif game_state == NAME_INPUT:
        screen.fill(DARK_BACKGROUND)
        draw_text("Enter Your Name:", WIDTH // 2 - 150, HEIGHT // 3, WHITE, bold_font)
        draw_text(player_name + "_", WIDTH // 2 - 100, HEIGHT // 2, WHITE, font)
    
    elif game_state == PLAYING:
        screen.blit(background, (0, 0))
        # screen.blit(basket, (basket_x, basket_y))
        screen.blit(basket.image, basket.rect.topleft)
        draw_text(f"Score: {score}", 10, 10, WHITE)

        # keys = pygame.key.get_pressed()
        keys = pygame.key.get_pressed()
        basket.update(keys)

        if keys[pygame.K_LEFT] and basket_x > 0:
            basket_x -= basket_speed
        if keys[pygame.K_RIGHT] and basket_x < WIDTH - basket_width:
            basket_x += basket_speed
        
        # Handle Shield Timer
        if shield_active:
            shield_timer -= 1
            draw_text(f"Immunity: {shield_timer // 30}s", 10, 50, GOLD)
            if shield_timer <= 0:
                shield_active = False

        if random.randint(1, spawn_rate) == 1:
            x_pos = random.randint(0, WIDTH - object_radius * 2)
            obj_type = random.choices(["green", "red", "gold"], [0.7, 0.29, 0.01])[0]
            color = GREEN if obj_type == "green" else RED if obj_type == "red" else GOLD
            falling_objects.append([x_pos, 0, color, obj_type])

        for obj in falling_objects[:]:
            obj[1] += fall_speed
            pygame.draw.circle(screen, obj[2], (obj[0] + object_radius, obj[1] + object_radius), object_radius)
            if basket.rect.x < obj[0] < basket.rect.x + basket_width and basket.rect.y < obj[1] < basket.rect.y + basket_height:
                if obj[3] == "green":
                    score += 1
                elif obj[3] == "gold" and difficulty_settings[difficulty]["shield_enabled"]:
                    shield_active = True
                    shield_timer = 300  # Temporary shield duration
                elif obj[3] == "red":
                    if not shield_active:
                        pygame.mixer.music.pause()
                        game_over_sound.play()
                        game_over()
                        pygame.mixer.music.unpause()
                falling_objects.remove(obj)
            elif obj[1] > HEIGHT:
                falling_objects.remove(obj)
    
    elif game_state == GAME_OVER:
        screen.blit(opening_background, (0, 0))
        draw_text("Game Over", WIDTH // 2 - 100, HEIGHT // 8, WHITE, bold_font)
        draw_text(f"Final Score: {score}", WIDTH // 2 - 100, HEIGHT // 5, WHITE)
        draw_button("Replay", WIDTH // 2 - 100, HEIGHT // 2, 300, 60, replay_game)
        draw_button("Back to Menu", WIDTH // 2 - 100, HEIGHT // 2 + 80, 300, 60, return_to_menu)
    
    elif game_state == HELP:
        screen.fill(DARK_BACKGROUND)
        draw_text("Welcome to Catch Frenzy!", WIDTH // 2 - 400, HEIGHT // 5, WHITE, bold_font)
        draw_text("How to Play:", WIDTH // 2 - 400, HEIGHT // 3, WHITE)
        draw_text("- Move the basket left/right to catch green objects.", WIDTH // 2 - 400, HEIGHT // 3 + 40, WHITE)
        draw_text("- Avoid red objects or the game is over!", WIDTH // 2 - 400, HEIGHT // 3 + 80, WHITE)
        draw_text("- If you catch golden object, you'll get a 10 seconds immunity!", WIDTH // 2 - 400, HEIGHT // 3 + 120, WHITE)
        draw_button("Back to Menu", WIDTH // 2 - 200, HEIGHT // 2 + 130, 300, 60, return_to_menu)

    elif game_state == HIGHEST_SCORE:
        screen.fill(DARK_BACKGROUND)
        draw_text("Top 3 Highest Scores", WIDTH // 2 - 200, HEIGHT // 7, WHITE, bold_font)
        for i, entry in enumerate(high_scores[:3]):
            draw_text(f"Name: {entry['name']} Level: {entry['level']}", WIDTH // 2 - 150, HEIGHT // 3 + i * 50, WHITE)
            draw_text(f"Score: {entry['score']}", WIDTH // 2 - 150, HEIGHT // 3 + i * 50 + 30, WHITE)
        draw_button("Back to Menu", WIDTH // 2 - 150, HEIGHT // 2 + 130, 300, 60, return_to_menu)
    
    pygame.display.flip()
    clock.tick(30)

pygame.quit()