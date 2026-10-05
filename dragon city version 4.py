import random
import tkinter as tk
from tkinter import simpledialog, messagebox

# ---------- settings ----------
SIZE = 10          # the grid is 10 x 10
CELL = 80          # size of each square in pixels

# ---------- game variables ----------
name = "Hero"
player_row = 0
player_col = 0
attack = 5
shield = 0
gold = 0
level = 1
grid = []          # the map (list of lists)
labels = []        # the label for every square on the screen


def make_map():
    """Makes a new random map."""
    global grid
    grid = []
    for r in range(SIZE):
        row = []
        for c in range(SIZE):
            row.append(".")
        grid.append(row)

    # fixed things
    grid[1][0] = "E5"      # easy enemy next to the start
    grid[9][9] = "S"       # safe zone
    grid[8][9] = "E75"     # bosses guarding the safe zone
    grid[9][8] = "E75"

    # make a list of all the empty squares and shuffle it
    empty = []
    for r in range(SIZE):
        for c in range(SIZE):
            if grid[r][c] == "." and not (r == 0 and c == 0):
                empty.append((r, c))
    random.shuffle(empty)

    # 5 gold
    for i in range(5):
        r, c = empty.pop()
        grid[r][c] = "T"

    # 4 shields
    for i in range(4):
        r, c = empty.pop()
        grid[r][c] = "P"

    # 10 enemies with different power
    for power in [10, 15, 20, 25, 30, 35, 40, 50, 60, 70]:
        r, c = empty.pop()
        grid[r][c] = "E" + str(power)


def draw():
    """Updates the screen to match the game variables."""
    stats.config(text=name + "  |  Attack: " + str(attack) +
                 "  |  Shield: " + str(shield) +
                 "  |  Gold: " + str(gold) +
                 "  |  Level: " + str(level))

    for r in range(SIZE):
        for c in range(SIZE):
            tile = grid[r][c]

            if r == player_row and c == player_col:
                text = name[:6].upper() + "\nATK:" + str(attack)
                bg = "#3498db"
                fg = "white"
            elif tile == "T":
                text, bg, fg = "GOLD", "#f1c40f", "black"
            elif tile == "P":
                text, bg, fg = "SHIELD", "#2ecc71", "white"
            elif tile == "S":
                text, bg, fg = "SAFE\nZONE", "#9b59b6", "white"
            elif tile == "E75":
                text, bg, fg = "BOSS\n75", "#8b0000", "white"
            elif tile.startswith("E"):
                text, bg, fg = "ENEMY\n" + tile[1:], "#e74c3c", "white"
            else:
                text, bg, fg = "", "#ecf0f1", "black"

            labels[r][c].config(text=text, bg=bg, fg=fg)


def fight(enemy_power):
    """Returns True if the player wins the fight."""
    global attack, shield, level

    if attack >= enemy_power:
        attack = attack + enemy_power    # absorb the enemy's power
        level = level + 1
        return True

    # player loses: shield takes the damage first
    damage = enemy_power
    if shield >= damage:
        shield = shield - damage
        damage = 0
    else:
        damage = damage - shield
        shield = 0
    attack = attack - damage
    if attack < 0:
        attack = 0
    return False


def move(event):
    """Runs every time a key is pressed."""
    global player_row, player_col, gold, shield

    key = event.keysym.lower()
    new_row = player_row
    new_col = player_col

    if key == "w":
        new_row = new_row - 1
    elif key == "s":
        new_row = new_row + 1
    elif key == "a":
        new_col = new_col - 1
    elif key == "d":
        new_col = new_col + 1
    else:
        return   # some other key, do nothing

    # stay inside the grid
    if new_row < 0 or new_row >= SIZE or new_col < 0 or new_col >= SIZE:
        return

    tile = grid[new_row][new_col]
    can_move = True

    if tile.startswith("E"):
        power = int(tile[1:])
        won = fight(power)
        if won:
            grid[new_row][new_col] = "."
        else:
            can_move = False     # enemy is still there, so we can't step on it

    elif tile == "T":
        gold = gold + 50
        grid[new_row][new_col] = "."

    elif tile == "P":
        shield = shield + 20
        grid[new_row][new_col] = "."

    if can_move:
        player_row = new_row
        player_col = new_col

    draw()
    check_end()


def check_end():
    """Checks if the player has won or lost."""
    if attack <= 0:
        again = messagebox.askyesno("GAME OVER",
                                    name + " was defeated!\n"
                                    "Level: " + str(level) + "   Gold: " + str(gold) +
                                    "\n\nTry again?")
        end_game(again)
    elif grid[player_row][player_col] == "S" or (player_row == 9 and player_col == 9):
        again = messagebox.askyesno("YOU WIN!",
                                    name + " reached the safe zone!\n"
                                    "Level: " + str(level) + "   Gold: " + str(gold) +
                                    "\n\nPlay again?")
        end_game(again)


def end_game(play_again):
    """Restarts the game or closes the window."""
    global player_row, player_col, attack, shield, gold, level

    if play_again:
        player_row = 0
        player_col = 0
        attack = 5
        shield = 0
        gold = 0
        level = 1
        make_map()
        draw()
    else:
        root.destroy()


# ---------- set up the window ----------
root = tk.Tk()
root.withdraw()
answer = simpledialog.askstring("Dragon City"
                                "Enter your Dragon's name:")
if answer and answer.strip() != "":
    name = answer.strip()
root.deiconify()

root.title("Dragon city")
root.geometry("860x960")
root.configure(bg="#2c3e50")

stats = tk.Label(root, font=("Helvetica", 14, "bold"), bg="#2c3e50", fg="#f1c40f")
stats.grid(row=0, column=0, columnspan=SIZE, pady=12)

# make the grid of labels
for r in range(SIZE):
    row_of_labels = []
    for c in range(SIZE):
        frame = tk.Frame(root, width=CELL, height=CELL)
        frame.grid(row=r + 1, column=c, padx=1, pady=1)
        frame.pack_propagate(False)
        lab = tk.Label(frame, borderwidth=2, relief="raised",
                       font=("Helvetica", 11, "bold"))
        lab.pack(fill="both", expand=True)
        row_of_labels.append(lab)
    labels.append(row_of_labels)

root.bind("<KeyPress>", move)

make_map()
draw()
root.mainloop()
