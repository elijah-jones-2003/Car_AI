import math, random, numpy, pygame, sys

# initialisation and variables

pygame.init()
game_clock = pygame.time.Clock()
main_clock = pygame.time.Clock()
timer, end = 0, 10
fps = 60
click = False
running = True

# display
display_size = (1200, 800)
pygame.display.set_caption("AI Learns to Drive")
display = pygame.display.set_mode(display_size)
background = (50, 50, 50)
button_colour = (100, 100, 100)
font1 = pygame.font.Font('freesansbold.ttf', 14)
font2 = pygame.font.Font('freesansbold.ttf', 20)
track_number = -1
track = pygame.image.load("images/mario.png").convert()

# Game variables
dead = []
alive = []
current_generation = 1
pop_size = 10
car_position = [0, 0]
car_size = [0, 0]
car_angle = 0

# Movement Constants
accel_val = 0.08
angle_change = 8  # 6 - 12
friction = 0.98
braking = 0.92
max_speed = 5

# Collision Constants
sight_range = 300
wall_colour = (34, 177, 76)

# Brain Constants
activation_threshold = 0.55


# Classes


class Car(pygame.sprite.Sprite):
    def __init__(self, size = [20, 40], pos = [400, 125], angle = 90):
        super(Car, self).__init__()
        # create car
        if track_number == 1:  # using track_number decide size position and angle of car
            self.size = [20, 40]
            self.position = [400, 125]
            self.angle = 90
        if track_number == 2:
            self.size = [20, 40]
            self.position = [300, 250]
            self.angle = 90
        if track_number == 3:
            self.size = [30, 60]
            self.position = [540, 120]
            self.angle = 90
        if track_number == 4:
            self.size = [20, 40]
            self.position = [180, 80]
            self.angle = 90
        if track_number == 5:
            self.size = [15, 30]
            self.position = [250, 250]
            self.angle = 120
        if track_number == 6:
            self.size = [10, 20]
            self.position = [100, 500]
            self.angle = 180
        '''   
        self.size = size
        self.position = pos
        self.angle = angle
        '''

        # create car image
        self.surf = pygame.transform.scale(pygame.image.load('images/car_image.png'), self.size).convert_alpha()
        self.rotated_surf = self.surf
        self.corners = []

        # Movement variables
        self.speed = 0
        self.x_speed, self.y_speed = 0, 0
        self.forward = False
        self.brake = False
        self.left = False
        self.right = False
        self.radars = []

        # Fitness
        self.alive = True
        self.distance = 0

    def check_collision(self):  # checks each corner if it overlaps a pixel on the track that is green
        for point in self.corners:
            if track.get_at((int(point[0]), int(point[1]))) == wall_colour:
                self.alive = False

    def draw(self, screen):  # update the car and draw to screen
        self.update_car()
        screen.blit(self.rotated_surf, 
        (self.position[0] - (self.rotated_surf.get_width() / 2), self.position[1] - (self.rotated_surf.get_height() / 2)))

    def move(self): # update all movement variables based on bools
        if self.alive:
            if self.forward:
                if self.speed >= max_speed:
                    self.speed = max_speed
                else: 
                    self.speed += accel_val
            else:
                if self.brake:
                    self.speed *= braking
                else:
                    self.speed *= friction        

            self.x_speed = self.speed * (math.sin(math.radians(self.angle)))
            self.y_speed = self.speed * (math.cos(math.radians(self.angle)))

            self.position[0] += self.x_speed
            self.position[1] += self.y_speed
        else:
            self.speed = 0

    def rotate(self): # changes angle variable and uses it to update the rotated image
        if self.left:
            self.angle += angle_change
        elif self.right:
            self.angle -= angle_change
        self.rotated_surf = pygame.transform.rotozoom(self.surf, self.angle, 1)

    def update_car(self):
        self.rotate()
        self.move()
        self.update_corners()
        self.update_radars(True)
        self.check_collision()
        self.distance += self.speed

    def update_corners(self):  # this is modified code from a solution I found by NeuralNine for finding the corners of the image
        x_length = self.size[0] / 2
        y_length = self.size[1] / 2
        top_left = [self.position[0] + math.cos(math.radians(360 - (self.angle + 30))) * x_length,
                    self.position[1] + math.sin(math.radians(360 - (self.angle + 30))) * y_length]
        top_right = [self.position[0] + math.cos(math.radians(360 - (self.angle + 150))) * x_length,
                     self.position[1] + math.sin(math.radians(360 - (self.angle + 150))) * y_length]
        bottom_left = [self.position[0] + math.cos(math.radians(360 - (self.angle + 210))) * x_length,
                       self.position[1] + math.sin(math.radians(360 - (self.angle + 210))) * y_length]
        bottom_right = [self.position[0] + math.cos(math.radians(360 - (self.angle + 330))) * x_length,
                        self.position[1] + math.sin(math.radians(360 - (self.angle + 330))) * y_length]
        self.corners = [top_left, top_right, bottom_left, bottom_right]

    def update_movement(self, inputs):  # takes inputs from network and updates movement bools based on this
        if len(inputs) == 4:
            self.forward = inputs[0]
            self.brake = inputs[1]
            self.left = inputs[2]
            self.right = inputs[3]
        else:
            raise ValueError('Invalid input to the network')

    def update_radars(self, draw):  # calculations for distance to walls for each car
        lengths = []
        draw_radar = draw
        for j in range(-90, 100, 30):
            x, y = 0, 0
            for i in range(sight_range):
                x = self.position[0] + i * math.sin(math.radians(self.angle) + math.radians(j))
                y = self.position[1] + i * math.cos(math.radians(self.angle) + math.radians(j))
                if track.get_at((int(x), int(y))) == wall_colour:
                    break
            if draw_radar:  # optionally draws radar
                pygame.draw.line(display, (0, 255, 0), self.position, (x, y))
                pygame.draw.circle(display, (0, 255, 0), (x, y), 2)
            length = int(math.sqrt(math.pow(x - self.position[0], 2) + math.pow(y - self.position[1], 2)))
            lengths.append(length)
        lengths.reverse()
        self.radars = lengths


