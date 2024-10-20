"""
Simple assisted comms board with moving cursor for integration
with blink detection.
Adapted from simpson college pygame tile sample.
"""
import pygame
# Define some colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
GREENISH = (220, 255, 220)
RED = (255, 0, 0)

# This sets the WIDTH and HEIGHT of each grid location
WIDTH = 60
HEIGHT = 40
 
# This sets the margin between each cell
MARGIN = 5

# Create a 2 dimensional array. A two dimensional
# array is simply a list of lists.
grid = []
# use gridsize if square:
ROWS = 6
COLS = 7
for row in range(ROWS):
    # Add an empty array that will hold each cell
    # in this row
    grid.append([])
    for column in range(COLS):
        grid[row].append(0)  # Append a cell
 
# alphabet_string = "abcdefghijklmnopqrstuvwxyz"
# link to CIR board: 
# http://www.instructables.com/id/Communication-Board-for-Individuals-with-Disabilit/
CIRORDER = "AEIOU5bfjpv6cgkqw7dhlrx813msy924ntz0"
# pad it with one extra column worth of spaces
alphabet = " "*ROWS + CIRORDER
# create alphabet position dict that we will populate later in grid loop
alphabet_pos = {}
# MESSAGE string to log to console in course of game
MESSAGE = ""

# Set row 1, cell 5 to one. (Remember rows and
# column numbers start at zero.)
# grid[1][5] = 1
 
# Initialize pygame
pygame.init()

# set font for text display in each grid
myfont = pygame.font.SysFont("monospace", 30)
letter = "T"
testTextRect = myfont.render(letter, 1, BLACK).get_rect()
# USAGE: font.render(text, antialias, color, background=None)


# Set the HEIGHT and WIDTH of the screen
winHeight = ROWS*(HEIGHT+MARGIN)+ MARGIN
winWidth = COLS*(WIDTH+MARGIN) + MARGIN
WINDOW_SIZE = [winWidth, winHeight]
screen = pygame.display.set_mode(WINDOW_SIZE)
 
# Set title of screen
pygame.display.set_caption("Array Backed Grid")
 
# Loop until the user clicks the close button.
done = False
 
# Used to manage how fast the screen updates
clock = pygame.time.Clock()
 
# render some letters
font = pygame.font.SysFont('arial', 40)


# get text objects:
def text_objects(text):
    """takes string, returns a textSurface object and its rectangular coords"""
    textSurface = font.render(text, True, (0, 50, 0))
    return textSurface, textSurface.get_rect()

# create own event for timer interruption, blink
cursor_timer = pygame.USEREVENT + 1
blink = pygame.USEREVENT + 2
CURSORDELAY = 1000
pygame.time.set_timer(cursor_timer, CURSORDELAY)

# -------- Event handlers  -----------
def clickToggle():
    """toggles value of tile that is clicked to change color"""
    # User clicks the mouse. Get the position
    pos = pygame.mouse.get_pos()
    # Change the x/y screen coordinates to grid coordinates
    column = pos[0] // (WIDTH + MARGIN)
    row = pos[1] // (HEIGHT + MARGIN)
    # toggle value of that tile
    toggle_grid(row, column)
    # print("Click ", pos, "Grid coordinates: ", row, column)
    clicked_str = alphabet_pos[(row, column)]
    console_msg = "Clicked char {0} at grid point {1}:{2}".format(clicked_str,row, column)
    # could add functionality to log selected chars to message string
    # for now just print one selected char at a time
    print(console_msg)

def toggle_grid(row, column, only_one_active=True):
    """toggle a single grid position's value between 0 and 1"""
    if grid[row][column] == 0:
        grid[row][column] = 1
    else:
        grid[row][column] = 0

def inc_before_end(c,end):
    """mini function to increment counter until end of list then reset"""
    if c < end -1:
        return c+1
    else: 
        return 0


def movingCursor(currentTile, downwards):
    """move cursor down or sideways based on timer"""
    x, y = currentTile
    if downwards:
        # move down as long until active hits lower end, then reset
        x = inc_before_end(x, ROWS)
    else:
        # move sideways, i.e. increment col instead
        y = inc_before_end(currentTile[1], COLS)
    # return tuple with new position
    return (x,y)


# initialise first tile for beginning of game:
currentTile = (0,0)
# toggle_grid(*currentTile)
# also, in beginning we want the cursor to move downwards 
downwards = True
# -------- Main Program Loop -----------
while not done:
    ### event handling part...
    for event in pygame.event.get():  # User did something
        if event.type == pygame.QUIT:  # If user clicked close
            done = True  # Flag that we are done so we exit this loop
        elif event.type == pygame.MOUSEBUTTONDOWN:
            # old:
            # clickToggle()
            # new: click changes direction of cursor
            if currentTile[1] != 0:
                MESSAGE = MESSAGE + alphabet_pos[currentTile]
                print(MESSAGE)
                currentTile = (0,0)
                downwards = True
            elif downwards:
                downwards = False
        elif event.type == cursor_timer:
            # cycle cursor through first row
            currentTile = movingCursor(currentTile, downwards)
            # toggle_grid(*currentTile)

    ### rendering part...
    # Set the screen background
    screen.fill(BLACK)
    # Draw the grid
    # extra string_counter for CIR board implementation
    string_counter = 0
    for column in range(COLS):
        for row in range(ROWS):
            color = WHITE
            # old: if grid[row][column] == 1:
            # new: recolor currently active row in lighter color
            if row == currentTile[0]:
                color = GREENISH
            # also highlight active tile in strong color:
            if (row, column) == currentTile:
                color = GREEN
            x_coord = (MARGIN + WIDTH) * column + MARGIN
            y_coord = (MARGIN + HEIGHT) * row + MARGIN
            pygame.draw.rect(screen,
                             color,
                             [x_coord, y_coord, WIDTH, HEIGHT])
            # in loop also insert CIR board chars on screen:
            currentChar = alphabet[string_counter]
            surf, rect = text_objects(currentChar)
            screen.blit(surf, (x_coord, y_coord))
            # index chars in dict with row/column tuple as key:
            alphabet_pos.update({(row, column): currentChar})
            string_counter += 1
    # Limit to 60 frames per second
    clock.tick(60)
    # timer test code:
    # milliseconds += clock.tick_busy_loop(60)
    # Go ahead and update the screen with what we've drawn.
    pygame.display.flip()
 
# Be IDLE friendly. If you forget this line, the program will 'hang'
# on exit.
pygame.quit()