import tkinter as tk
from tkinter import messagebox
import random

# Game Constants
WIDTH = 600
HEIGHT = 400
SNAKE_SIZE = 20
SNAKE1_COLOR = 'green'
SNAKE2_COLOR = 'blue'
BACKGROUND_COLOR = 'black'
FOOD_COLOR = 'red'
WALL_COLOR = 'gray'
BORDER_COLOR = 'dark red'  # Color for the border
BORDER_WIDTH = 20  # Width of the border in pixels

# Initialize tkinter window
root = tk.Tk()
root.title("Two-Player Snake Game")
root.geometry(f"{WIDTH}x{HEIGHT}")
canvas = tk.Canvas(root, width=WIDTH, height=HEIGHT, bg=BACKGROUND_COLOR)
canvas.pack()

# Game Variables
snake1 = [(100, 100)]  # Player 1's snake
snake2 = [(500, 100)]  # Player 2's snake
direction1 = 'Right'   # Player 1's initial direction
direction2 = 'Left'    # Player 2's initial direction
food = None
score1 = 0
score2 = 0
lives1 = 3
lives2 = 3
game_over = False
speed = 100  # Game speed in milliseconds
is_multiplayer = False
highest_score = 0  # Track highest score
game_paused = False
game_running = False  # Flag to indicate if game is in progress

# Define the playable area (inside the border)
playable_x_min = BORDER_WIDTH
playable_x_max = WIDTH - BORDER_WIDTH
playable_y_min = BORDER_WIDTH
playable_y_max = HEIGHT - BORDER_WIDTH

# Function to check if a position is inside the border (and thus not playable)
def is_on_border(pos):
    x, y = pos
    return (x < playable_x_min or
            x >= playable_x_max or
            y < playable_y_min or
            y >= playable_y_max)

# Function to draw the border
def draw_border():
    # Top border
    canvas.create_rectangle(0, 0, WIDTH, BORDER_WIDTH, fill=BORDER_COLOR, outline="", tags="border")
    # Bottom border
    canvas.create_rectangle(0, HEIGHT - BORDER_WIDTH, WIDTH, HEIGHT, fill=BORDER_COLOR, outline="", tags="border")
    # Left border
    canvas.create_rectangle(0, 0, BORDER_WIDTH, HEIGHT, fill=BORDER_COLOR, outline="", tags="border")
    # Right border
    canvas.create_rectangle(WIDTH - BORDER_WIDTH, 0, WIDTH, HEIGHT, fill=BORDER_COLOR, outline="", tags="border")