class Brain:
    def __init__(self, shape = [7, 8, 8, 4]):  # create the brain
        i_layer = Input(shape[0])
        h_layer1 = Hidden(shape[1], shape[0])
        h_layer2 = Hidden(shape[2], shape[1])
        o_layer = Output(shape[3], shape[2])
        self.network = [i_layer, h_layer1, h_layer2, o_layer]
        self.outputs = [False, False, False, False]

    def run_network(self, inputs):  # run inputs through the brain
        self.network[0].forward(inputs)
        self.network[1].forward(self.network[0].outputs)
        self.network[2].forward(self.network[1].outputs)
        self.network[3].forward(self.network[2].outputs)
        self.outputs = self.network[3].outputs

    def inheritance(self, best):  # new gen inherits characteristics from previous gen
        for layer in range(len(self.network)):
            for x in range(len(self.network[layer].weights)):
                for y in range(len(self.network[layer].weights[x])):
                    i = random.randint(0, 2)
                    self.network[layer].weights[x][y] = best[i][1].network[layer].weights[x][y]
        for layer in range(len(self.network)):
            for x in range(len(self.network[layer].biases)):
                i = random.randint(0, 2)
                self.network[layer].biases[x] = best[i][1].network[layer].biases[x]

    def mutate(self):  # random 0.1% to mutate any weight or bias in the new networks
        for layer in self.network:
            for x in range(len(layer.weights)):
                for y in range(len(layer.weights[x])):
                    i = random.randint(1, 200)
                    if i == 69:
                        layer.weights[x][y] = numpy.random.randn(1)
            for x in range(len(layer.biases)):
                i = random.randint(1, 200)
                if i == 69:
                    layer.biases[x] = numpy.random.randn(1)

    def save_brain(self):
        brain_list = []
        with open('brain_file.txt', 'w') as file:
            for layer in self.network:
                for node in layer.weights:
                    print(node, file=file)       

class Layer:
    def __init__(self, n_neurons, n_inputs):
        self.outputs = []
        self.weights = numpy.random.randn(n_inputs, n_neurons)
        self.biases = numpy.random.randn(n_neurons)

    def forward(self, inputs):
        self.outputs = numpy.dot(inputs, self.weights) + self.biases

class Input(Layer):
    def __init__(self, n_neurons):  # inherits __init__ from Layer and adds n_neurons
        n_inputs = 0
        super().__init__(n_neurons, n_inputs)
        self.neurons = n_neurons

    def forward(self, inputs):  # overrides forward from layer
        self.outputs = inputs

class Hidden(Layer):  # no __init__ as it inherits from Layer
    def forward(self, inputs):  # inherits and adds activation function
        super().forward(inputs)
        self.outputs = relu(self.outputs)

class Output(Layer):  # no __init__ as it inherits from Layer
    def forward(self, inputs):  # inherits and adds activation functions
        super().forward(inputs)
        outputs = softmax(self.outputs)
        self.outputs = binary(outputs)


