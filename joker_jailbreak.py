import pygame, random, os, itertools

pygame.init()
main_dir = os.path.split(os.path.abspath(__file__))[0]
data_dir = os.path.join(main_dir, "graphics")
cardw, cardh = (80, 120)

NUMBERS = {1: 'ace', 2 : '2', 3: '3', 4: '4', 5: '5', 6:'6', 7:'7',8:'8',9:'9',10:'10',11:'jack', 12:'queen', 13:'king'}
SUITS = ['hearts', 'spades', 'diamonds', 'clubs']
POSITION = {(0,0): 'corner', (0,1): 'side', (0,2):'corner', (1,0): 'side', (1,1):'center', (1,2):'side', (2,0):'corner', (2,1):'side', (2,2):'corner'}

def load_image(name):
    fullname = os.path.join(data_dir, name)
    try:
        image = pygame.image.load(fullname)
        image = pygame.transform.scale(image, (cardw, cardh))
        if image.get_alpha() is None:
            image = image.convert()
        else:
            image = image.convert_alpha()
    except FileNotFoundError:
        print(f"Cannnot load image: {fullname}")
        raise SystemExit
    return image, image.get_rect()

class Card(pygame.sprite.Sprite):
    def __init__(self, number, suit):
        pygame.sprite.Sprite.__init__(self)
        self.upimage, self.rect = load_image(NUMBERS[number] + "_of_" + suit + '.png')
        self.number = number
        self.suit = suit
        self.color = 'red' if suit in ['hearts', 'diamonds'] else 'black'
        self.location = 'stock'
        self.hide(False)
        self.position = None
        self.selected = False
        
    def hide(self, val):
        self.hidden = val
        self.image = cardback if val else self.upimage
    
    def update(self):
        return None

