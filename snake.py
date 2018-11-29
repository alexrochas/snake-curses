import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
import tensorflow as tf
from tensorflow import layers
from numpy import array

curses.initscr()
win = curses.newwin(20, 60, 0, 0)
win.keypad(1)
curses.noecho()
curses.curs_set(0)
win.border(0)
win.nodelay(1)

score = 0
deaths = 0
key = -1                                                    # Initializing values

start = 0
init_text = 0

snake = [[4,10], [4,9], [4,8]]                                     # Initial snake co-ordinates
food = [11,20]                                                     # First food co-ordinates

win.addch(food[0], food[1], '*')                                   # Prints the food
win.addstr(10, 19, 'PRESS ANY KEY TO START')

KEYS = [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN]


def future_position(snake, key):
    return [snake[0][0] + (key == KEY_DOWN and 1) + (key == KEY_UP and -1), snake[0][1] + (key == KEY_LEFT and -1) + (key == KEY_RIGHT and 1)]


def snake_out_of_bounds(snake):
    return snake[0][0] == 0 or snake[0][0] == 19 or snake[0][1] == 0 or snake[0][1] == 59 or snake[0] in snake[1:]


def action():
    return KEYS[randint(0, 3)]


def training_model():
    model = tf.keras.Sequential([
    # Adds a densely-connected layer with 64 units to the model:
    layers.Dense(64, activation='relu'),
    # Add another:
    layers.Dense(64, activation='relu'),
    # Add a softmax layer with 10 output units:
    layers.Dense(10, activation='softmax')])

    model.compile(optimizer=tf.train.AdamOptimizer(0.001),
                  loss='categorical_crossentropy',
                  metrics=['accuracy'])

    return model

training_data = []
loop = 0

while key != 27 and loop < 1:                                                   # While Esc key is not pressed
    win.border(0)
    win.addstr(0, 2, 'Score : ' + str(score) + ' ')                # Printing 'Score' and
    win.addstr(0, 14, 'Deaths : ' + str(deaths) + ' ')                # Printing 'Score' and
    win.addstr(0, 27, ' SNAKE ')                                   # 'SNAKE' strings
    win.timeout(150 - (len(snake) / 5 + len(snake) / 10) % 120)          # Increases the speed of Snake as its length increases

    prevKey = key                                                  # Previous key pressed
    key = KEY_RIGHT if start != 1 else action()
    event = win.getch()
    event = key
    snake_before_move = snake
    key = key if event == -1 else event

    if start != 0 and init_text == 0:
        init_text = 1
        win.addstr(10, 19, '                      ')

    if start == 1 or event != -1:
        start = 1
        died = 0
        if key == ord(' '):                                            # If SPACE BAR is pressed, wait for another
            key = -1                                                   # one (Pause/Resume)
            while key != ord(' '):
                key = win.getch()
            key = prevKey
            continue

        if key not in [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, 27]:     # If an invalid key is pressed
            key = prevKey

        # Calculates the new coordinates of the head of the snake. NOTE: len(snake) increases.
        # This is taken care of later at [1].
        key = prevKey if abs(prevKey - key) == 1 else key
        snake.insert(0, future_position(snake, key))

        # Exit if snake crosses the boundaries (Uncomment to enable)
        if snake_out_of_bounds(snake):
            win.clear()
            key = -1                                                    # Initializing values

            start = 0
            init_text = 0

            snake = [[4,10], [4,9], [4,8]]                                     # Initial snake co-ordinates
            food = [11,20]                                                     # First food co-ordinates

            win.addch(food[0], food[1], '*')                                   # Prints the food
            win.addstr(10, 19, 'PRESS ANY KEY TO START')
            deaths += 1
            died = 1
            loop += 1
            training_data.append(array([snake_before_move, key, died]))

        if snake[0] == food:                                            # When snake eats the food
            food = []
            score += 1
            while food == []:
                food = [randint(1, 18), randint(1, 58)]                 # Calculating next food's coordinates
                if food in snake: food = []
            win.addch(food[0], food[1], '*')
        else:
            last = snake.pop()                                          # [1] If it does not eat the food, length decreases
            win.addch(last[0], last[1], ' ')
        win.addch(snake[0][0], snake[0][1], '#')

curses.endwin()

x = array([i[0] for i in training_data]).reshape(8,)
y = array([i[0] for i in ['snake position', 'key', 'is dead?']]).reshape(3,)
training_model().fit(x, y, epochs=10, batch_size=32)

print("\nScore - " + str(score))
print("http://bitemelater.in\n")
