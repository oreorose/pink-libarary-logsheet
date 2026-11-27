from tkinter import *
import random
import math

root = Tk()
root.title("Patrick's Bikini Bottom Swim")
root.geometry("600x480")
root.configure(bg="#1A2B3C")

# Main Canvas matching image dimensions aspect ratio
canvas = Canvas(root, width=560, height=320, highlightthickness=2, highlightbackground="#38A1DB")
canvas.pack(pady=10)

# --- DRAWING BIKINI BOTTOM BACKGROUND ---
def draw_background():
    # Pastel background gradient stripes (matching the reference image)
    canvas.create_rectangle(0, 0, 560, 55, fill="#FFD1DC", outline="")    # Pastel Pink
    canvas.create_rectangle(0, 55, 560, 110, fill="#FFE5B4", outline="")  # Pastel Yellow
    canvas.create_rectangle(0, 110, 560, 165, fill="#C5E0B4", outline="") # Pastel Soft Green
    canvas.create_rectangle(0, 165, 560, 220, fill="#B4E1FF", outline="") # Ocean Blue
    canvas.create_rectangle(0, 220, 560, 320, fill="#E6D595", outline="") # Sand Floor

    # Draw Sand Dunes
    canvas.create_oval(-50, 230, 250, 360, fill="#CDBA76", outline="")
    canvas.create_oval(320, 240, 600, 370, fill="#CDBA76", outline="")

    # Flower Clouds (Background)
    draw_flower_cloud(100, 35, "#A0C4FF", 18)
    draw_flower_cloud(300, 28, "#A0C4FF", 22)
    draw_flower_cloud(500, 40, "#A0C4FF", 18)
    draw_flower_cloud(270, 130, "#FFB7B2", 30) # Center large pink flower
    draw_flower_cloud(60, 140, "#FFB7B2", 20)
    draw_flower_cloud(440, 110, "#FFB7B2", 16)

    # Scenery Props: Rocks & Coral Plants
    canvas.create_oval(60, 225, 110, 255, fill="#D0D0D0", outline="#888")
    canvas.create_oval(90, 220, 140, 253, fill="#E0E0E0", outline="#888")
    canvas.create_line(60, 225, 55, 185, 65, 165, fill="#4CAF50", width=4, smooth=True)
    canvas.create_line(68, 225, 75, 195, 70, 170, fill="#81C784", width=3, smooth=True)

    canvas.create_oval(430, 215, 480, 250, fill="#E0E0E0", outline="#888")
    canvas.create_oval(410, 235, 460, 260, fill="#CCCCCC", outline="#888")
    canvas.create_oval(425, 200, 455, 230, fill="#E1BEE7", outline="#BA68C8", width=2)
    canvas.create_oval(433, 207, 439, 213, fill="#8E24AA", outline="")
    canvas.create_oval(442, 217, 448, 223, fill="#8E24AA", outline="")

def draw_flower_cloud(cx, cy, color, r):
    petals = [
        (cx, cy - r),
        (cx + r * 0.95, cy - r * 0.31),
        (cx + r * 0.59, cy + r * 0.81),
        (cx - r * 0.59, cy + r * 0.81),
        (cx - r * 0.95, cy - r * 0.31)
    ]
    for px, py in petals:
        canvas.create_oval(px - r*0.6, py - r*0.6, px + r*0.6, py + r*0.6, outline=color, width=3)
    canvas.create_oval(cx - r*0.5, cy - r*0.5, cx + r*0.5, cy + r*0.5, outline=color, width=2)

draw_background()

# --- GAME VARIABLES ---
velocity = 0
gravity = 0.3
lift = -5.5
game_running = False
score = 0
current_angle = 0

# --- PLAYER: PATRICK STAR (Base Coordinates) ---
base_patrick_points = [
    100, 130, # Top point
    107, 145, # Inner right top
    122, 145, # Right arm
    110, 155, # Inner right bottom
    115, 170, # Right leg
    100, 160, # Bottom crotch
    85, 170,  # Left leg
    90, 155,  # Inner left bottom
    78, 145,  # Left arm
    93, 145   # Inner left top
]

patrick = canvas.create_polygon(base_patrick_points, fill="#FF9999", outline="#FF6688", width=2)

# Adjusted smaller score text display size
score_text = canvas.create_text(500, 20, text="SCORE: 0", font=("Arial", 9, "bold"), fill="#1A2B3C")

obstacles = []

def rotate_points(points, angle_deg, cx, cy):
    rad = math.radians(angle_deg)
    cos_a = math.cos(rad)
    sin_a = math.sin(rad)
    new_pts = []
    for i in range(0, len(points), 2):
        x = points[i] - cx
        y = points[i+1] - cy
        nx = x * cos_a - y * sin_a + cx
        ny = x * sin_a + y * cos_a + cy
        new_pts.extend([nx, ny])
    return new_pts

def spin_animation(target_angle, steps=5, current_step=0):
    global current_angle
    if not game_running:
        return
    if current_step <= steps:
        current_angle += (target_angle / steps)
        bbox = canvas.bbox(patrick)
        if bbox:
            cx = (bbox[0] + bbox[2]) / 2
            cy = (bbox[1] + bbox[3]) / 2
            rotated = rotate_points(base_patrick_points, current_angle, 100, 150)
            dx = cx - 100
            dy = cy - 150
            final_pts = [p + (dx if i%2==0 else dy) for i, p in enumerate(rotated)]
            canvas.coords(patrick, *final_pts)
            
        root.after(25, lambda: spin_animation(target_angle, steps, current_step + 1))