# Function to spawn food
def spawn_food():
    global food
    while True:
        # Generate coordinates within the playable area
        x = random.randint(playable_x_min // SNAKE_SIZE, (playable_x_max - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
        y = random.randint(playable_y_min // SNAKE_SIZE, (playable_y_max - SNAKE_SIZE) // SNAKE_SIZE) * SNAKE_SIZE
        if (x, y) not in snake1 and (x, y) not in snake2:  # Ensure food doesn't spawn on snakes
            food = (x, y)
            canvas.create_rectangle(x, y, x + SNAKE_SIZE, y + SNAKE_SIZE, fill=FOOD_COLOR, tags="food")
            break

# Function to draw snakes
def draw_snakes():
    canvas.delete("snake1", "snake2")
    # Draw player 1 snake with head in a different shade
    for i, segment in enumerate(snake1):
        color = 'dark green' if i == 0 else SNAKE1_COLOR
        canvas.create_rectangle(segment[0], segment[1], segment[0] + SNAKE_SIZE, segment[1] + SNAKE_SIZE,
                               fill=color, outline='light green', tags="snake1")
   
    if is_multiplayer:
        # Draw player 2 snake with head in a different shade
        for i, segment in enumerate(snake2):
            color = 'dark blue' if i == 0 else SNAKE2_COLOR
            canvas.create_rectangle(segment[0], segment[1], segment[0] + SNAKE_SIZE, segment[1] + SNAKE_SIZE,
                                   fill=color, outline='light blue', tags="snake2")

# Function to update the score display
def update_score_display():
    canvas.delete("score")
    canvas.create_text(50, 20, text=f"P1 Score: {score1}", fill="white", font=("Arial", 14), tags="score")
    canvas.create_text(WIDTH // 2, 20, text=f"P1 Lives: {lives1}", fill="white", font=("Arial", 14), tags="score")
   
    if is_multiplayer:
        canvas.create_text(WIDTH - 50, 20, text=f"P2 Score: {score2}", fill="white", font=("Arial", 14), tags="score")
        canvas.create_text(WIDTH // 2, 40, text=f"P2 Lives: {lives2}", fill="white", font=("Arial", 14), tags="score")
   
    canvas.create_text(WIDTH // 2, HEIGHT - 20, text=f"Highest Score: {highest_score}", fill="yellow", font=("Arial", 12), tags="score")

# Function to check collisions
def check_collisions():
    global lives1, lives2, game_over, highest_score

    # Get snake heads
    head1 = snake1[0]
    head2 = snake2[0] if is_multiplayer else None
   
    # Handle head-on collision first (special case)
    if is_multiplayer and head1 == head2:
        lives1 -= 1
        lives2 -= 1
        if lives1 <= 0 or lives2 <= 0:
            game_over = True
            update_highest_score()
        else:
            reset_snake(1)
            reset_snake(2)
            flash_screen("purple")
        return  # Skip other collision checks if head-on collision occurred
   
    # Variables to track if collisions happened
    snake1_collision = False
    snake2_collision = False
   
    # Check if Player 1 collides with itself
    if len(snake1) > 1 and head1 in snake1[1:]:
        snake1_collision = True
   
    # Check if Player 1 hits the border
    if is_on_border(head1):
        snake1_collision = True
   
    # In multiplayer, check if Player 1 collides with Player 2's body
    if is_multiplayer and head1 in snake2[1:]:
        snake1_collision = True
   
    # Handle Player 1 collision
    if snake1_collision:
        lives1 -= 1
        if lives1 <= 0:
            game_over = True
            update_highest_score()
        else:
            reset_snake(1)
            flash_screen("red")
   
    # For multiplayer: Check Player 2 collisions
    if is_multiplayer:
        # Check if Player 2 collides with itself
        if len(snake2) > 1 and head2 in snake2[1:]:
            snake2_collision = True
       
        # Check if Player 2 hits the border
        if is_on_border(head2):
            snake2_collision = True
       
        # Check if Player 2 collides with Player 1's body
        if head2 in snake1[1:]:
            snake2_collision = True
       
        # Handle Player 2 collision
        if snake2_collision:
            lives2 -= 1
            if lives2 <= 0:
                game_over = True
                update_highest_score()
            else:
                reset_snake(2)
                flash_screen("blue")

# Function to flash the screen when a collision occurs
def flash_screen(color):
    flash_rect = canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill=color, stipple="gray50", tags="flash")
    canvas.after(100, lambda: canvas.delete(flash_rect))

# Function to update the highest score
def update_highest_score():
    global highest_score
    if is_multiplayer:
        highest_score = max(highest_score, max(score1, score2))
    else:
        highest_score = max(highest_score, score1)

# Function to reset a snake after losing a life
def reset_snake(player):
    global snake1, snake2, direction1, direction2
    if player == 1:
        # Set snake1 to a safe position within playable area
        snake1 = [(playable_x_min + 3*SNAKE_SIZE, playable_y_min + 3*SNAKE_SIZE)]
        direction1 = 'Right'
    elif player == 2:
        # Set snake2 to a safe position within playable area
        snake2 = [(playable_x_max - 3*SNAKE_SIZE, playable_y_min + 3*SNAKE_SIZE)]
        direction2 = 'Left'

# Function to move the snakes
def move_snakes():
    global snake1, snake2, food, score1, score2, game_over, game_running

    if game_over or game_paused or not game_running:
        return

    # Store old head positions (needed for collision detection)
    old_head1 = snake1[0]
    old_head2 = snake2[0] if is_multiplayer else None

    # Calculate new head positions
    if direction1 == 'Right':
        new_head1 = (old_head1[0] + SNAKE_SIZE, old_head1[1])
    elif direction1 == 'Left':
        new_head1 = (old_head1[0] - SNAKE_SIZE, old_head1[1])
    elif direction1 == 'Up':
        new_head1 = (old_head1[0], old_head1[1] - SNAKE_SIZE)
    elif direction1 == 'Down':
        new_head1 = (old_head1[0], old_head1[1] + SNAKE_SIZE)

    # Calculate Player 2's new head position
    new_head2 = None
    if is_multiplayer:
        if direction2 == 'Right':
            new_head2 = (old_head2[0] + SNAKE_SIZE, old_head2[1])
        elif direction2 == 'Left':
            new_head2 = (old_head2[0] - SNAKE_SIZE, old_head2[1])
        elif direction2 == 'Up':
            new_head2 = (old_head2[0], old_head2[1] - SNAKE_SIZE)
        elif direction2 == 'Down':
            new_head2 = (old_head2[0], old_head2[1] + SNAKE_SIZE)

    # Update snake positions
    snake1.insert(0, new_head1)
    if is_multiplayer and new_head2:
        snake2.insert(0, new_head2)

    # Check if Player 1 eats food
    food_eaten = False
    if new_head1 == food:
        score1 += 10
        food_eaten = True
    else:
        snake1.pop()  # Only remove tail if food not eaten

    # Check if Player 2 eats food
    if is_multiplayer and new_head2 == food:
        score2 += 10
        food_eaten = True
    elif is_multiplayer:
        snake2.pop()  # Only remove tail if food not eaten

    # If food was eaten, spawn new food and speed up the game
    if food_eaten:
        canvas.delete("food")  # Remove the current food
        spawn_food()
        speed_up_game()  # Speed up the game slightly

    # Check for collisions AFTER all movement is completed
    check_collisions()

    # Redraw the game
    draw_snakes()
    update_score_display()

    # Continue the game loop if not over
    if not game_over:
        root.after(speed, move_snakes)
    else:
        show_game_over()

# Function to speed up the game slightly when food is eaten
def speed_up_game():
    global speed
    if speed > 50:
        speed = max(50, speed - 2)  # Speed up slightly, but not too much

# Function to show the Game Over screen
def show_game_over():
    global game_running
    game_running = False
    update_highest_score()
   
    # Create game over text with winner information
    if is_multiplayer:
        if lives1 <= 0 and lives2 <= 0:
            if score1 > score2:
                winner_text = "Player 1 Wins by Score!"
            elif score2 > score1:
                winner_text = "Player 2 Wins by Score!"
            else:
                winner_text = "It's a Tie!"
        elif lives1 <= 0:
            winner_text = "Player 2 Wins!"
        elif lives2 <= 0:
            winner_text = "Player 1 Wins!"
        else:
            # This shouldn't happen, but just in case
            if score1 > score2:
                winner_text = "Player 1 Wins!"
            elif score2 > score1:
                winner_text = "Player 2 Wins!"
            else:
                winner_text = "It's a Tie!"
    else:
        winner_text = f"Your Score: {score1}"
   
    canvas.create_rectangle(WIDTH//4, HEIGHT//4, WIDTH*3//4, HEIGHT*3//4, fill="black", outline="red", width=3)
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 60, text="GAME OVER", fill="red", font=("Arial", 30))
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 20, text=winner_text, fill="white", font=("Arial", 20))
    canvas.create_text(WIDTH // 2, HEIGHT // 2 + 10, text=f"Highest Score: {highest_score}", fill="yellow", font=("Arial", 18))

    play_again_button = tk.Button(root, text="Play Again", font=("Arial", 16), command=start_menu)
    quit_button = tk.Button(root, text="Quit", font=("Arial", 16), command=root.destroy)
    canvas.create_window(WIDTH // 2 - 70, HEIGHT // 2 + 60, window=play_again_button)
    canvas.create_window(WIDTH // 2 + 70, HEIGHT // 2 + 60, window=quit_button)

# Function to start the game
def start_game():
    global game_running
    game_running = True
    reset_game()
    move_snakes()

# Function to reset the game
def reset_game():
    global snake1, snake2, direction1, direction2, food, score1, score2, lives1, lives2, game_over, speed, game_paused
    # Initialize snakes at safe positions inside the playable area
    snake1 = [(playable_x_min + 3*SNAKE_SIZE, playable_y_min + 3*SNAKE_SIZE)]
    snake2 = [(playable_x_max - 3*SNAKE_SIZE, playable_y_min + 3*SNAKE_SIZE)]
    direction1 = 'Right'
    direction2 = 'Left'
    score1 = 0
    score2 = 0
    lives1 = 3
    lives2 = 3
    game_over = False
    game_paused = False
    speed = 100  # Reset speed
    canvas.delete("all")
   
    # Draw border
    draw_border()
   
    # Spawn initial food
    spawn_food()
    update_score_display()

# Function to choose Single Player or Multiplayer
def choose_mode(mode):
    global is_multiplayer
    is_multiplayer = mode == "multiplayer"
    start_game()

# Function to pause/unpause the game
def toggle_pause():
    global game_paused
    if not game_running:
        return
       
    game_paused = not game_paused
   
    if game_paused:
        canvas.create_text(WIDTH // 2, HEIGHT // 2, text="PAUSED", fill="white", font=("Arial", 30), tags="pause")
    else:
        canvas.delete("pause")
        move_snakes()  # Resume movement

# Create start menu
def start_menu():
    global game_running, game_over
    game_running = False
    game_over = False
   
    canvas.delete("all")
   
    # Create a fancy background for the menu
    for i in range(0, WIDTH, SNAKE_SIZE*2):
        for j in range(0, HEIGHT, SNAKE_SIZE*2):
            canvas.create_rectangle(i, j, i+SNAKE_SIZE, j+SNAKE_SIZE, fill=SNAKE1_COLOR, outline="")
           
    # Create semi-transparent overlay
    canvas.create_rectangle(0, 0, WIDTH, HEIGHT, fill="black", stipple="gray50")
   
    canvas.create_text(WIDTH // 2, HEIGHT // 4, text="SNAKE GAME", fill="white", font=("Arial", 36, "bold"))
    canvas.create_text(WIDTH // 2, HEIGHT // 3, text=f"Highest Score: {highest_score}", fill="yellow", font=("Arial", 18))
   
    # Add controls information
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 40, text="Controls:", fill="white", font=("Arial", 14, "bold"))
    canvas.create_text(WIDTH // 2, HEIGHT // 2 - 15, text="Player 1: Arrow Keys", fill="white", font=("Arial", 12))
    canvas.create_text(WIDTH // 2, HEIGHT // 2 + 10, text="Player 2: WASD Keys", fill="white", font=("Arial", 12))
    canvas.create_text(WIDTH // 2, HEIGHT // 2 + 35, text="Press 'P' to pause", fill="white", font=("Arial", 12))
   
    # Create styled buttons
    single_player_button = tk.Button(root, text="Single Player", font=("Arial", 14), bg="green", fg="white",
                                    command=lambda: choose_mode("single"))
    multiplayer_button = tk.Button(root, text="Multiplayer", font=("Arial", 14), bg="blue", fg="white",
                                  command=lambda: choose_mode("multiplayer"))
    quit_button = tk.Button(root, text="Quit Game", font=("Arial", 12), bg="red", fg="white",
                           command=root.destroy)
   
    canvas.create_window(WIDTH // 2, HEIGHT * 2 // 3, window=single_player_button)
    canvas.create_window(WIDTH // 2, HEIGHT * 2 // 3 + 50, window=multiplayer_button)
    canvas.create_window(WIDTH // 2, HEIGHT * 2 // 3 + 100, window=quit_button)

# Start the menu
start_menu()

# Key binding functions
def on_key_press(event):
    global direction1, direction2
   
    # Pause game with 'p' key
    if event.keysym.lower() == 'p':
        toggle_pause()
        return

    if game_paused or not game_running:
        return  # Don't process movement keys when game is paused or not running

    # Player 1 controls (Arrow keys)
    if event.keysym == 'Right' and direction1 != 'Left':
        direction1 = 'Right'
    elif event.keysym == 'Left' and direction1 != 'Right':
        direction1 = 'Left'
    elif event.keysym == 'Up' and direction1 != 'Down':
        direction1 = 'Up'
    elif event.keysym == 'Down' and direction1 != 'Up':
        direction1 = 'Down'

    # Player 2 controls (WASD keys)
    if event.keysym.lower() == 'd' and direction2 != 'Left':
        direction2 = 'Right'
    elif event.keysym.lower() == 'a' and direction2 != 'Right':
        direction2 = 'Left'
    elif event.keysym.lower() == 'w' and direction2 != 'Down':
        direction2 = 'Up'
    elif event.keysym.lower() == 's' and direction2 != 'Up':
        direction2 = 'Down'

# Run the tkinter main loop
root.bind("<KeyPress>", on_key_press)
root.mainloop()
