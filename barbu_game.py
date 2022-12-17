import numpy as np

# Deck mapping: cards are represented by an integer from 0 to 51
# 0 is Ace of Spades, 1 is 2 of Spades, ..., 12 is King of Spades
# 14 is Ace of Hearts, 15 is 2 of Hearts, ..., 25 is King of Hearts

def cardToUnicode(cardId):
    if hasattr(cardId, '__iter__'):
        return " ".join(cardToUnicode(c) for c in sorted(cardId))

    number = cardId % 13
    suit = cardId // 13

    if number == 0:
        number = 'A'
    elif number == 10:
        number = 'J'
    elif number == 11:
        number = 'Q'
    elif number == 12:
        number = 'K'

    if suit == 0:
        suit = '♠'
    elif suit == 1:
        suit = '♥'
    elif suit == 2:
        suit = '♣'
    elif suit == 3:
        suit = '♦'

    return f"{number}{suit} ({cardId})"



class BarbuGame:
    def __init__(self, rule):
        assert rule == "reds"

        deck = np.arange(52, dtype=int)
        np.random.shuffle(deck)

        # make an array of 4 sets
        self.player_cards = [set(l) for l in np.split(deck, 4)]

        self.player_points = np.zeros(4, dtype=int)

        self.round_start_player = 0

        self.round_cards = np.ones(4, dtype=int) * -1

    def set_seed(self, seed):
        np.random.seed(seed)

    def get_next_player(self):
        return (self.round_start_player + np.count_nonzero(self.round_cards != -1)) % 4

    def is_last_player_in_round(self):
        return self.get_next_player() == self.round_start_player

    def game_finished(self):
        return np.all([len(cards) == 0 for cards in self.player_cards])

    def set_player_input(self, player_id, card):
        # Check if the player has the card
        print(self.player_cards[player_id])
        print(card)
        assert card in self.player_cards[player_id], "player_not_having_card"
        # make sure the player is playing in the right order
        if player_id != self.round_start_player:
            raise Exception("player_wrong_order")
        # make sure the player is playing a card of the right suit, if they can.
        if np.any(self.round_cards != -1):
            round_suit = self.round_cards[self.round_start_player] // 13
            if not np.any((card // 13) == round_suit):
                assert np.all((self.round_cards // 13) != round_suit), "player_wrong_suit"

        self.round_cards[player_id] = card

    def evaluate_round(self):
        assert np.all(self.round_cards != -1)

        match_suit = self.round_cards[self.round_start_player] // 13

        # Find the index of the player who played the highest card of the match suit
        looser = np.argmax(self.round_cards // 13 == match_suit)

        # Calculate the points for the round
        points = self.calculate_points(self.round_cards)

        # Add the points to the looser
        self.player_points[looser] += points

        # Take the cards from the player's hands
        for player_id in range(4):
            self.player_cards[player_id].remove(self.round_cards[player_id])

        self.round_cards = np.ones(4, dtype=int) * -1
        self.round_start_player = (self.round_start_player + 1) % 4

        # return gain in points for each player
        point_diff = np.zeros(4, dtype=int)
        point_diff[looser] = points
        return point_diff


    def calculate_points(self, cards):
        # For "reds" rule, every red card is worth 1 point
        return np.sum((cards // 13) % 2 == 1)




if __name__ == "__main__":
    game = BarbuGame("reds")

    while True:
        print("===============~===*===~===============")

        for i in range(4):
            player_index = (game.round_start_player + i) % 4
            print(f"Player {player_index}: {cardToUnicode(game.player_cards[player_index])}")
            print("Choose a card to play: ", end="")
            
            card_index = int(input())

            game.set_player_input(player_index, card_index)

        game.evaluate_round()

        print(f"Player {np.argmax(game.player_points)} lost the round with {game.player_points[np.argmax(game.player_points)]} points!")