def jump(event=None):
    global velocity
    if game_running:
        velocity = lift
        spin_animation(360, steps=6)

def start_game():
    global game_running, score, velocity, obstacles, current_angle
    if game_running:
        return
    
    canvas.delete("game_over_ui")
    for pair in obstacles:
        for part in pair:
            canvas.delete(part)
    obstacles.clear()
    
    current_angle = 0
    canvas.coords(patrick, *base_patrick_points)
    velocity = 0
    score = 0
    canvas.itemconfig(score_text, text="SCORE: 0")
    game_running = True
    
    update_game()
    game_loop()

def create_obstacle():
    if not game_running:
        return
    gap_y = random.randint(60, 160)
    gap_size = 95
    
    top_main = canvas.create_rectangle(565, 0, 595, gap_y, fill="#1E5631", outline="#0F2E19", width=2)
    top_rib1 = canvas.create_line(580, 0, 580, gap_y, fill="#2E8B57", width=3)
    top_leaf1 = canvas.create_oval(555, gap_y - 60, 575, gap_y - 30, fill="#2E8B57", outline="#1E5631")
    top_leaf2 = canvas.create_oval(585, gap_y - 40, 605, gap_y - 15, fill="#3CB371", outline="#1E5631")
    
    bot_main = canvas.create_rectangle(565, gap_y + gap_size, 595, 320, fill="#1E5631", outline="#0F2E19", width=2)
    bot_rib1 = canvas.create_line(580, gap_y + gap_size, 580, 320, fill="#2E8B57", width=3)
    bot_leaf1 = canvas.create_oval(555, gap_y + gap_size + 30, 575, gap_y + gap_size + 60, fill="#3CB371", outline="#1E5631")
    bot_leaf2 = canvas.create_oval(585, gap_y + gap_size + 15, 605, gap_y + gap_size + 40, fill="#2E8B57", outline="#1E5631")

    top_group = (top_main, top_rib1, top_leaf1, top_leaf2)
    bot_group = (bot_main, bot_rib1, bot_leaf1, bot_leaf2)
    
    obstacles.append((top_group, bot_group))

def move_obstacles():
    global game_running, score
    for top_group, bot_group in obstacles:
        for part in top_group:
            canvas.move(part, -4, 0)
        for part in bot_group:
            canvas.move(part, -4, 0)

    px1, py1, px2, py2 = canvas.bbox(patrick)
    for top_group, bot_group in obstacles:
        top_rect_coords = canvas.coords(top_group[0])
        bot_rect_coords = canvas.coords(bot_group[0])
        
        if px2 > top_rect_coords[0] and px1 < top_rect_coords[2] and py1 < top_rect_coords[3]:
            game_over()
            return
        if px2 > bot_rect_coords[0] and px1 < bot_rect_coords[2] and py2 > bot_rect_coords[1]:
            game_over()
            return

    if obstacles:
        first_top_main = obstacles[0][0][0]
        if canvas.coords(first_top_main)[2] < 0:
            for part in obstacles[0][0]:
                canvas.delete(part)
            for part in obstacles[0][1]:
                canvas.delete(part)
            obstacles.pop(0)
            score += 1
            canvas.itemconfig(score_text, text=f"SCORE: {score}")

def game_over():
    global game_running
    game_running = False
    
    # Adjusted text sizes for "OUT OF WATER!" and "FINAL SCORE" inside the game over card
    canvas.create_rectangle(130, 100, 430, 220, fill="#0F4C81", outline="#00D2FC", width=3, tag="game_over_ui")
    canvas.create_text(280, 135, text="OUT OF WATER!", font=("Comic Sans MS", 14, "bold"), fill="#00D2FC", tag="game_over_ui")
    canvas.create_text(280, 175, text=f"FINAL SCORE: {score}", font=("Comic Sans MS", 11, "bold"), fill="#E0F7FA", tag="game_over_ui")

def update_game():
    if not game_running:
        return

    global velocity
    velocity += gravity
    canvas.move(patrick, 0, velocity)
    
    x1, y1, x2, y2 = canvas.bbox(patrick)
    if y1 <= 0 or y2 >= 320:
        game_over()
        return

    move_obstacles()
    root.after(30, update_game)

def game_loop():
    if not game_running:
        return
    create_obstacle()
    root.after(1600, game_loop)

# Keyboard Controls
root.bind("<space>", jump)
root.bind("<Up>", jump)

# Control Buttons Frame
btn_frame = Frame(root, bg="#1A2B3C")
btn_frame.pack(pady=10)

start_btn = Button(
    btn_frame, text="START", font=("Arial", 10, "bold"),
    bg="#2E8B57", fg="#FFFFFF", activebackground="#3CB371", activeforeground="#FFFFFF",
    relief="raised", width=12, pady=5, command=start_game
)
start_btn.pack(side=LEFT, padx=10)

swim_btn = Button(
    btn_frame, text="SWIM (BOSS)", font=("Arial", 10, "bold"),
    bg="#FF9999", fg="#1A2B3C", activebackground="#FF6688", activeforeground="#FFFFFF",
    relief="raised", width=14, pady=5, command=jump
)
swim_btn.pack(side=LEFT, padx=10)

root.mainloop()

