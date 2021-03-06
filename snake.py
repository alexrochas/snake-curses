import curses
from curses import KEY_RIGHT, KEY_LEFT, KEY_UP, KEY_DOWN
from random import randint
import tensorflow as tf
from tensorflow import layers
import numpy as np
import os

from keras.models import Sequential
from keras.layers import Dense
from keras.layers import Flatten
from tflearn.layers.core import input_data, fully_connected
from tflearn.layers.estimator import regression
import tflearn

os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

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

KEYS = [KEY_LEFT, KEY_RIGHT, KEY_UP, KEY_DOWN, -1]


def future_position(snake, key):
    return [snake[0][0] + (key == KEY_DOWN and 1) + (key == KEY_UP and -1), snake[0][1] + (key == KEY_LEFT and -1) + (key == KEY_RIGHT and 1)]


def snake_out_of_bounds(snake):
    result = snake[0][0] == 0 or snake[0][0] == 19 or snake[0][1] == 0 or snake[0][1] == 59 or snake[0] in snake[1:]
    print result
    return result


def action():
    return KEYS[randint(0, 3)]


def training_model(size):
    model = Sequential()
    model.add(Dense(16, input_dim=3, activation='relu'))
    model.add(Dense(16, activation='relu'))
    model.add(Dense(1, activation='linear'))
    model.compile(loss='binary_crossentropy', optimizer='adam')
    # network = input_data(shape=[None, 3, 1], name='input')
    # network = fully_connected(network, 25, activation='relu')
    # network = fully_connected(network, 25, activation='relu')
    # network = fully_connected(network, 1, activation='linear')
    # network = regression(network, optimizer='adam', learning_rate=1e-2, loss='mean_square', name='target')
    # model = tflearn.DNN(network, tensorboard_dir='log')
    return model

training_data = []
steps = []
loop = 0
n_loops = 1000

while key != 27 and loop < n_loops:                                                   # While Esc key is not pressed
    win.border(0)
    win.addstr(0, 2, 'Score : ' + str(score) + ' ')                # Printing 'Score' and
    win.addstr(0, 14, 'Deaths : ' + str(deaths) + ' ')                # Printing 'Score' and
    win.addstr(0, 27, ' SNAKE ')                                   # 'SNAKE' strings
    # win.timeout(150 - (len(snake) / 5 + len(snake) / 10) % 120)          # Increases the speed of Snake as its length increases
    win.timeout(1)          # Increases the speed of Snake as its length increases

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
            training_data.append([[int(KEYS.index(prevKey)), int(KEYS.index(key)), int(snake_out_of_bounds(snake))], 1])
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
        else:
            training_data.append([[int(KEYS.index(prevKey)), int(KEYS.index(key)), int(snake_out_of_bounds(snake))], 0])


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
        # left 0 right 1 up 2 down 3
        # direction, have obstacle, decision

curses.endwin()
#
# for i in range(0,100):
#     training_data.append([[int(KEYS.index(KEY_LEFT)), int(KEYS.index(KEY_LEFT)), int(1)], 1])
#     training_data.append([[int(KEYS.index(KEY_RIGHT)), int(KEYS.index(KEY_RIGHT)), int(1)], 1])
#     training_data.append([[int(KEYS.index(KEY_UP)), int(KEYS.index(KEY_UP)), int(1)], 1])
#     training_data.append([[int(KEYS.index(KEY_DOWN)), int(KEYS.index(KEY_DOWN)), int(1)], 1])

x = np.array([i[0] for i in training_data]) #.reshape(-1, 3, 1)
y = np.array([i[1] for i in training_data]) #.reshape(-1, 1)
import pprint
pprint.pprint(training_data)
model = training_model(len(x))
model.fit(x, y, epochs=3, shuffle = True, verbose=1)
results = []
for k in range(0,4):
    results.append(model.predict(np.array([3,k,1]).reshape(-1,3))) #.reshape(-1, 3, 1)))
    results.append(model.predict_classes(np.array([3,k,1]).reshape(-1,3))) #.reshape(-1, 3, 1)))
pprint.pprint(results)
#print(model.predict(np.array([int(KEY_LEFT), int(KEY_LEFT), int(1)]))) #.reshape(-1, 3, 1)))
model.save('snake_bot.h5')


print("\nScore - " + str(score))
print("http://bitemelater.in\n")
