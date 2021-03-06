import gc
import random
import time
from boilerboard import Boilerboard
from boilerboard import Buttons

#define screen boundaries for the snake
X_MIN = 0
X_MAX = 124
Y_MIN = 12
Y_MAX = 60

class Snake:

    #initialization function for Snake class
    def __init__(self):
        #initialize Boilerboard class
        self.snake = [[16,32],[12,32],[8,32],[4,32]]
        self.bb = Boilerboard()
        #initialize butons for board
        self.buttons = Buttons(self.bb.i2c)
        #assign directions snake can travel for cooresponding button press
        self.directions = [self.buttons.RIGHT, self.buttons.RIGHT, self.buttons.RIGHT, self.buttons.RIGHT]

    #starts and runs the snake game
    def start(self):
        food_not_present = True
        food = [0,0]
        score = -1
        gameover = 0

        #seeds for random function
        a0 = 12345
        b0 = 34567
        c0 = 12789
        d0 = 23893
        e0 = 56788

        #turn all pixels on screen off
        self.bb.screen.clear(0)
        #write name of game on screen
        self.bb.screen.lcd.text('BOILER SNAKE', 18,26)
        #display screen
        self.bb.screen.lcd.show()
        time.sleep(1)

        #main loop that runs game
        while True:
            print("location: ", self.snake[0])
            #if game over
            if gameover != 0:
                #turn all pixels on screen off
                self.bb.screen.clear(0)
                #write GAME OVER on screen
                self.bb.screen.lcd.text('GAME OVER', 27,26)
                #display screen
                self.bb.screen.lcd.show()
                time.sleep(1)
                self.snake = [[16,32],[12,32],[8,32],[4,32]]
                self.directions = [self.buttons.RIGHT, self.buttons.RIGHT, self.buttons.RIGHT, self.buttons.RIGHT]
                return

            #if winning score of 15 is met
            if score == 15:
                #turn all pixels on screen off
                self.bb.screen.clear(0)
                #write You win! on screen
                self.bb.screen.lcd.text('You win!', 27, 26)
                #display screen
                self.bb.screen.lcd.show()
                return

            #if snake eats food or food is not present
            if (self.snake[0] == food) or food_not_present:
                #generate random food location
                x_food, a0, b0, c0, d0, e0 = random.randomInt(X_MIN, X_MAX, a0, b0, c0, d0, e0)
                y_food, a0, b0, c0, d0, e0 = random.randomInt(Y_MIN, Y_MAX, a0, b0, c0, d0, e0)
                food = [int(x_food/4)*4, int(y_food/4)*4]
                score += 1
                #adding unit to snake
                if not food_not_present:
                    if   self.directions[-1] == self.buttons.UP:
                        self.snake.append([self.snake[-1][0], self.snake[-1][1]+4])
                    elif self.directions[-1] == self.buttons.DOWN:
                        self.snake.append([self.snake[-1][0], self.snake[-1][1]-4])
                    elif self.directions[-1] == self.buttons.LEFT:
                        self.snake.append([self.snake[-1][0]+4, self.snake[-1][1]])
                    elif self.directions[-1] == self.buttons.RIGHT:
                        self.snake.append([self.snake[-1][0]-4, self.snake[-1][1]])
                    self.directions.append(self.directions[-1])
                food_not_present = False

            #update score and food position
            self.bb.screen.clear(0)
            self.bb.screen.lcd.text('SCORE:', 37, 0)
            self.bb.screen.lcd.text(str(score), 84, 0)
            self.displaySolidUnit(food)

            self.checkButtonPress()

            #display snake
            for i in range(0, len(self.snake)):
                self.displayHollowUnit(self.snake[i])

            self.bb.screen.lcd.show()
            #increase gameover
            gameover += self.updateSnake()
            #update direction of snake
            self.updateDirections()

            #determine speed of snake based on score
            if score <= 9:
                time.sleep((50-(score*5))/1000)
            else:
                time.sleep((50-(49))/1000)

            #garbage collection
            gc.collect()

    def checkButtonPress(self):
        #check for button press
        button = self.bb.irq.get_pressed_button()
        #if a button is pressed
        if button is not None:
            #if up is pressed and not moving down
            if   button == self.buttons.UP    and self.directions[0] != self.buttons.DOWN:
                self.directions[0] = self.buttons.UP
            #else if down is pressed and not moving up
            elif button == self.buttons.DOWN  and self.directions[0] != self.buttons.UP:
                self.directions[0] = self.buttons.DOWN
            #else if left is pressed and not moving right
            elif button == self.buttons.LEFT  and self.directions[0] != self.buttons.RIGHT:
                self.directions[0] = self.buttons.LEFT
            #else if right is pressed and not moving left
            elif button == self.buttons.RIGHT and self.directions[0] != self.buttons.LEFT:
                self.directions[0] = self.buttons.RIGHT

    #update state and condition of snake
    def updateSnake(self):
        p_index = 0
        gameover = 0
        if self.snake[0] in self.snake[1:]:
            return 1
        for p in self.snake:
            if self.directions[p_index] == self.buttons.LEFT:
                if p[0] < X_MIN:
                    gameover = 1
                    break
                else:
                    p[0] -= 4
            if self.directions[p_index] == self.buttons.RIGHT:
                if p[0] > X_MAX:
                    gameover = 1
                    break
                else:
                    p[0] += 4
            if self.directions[p_index] == self.buttons.UP:
                if p[1] < Y_MIN:
                    gameover = 1
                    break
                else:
                    p[1] -= 4
            if self.directions[p_index] == self.buttons.DOWN:
                if p[1] > Y_MAX:
                    gameover = 1
                    break
                else:
                    p[1] += 4
            p_index += 1
        return gameover

    #update direction snake travels
    def updateDirections(self):
        for i in range(len(self.directions)-1, 0, -1):
            self.directions[i] = self.directions[i-1]

    #display something that can be passed through
    def displayHollowUnit(self, p):
        self.bb.screen.lcd.rect(p[0],p[1],4,4,1)

    #display something that cannot be passed through
    def displaySolidUnit(self, p):
        self.bb.screen.lcd.rect(p[0],p[1],4,4,1)
        self.bb.screen.lcd.rect(p[0]+1,p[1]+1,2,2,1)