# Activation Functions


def relu(inputs):  # ReLU function, any negative values become 0
    output = []
    for i in inputs:
        if i > 0:
            output.append(i)
        else:
            output.append(i * 0.10)
    return output

def softmax(inputs):  # creates a separate probability for 1, 2 and 3, 4 neuron to fire
    # 1 is forward, 2 is brake, 3 is left, 4 is right
    max1 = inputs[0] + (inputs[1])
    max2 = inputs[2] + inputs[3]
    output = [(inputs[0] / max1), (inputs[1] / max1), (inputs[2] / max2), (inputs[3] / max2)]
    return output

def binary(inputs):  # probability must meet certain threshold to fire
    output = []
    for i in inputs:
        if i > activation_threshold:
            output.append(True)  # return booleans to make things easier later
        else:
            output.append(False)
    return output


# Game Procedures and Functions

def draw_population(pop):
    for i in pop:
        i[0].draw(display)

def exchange_data(pop):
    for i in pop:
        try:
            i[1].run_network(i[0].radars)
        except:
            pass
        i[0].update_movement(i[1].outputs)  # and the return value is used to update the movement booleans

def kill(pop):  # checks every member of the population and swaps them to dead when .alive = False
    for i in pop:
        if not i[0].alive:
            dead.append(i)
            alive.remove(i)

def create_generation(size):
    new_pop = []
    for i in range(size):
        new_pop.append([Car(), Brain()])
    return new_pop

def next_generation(size, best):
    new_pop = create_generation(size - 3)
    for i in new_pop:
        i[1].inheritance(best)  # takes best 3 to create network for new gen
    for i in new_pop:
        i[1].mutate()
    for i in best:  # keep the best from previous gen to help prevent backwards progress
        new_pop.append([Car(), i[1]])
    return new_pop

def get_avg_fitness(pop):
    if pop:
        tot = 0
        for c in pop:
            tot += c[0].distance
        avg = tot / len(pop)
    else:
        avg = 0
    return avg

def get_top_fitness(pop):
    best = []
    length = len(pop)
    if length > 3:
        for i in range(3):
            temp = 0
            for c in range(len(pop)):
                if pop[c][0].distance > pop[temp][0].distance:
                    temp = c
            best.append(pop[temp])
            pop.pop(temp)
    else:
        return pop
    return best

def write_to_screen(text, colour, font, surface, position, back):  # adding text to the game screen
    text_ = font.render(text, True, colour, back)
    text_rect = text_.get_rect()
    text_rect.topleft = position
    surface.blit(text_,  text_rect)

# Display Functions


def main_menu():
    click = False
    while True:  # indefinite loop
        # create the visuals
        display.fill(background)
        write_to_screen("main menu", (200, 200, 200), font2, display, (20, 20), background)
        button_track_list = pygame.Rect(25, 45, 95, 25)
        pygame.draw.rect(display, button_colour, button_track_list)
        write_to_screen("Track Select", (200, 200, 200), font1, display, (30, 50), button_colour)
        button_quit = pygame.Rect(25, 80, 95, 25)
        pygame.draw.rect(display, button_colour, button_quit)
        write_to_screen("Quit", (200, 200, 200), font1, display, (55, 85), button_colour)

        # check if button clicked
        mx, my = pygame.mouse.get_pos()
        if click:
            if button_track_list.collidepoint((mx, my)):
                track_num = track_select()
                break
            if button_quit.collidepoint((mx, my)):
                sys.exit()
        click = False

        # check events for a click or button press
        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    click = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit()
        pygame.display.update()
        main_clock.tick(60)
    return track_num


