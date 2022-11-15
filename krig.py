from random import shuffle
from datetime import timedelta
from tqdm import tqdm

class Player():
    def __init__(self, id: int = 1):
        self.id = id
        self.army = []
        self.loot = []

    def attack(self):
        if len(self.army) == 0:
            self.army = self.loot
            self.loot = []
        return self.army.pop() if len(self.army) else None 
    
    def get_loot(self, cards):
        self.loot += cards

    def worth(self):
        return len(self.army) + len(self.loot)

    def has_lost(self):
        return self.worth() == 0
        
class Game():
    def __init__(self, num_players=2, verbose=False):
        deck = self.make_deck()
        self.players = [Player(id=i+1) for i in range(num_players)]
        for i, c in enumerate(deck):
            self.players[i%num_players].get_loot([c])
        self.turns = 0
        self.done = False
        self.verbose = verbose
        self.limit = 50000
        
    def make_deck(self):
        deck = list(range(2,14))*4 + [15,15]
        shuffle(deck)
        return deck

    def play(self):
        while not self.done:
            try:
                self.play_round()
            except ValueError:
                return -1
        if self.verbose:
            print("WE HAVE A WINNER: Player %d" % self.players[0].id)
            print("It only took us %d turns" % self.turns)
            print("At a rapid speed of 2 seconds per turn, that would take %s" % timedelta(seconds=2*self.turns))
        return self.turns

    def play_round(self):
        self.compete(self.players, pot=[])
        self.remove_losers()
    
    def turn_cards(self, players):
        self.turns += 1 
        if self.turns % 100 == 0:
            if self.verbose: self.print_score()
            if self.turns > self.limit:
                raise ValueError
        
        fighters = []
        for p in players:
            f = p.attack()
            if f is not None: fighters.append(f)
        return fighters

    def compete(self, players, pot=[]):
        if self.done: return
        fighters = self.turn_cards(players)
        pot += fighters
        best = [index for index, item in enumerate(fighters) if item == max(fighters)]
        
        if len(best) == 1:
            # One winner, no war
            players[best[0]].get_loot(pot)
        else:
            warriors = [players[i] for i in best]
            self.war(warriors, pot)

    def war(self, players, pot):
        pot += self.turn_cards(players)
        pot += self.turn_cards(players)
        self.compete(players, pot)

    def remove_losers(self):
        self.players = list(filter(lambda p: not p.has_lost(), self.players))
        if len(self.players) == 1:
            self.done = True

    def print_score(self):
        score = "Turn %8d" % (self.turns)
        for p in self.players:
            score += " - P%d: %d cards" % (p.id, p.worth())
        print(score, end="\r", flush=True)        
        

        
if __name__ == "__main__":
    # Play 20,000 games of war.
    turns = [Game().play() for _ in tqdm(range(20000))]
    finished = list(filter(lambda i: i > 0, turns))
    stalemate = list(filter(lambda i: i < 0, turns))
    
    print("%.f%% of all games ended with an infinite loop" % (len(stalemate) / len(finished) * 100))

    print("\nOf the ones that finished within 50000 turns, if we assume a fast turn-rate of 2 seconds")
    print("max time:", timedelta(seconds=max(finished)))
    print("avg time:", timedelta(seconds=sum(finished) / len(finished) * 2))
    