class Joker(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image, self.rect = load_image('red_joker.png')
        self.rotate = 0
        self.direction = None

    def run_away(self):
        # victory animation
        center = self.rect.center
        if self.rotate == 0:
            self.rotate = 5
        elif self.rotate == 5:
            self.rotate = -10
        else:
            self.rotate = - self.rotate
        
        self.image = pygame.transform.rotate(self.image, self.rotate)
        self.rect = self.image.get_rect(center = center)
        # self.rect.center = center

        d = self.direction
        steps = 30
        if d == 'N':
            self.rect.centery -= steps
        elif d == 'W':
            self.rect.centerx -=steps
        elif d == 'S':
            self.rect.centery += steps
        elif d == 'E':
            self.rect.centerx += steps

class Game():
    def __init__(self):
        # Set up rects and sprite groups
        self.tableau = [[[], [], []] for _ in range(3)]
        self.tableau_groups = [[pygame.sprite.Group()]*3 for _ in range(3)]
        self.area = pygame.display.get_surface().get_rect()
        self.selected = []

        self.stock = [Card(*val) for val in itertools.product(NUMBERS.keys(), SUITS)]
        random.shuffle(self.stock)
        self.joker = Joker()

        corners = [(0,0), (0,2), (2,0), (2,2)]
        corner_cards = 3
        sides = [(0,1), (1,0), (1,2), (2,1)]
        side_cards = 7
        for i,j in itertools.product(range(3), range(3)):
            if (i,j) in corners:
                for k in range(corner_cards):
                    card = self.stock.pop()
                    self.add(card, i, j)
                    card.hide(k != corner_cards - 1)
            elif (i, j) in sides:
                for k in range(side_cards):
                    card = self.stock.pop()
                    self.add(card, i, j)
                    card.hide(k != side_cards - 1)
            elif (i,j) == (1,1):
                self.add(self.joker, i, j)

    def add(self, card, i, j):
        #  Add card to tableau and adjust card.rect accordingly
        k = len(self.tableau[i][j])
        self.tableau[i][j].append(card)
        self.tableau_groups[i][j].add(card)
        card.position = (i,j)
        card.rect.center = self.area.center
        hp, cp = 10, 18
        if (i,j) == (0,0):
            # top left corner
            card.rect.left -= cardw + hp + cp*k
            card.rect.top -= cardh + hp + cp*k
        elif (i,j) == (0,1):
            # north side
            card.rect.top -= cardh + hp + cp*k
        elif (i,j) == (0,2):
            # top right corner
            card.rect.left += cardw + hp + cp*k
            card.rect.top -= cardh + hp + cp*k
        elif (i,j) == (1,0):
            # west side
            card.rect.left -= cardw + hp + cp*k
        elif (i,j) == (1,2):
            # east side
            card.rect.left += cardw + hp + cp*k
        elif (i,j) == (2,0):
            # bottom left corner
            card.rect.left -= cardw + hp + cp*k
            card.rect.top += cardh + hp + cp*k
        elif (i,j) == (2,1):
            # south side
            card.rect.top += cardh + hp + cp*k
        elif (i,j) == (2,2):
            # bottom right corner
            card.rect.left += cardw + hp + cp*k
            card.rect.top += cardh + hp + cp*k
    
    def remove(self, card):
        card.selected = False
        (i,j) = card.position
        n = len(self.tableau[i][j])
        self.tableau_groups[i][j].remove(self.tableau[i][j].pop())
        if n > 1:
            card = self.tableau[i][j][-1]
            if card != self.joker:
                card.hide(False)
    
    def draw(self):
        midcard = self.tableau[1][1][-1]
        if midcard != self.joker and midcard.selected:
            self.selected.remove(midcard)
            midcard.selected = False

        if len(self.stock) > 0:
            self.add(self.stock.pop(), 1, 1)
    
    def select(self, mousepos):
        for i,j in itertools.product(range(3), range(3)):
            if len(self.tableau[i][j]) > 0:
                card = self.tableau[i][j][-1]
                if card.rect.collidepoint(mousepos) and card != self.joker:
                    if card.selected:
                        self.selected.remove(card)
                        card.selected = False
                    else:
                        self.selected.append(card)
                        card.selected = True
                    return card 
                
    def reset(self):
        self.__init__()

    def play(self):
        redvalue = 0
        blackvalue = 0
        for card in self.selected:
            if card.color == 'red':
                redvalue += card.number
            elif card.color == 'black':
                blackvalue += card.number

        if redvalue == blackvalue:
            for card in self.selected:
                self.remove(card)
        
        for card in self.selected:
            card.selected = False

        self.selected = []
        return redvalue == blackvalue

    def win(self):
        if len(self.tableau[1][1]) > 1:
            return None
        if self.tableau[0][1] == []:
            return 'N'
        if self.tableau[1][0] == []:
            return 'W'
        if self.tableau[1][2] == []:
            return 'E'
        if self.tableau[2][1] == []:
            return 'S'
        return None

    def hint(self):
        red_cards = []
        red_vals = {}
        black_cards = []
        black_vals = {}
        for i,j in itertools.product(range(3), range(3)):
            if len(self.tableau[i][j]) > 0:
                card = self.tableau[i][j][-1]
                if card != self.joker:
                    if card.color == 'red':
                        red_cards.append(card)
                    else:
                        black_cards.append(card)
        nr = len(red_cards)
        nb = len(black_cards)
        for r in range(1, nr+1):
            for key in itertools.combinations(red_cards, r):
                sum = 0
                for card in key:
                    sum += card.number
                red_vals[key] = sum
        for b in range(1, nb+1):
            for key in itertools.combinations(black_cards, b):
                sum = 0
                for card in key:
                    sum += card.number
                black_vals[key] = sum

        valid_moves = []
        for rkey in red_vals:
            sum = red_vals[rkey]
            for bkey in black_vals:
                if black_vals[bkey] == sum:
                    valid_moves.append(rkey + bkey)
        
        if len(valid_moves) > 0:
            return max(valid_moves, key=self.score)
        else:
            return None

    def score(self, hand):
        s = 0
        for card in hand:
            if POSITION[card.position] == 'corner':
                s -= 1
            elif POSITION[card.position] == 'side':
                s += 1
            elif POSITION[card.position] == 'center':
                s += 2
        return s
def main():
    pygame.init()
    screen = pygame.display.set_mode((960, 740))
    area = screen.get_rect()
    background = pygame.Surface(screen.get_size()).convert()
    background.fill((150, 190, 37))

    global cardback
    cardback, _ = load_image("card_back.png")

    font = pygame.font.Font(None, 32)
    stock_rect = pygame.Rect(0, 0, cardw, cardh)
    stock_rect.bottomright = (area.width/4 - 50, area.height/4)
    invalid_surf = font.render("Invalid move!", True, 'red')
    invalid_rect = invalid_surf.get_rect(center = (area.width/2, 40))
    reset_surf = font.render("Restart", True, 'black')
    reset_rect = reset_surf.get_rect(bottomright = (area.width - 10, area.height - 10))
    victory_surf = font.render("You win!", True, 'red')
    victory_rect = victory_surf.get_rect(center = (area.width/2, 60))
    hint_surf = font.render("Hint", True, 'black')
    hint_rect = hint_surf.get_rect(bottomleft = (10, area.height - 10))
    background.blit(hint_surf, hint_rect)
    background.blit(reset_surf, reset_rect)

    def blit_game():
        screen.blit(background, (0,0))
        for i,j in itertools.product(range(3), range(3)):
            game.tableau_groups[i][j].draw(screen)
        if len(game.stock) > 0:
            screen.blit(cardback, stock_rect)
    game = Game()
    blit_game()

    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == 53:
                game.joker.run_away()
                blit_game()
            if event.type == pygame.MOUSEBUTTONDOWN:
                if stock_rect.collidepoint(event.pos):
                    game.draw()
                    game.tableau_groups[1][1].draw(screen)
                    if len(game.stock) > 0:
                        screen.blit(cardback, stock_rect)
                    else:
                        screen.blit(background, stock_rect, stock_rect)
                elif reset_rect.collidepoint(event.pos):
                    background.fill((150, 190, 37))
                    background.blit(reset_surf, reset_rect)
                    background.blit(hint_surf, hint_rect)
                    game.reset()
                    blit_game()
                else:
                    card = game.select(event.pos)
                    if card != None and card.selected:
                        pygame.draw.rect(screen, 'yellow', card.rect, width=3)
                    elif card != None:
                        screen.blit(card.image, card.rect)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_RETURN:
                valid = game.play()
                blit_game()
                if not valid:
                    screen.blit(invalid_surf, invalid_rect)
                if game.win() and game.joker.rect.center == area.center:
                    background.blit(victory_surf, victory_rect)
                    game.joker.direction = game.win()
                    pygame.time.set_timer(53, millis=100, loops=20)
            if event.type == pygame.KEYDOWN and event.key == pygame.K_h or event.type == pygame.MOUSEBUTTONDOWN and hint_rect.collidepoint(event.pos):
                hint = game.hint()
                if hint == None:
                    pygame.draw.rect(screen, 'red', stock_rect, width=3)
                else:
                    for card in hint:
                        pygame.draw.rect(screen, 'red', card.rect, width=3)
        pygame.display.flip()
        clock.tick(60)

if __name__ == "__main__":
    main()