def track_select():
    click = False
    while True:
        # create the visuals
        display.fill(background)
        write_to_screen("Track Select", (200, 200, 200), font2, display, (20, 20), background)
        button_paradis = pygame.Rect(25, 45, 115, 25)
        pygame.draw.rect(display, button_colour, button_paradis)
        write_to_screen("Paradis", (200, 200, 200), font1, display, (57, 50), button_colour)
        button_star = pygame.Rect(25, 80, 115, 25)
        pygame.draw.rect(display, button_colour, button_star)
        write_to_screen("Star Circuit", (200, 200, 200), font1, display, (45, 85), button_colour)
        button_nascar = pygame.Rect(25, 115, 115, 25)
        pygame.draw.rect(display, button_colour, button_nascar)
        write_to_screen("Nascar", (200, 200, 200), font1, display, (58, 120), button_colour)
        button_monza = pygame.Rect(25, 150, 115, 25)
        pygame.draw.rect(display, button_colour, button_monza)
        write_to_screen("Monza", (200, 200, 200), font1, display, (58, 155), button_colour)
        button_silver = pygame.Rect(25, 185, 115, 25)
        pygame.draw.rect(display, button_colour, button_silver)
        write_to_screen("SilverStone", (200, 200, 200), font1, display, (43, 190), button_colour)
        button_monaco = pygame.Rect(25, 220, 115, 25)
        pygame.draw.rect(display, button_colour, button_monaco)
        write_to_screen("Monaco", (200, 200, 200), font1, display, (55, 225), button_colour)
        button_back = pygame.Rect(25, 290, 115, 25)
        pygame.draw.rect(display, button_colour, button_back)
        write_to_screen("Back", (200, 200, 200), font1, display, (65, 295), button_colour)

        # check for buttons clicked
        mx, my = pygame.mouse.get_pos()
        if click:
            if button_paradis.collidepoint((mx, my)):           
                track_n = 1
                break
            elif button_star.collidepoint((mx, my)):
                track_n = 2
                break
            elif button_nascar.collidepoint((mx, my)):            
                track_n = 3
                break
            elif button_monza.collidepoint((mx, my)):   
                track_n = 4
                break
            elif button_silver.collidepoint((mx, my)):      
                track_n = 5
                break
            elif button_monaco.collidepoint((mx, my)):
                track_n = 6
                break
            elif button_back.collidepoint((mx, my)):      
                track_n = main_menu()
                break
        click = False

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if e.button == 1:
                    click = True
            if e.type == pygame.KEYDOWN:
                if e.key == pygame.K_ESCAPE:
                    sys.exit()
        pygame.display.update()
        main_clock.tick(60)
    return track_n


# Main code


while track_number == -1:  # loop until a track has been selected
    track_number = main_menu()
    if track_number == -1:
        print("Game didn't load successfully")
    elif track_number == 1:
        print("Paradis selected")
        track = pygame.image.load("images/Paradis.png").convert()     
    elif track_number == 2:
        print("Star selected")
        track = pygame.image.load("images/Star_Circuit.png").convert()
    elif track_number == 3:
        print("Nascar selected")
        track = pygame.image.load("images/Nascar.png").convert()
    elif track_number == 4:
        print("Monza selected")
        track = pygame.image.load("images/f1/Monza.png").convert()
    elif track_number == 5:
        print("Silverstone selected")
        track = pygame.image.load("images/f1/Silverstone.png").convert()
    elif track_number == 6:
        print("Monaco selected")
        track = pygame.image.load("images/f1/Monaco.png").convert()
track = pygame.transform.scale(track, display_size)

alive = create_generation(pop_size)
while running:
    # display game values to screen
    display.blit(track, (0, 0))
    write_to_screen("current generation: " + str(current_generation),
                    (200, 200, 200), font1, display, (50, 30), wall_colour)
    write_to_screen("timer: " + str(end - int(timer / fps)),
                    (200, 200, 200), font1, display, (50, 50), wall_colour)
    write_to_screen("alive: " + str(len(alive)), (200, 200, 200),
                    font1, display, (50, 70), wall_colour)
    button_kill = pygame.Rect(900, 20, 33, 25)
    pygame.draw.rect(display, button_colour, button_kill)
    write_to_screen("Kill", (200, 200, 200), font1, display, (905, 25), button_colour)

    # get mouse position and check for click on kill button
    mx, my = pygame.mouse.get_pos()
    if button_kill.collidepoint((mx, my)):
        if click:
            for z in alive:
                z[0].alive = False
                timer = 0

    # check for keys being pressed and click
    click = False
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            if event.key == pygame.K_k:
                for m in alive:
                    m[0].alive = False
        if event.type == pygame.MOUSEBUTTONDOWN:
            if event.button == 1:
                click = True

    if not alive:  # next gen if alive is empty
        current_generation += 1
        average = get_avg_fitness(dead)
        top = get_top_fitness(dead)
        alive = next_generation(pop_size, top)
        dead = []
        print("avg fitness: ", average, "gen: ", current_generation - 1)
        timer = 0

    else:  # run the game functions while alive isn't empty
        exchange_data(alive)
        draw_population(alive)
        kill(alive)
        timer += fps / 60
        if timer == end * fps:
            for z in alive:
                z[0].alive = False
                timer = 0
    pygame.display.flip()
    game_clock.tick(fps)
