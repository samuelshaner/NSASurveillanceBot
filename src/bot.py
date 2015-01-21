import argparse
import socket
import sys
from player import *
from hand import *
from tables import *
import random
import numpy as np
from card import Card
from deck import Deck 
from evaluator import Evaluator
from copy import deepcopy
from sklearn.linear_model import LinearRegression

"""
Simple example pokerbot, written in python.

This is an example of a bare bones pokerbot. It only sets up the socket
necessary to connect with the engine and then always returns the same action.
It is meant as an example of how a pokerbot should communicate with the engine.
"""
class Bot(object):

  def __init__(self):

    self._time_bank  = None
    self._stack_size = None
    self._players = {}
    self._big_blind  = None
    self._num_hands = None
    self._hands = []
    self._me = None
    self._k_nearest_matrices = {}
    self._k_nearest_values = {}
    self._k_nearest_points = 3
    self._aggregate_hand_strength = {}
    self.regression_model = {}
    
  def run(self, input_socket):

    # Get a file-object for reading packets from the socket.
    # Using this ensures that you get exactly one packet per read.
    f_in = input_socket.makefile()
    
    while True:
      
      # Block until the engine sends us a packet.
      data = f_in.readline().strip()
      
      # If data is None, connection has closed.
      if not data:

        for player in self._players.itervalues():
          print player

        for hand in self._hands:
          print hand

        print "Gameover, engine disconnected."
        break
        
      # Here is where you should implement code to parse the packets from
      # the engine and act on it. We are just printing it instead.
      print data
      
      # When appropriate, reply to the engine with a legal action.
      # The engine will ignore all spurious responses.
      # The engine will also check/fold for you if you return an
      # illegal action.
      # When sending responses, terminate each response with a newline
      # character (\n) or your bot will hang!
      words = data.split()
      
      if words[0] == "GETACTION":

        # get the current hand
        hand = self._hands[-1]

        # Pot size
        pot_size = int(words[1])

        # Update board for this hand
        num_board_cards = int(words[2])
        hand.setBoard(words[3:3+num_board_cards])
        
        # Update the stack size for each player
        self.setStackSizeBySeat(1, int(words[3+num_board_cards]))
        self.setStackSizeBySeat(2, int(words[4+num_board_cards]))
        self.setStackSizeBySeat(3, int(words[5+num_board_cards]))
        
        # Update the active players
        hand.setNumActive(int(words[6+num_board_cards]))
        self.setIsActiveBySeat(1, words[7+num_board_cards])
        self.setIsActiveBySeat(2, words[8+num_board_cards])
        self.setIsActiveBySeat(3, words[9+num_board_cards])

        # Update actions for this hand
        num_actions = int(words[10+num_board_cards])
        hand.addPerformedActions(words[11+num_board_cards:11+num_board_cards+num_actions], self._players)

        # get the current state
        state = hand._state

        # add features for cards on table
        #if state is not 'PREFLOP':
          #(straight,straight_draw) = self.getStraight(words[3:3+num_board_cards])
          #(flush,flush_draw) = self.getFlush(words[3:3+num_board_cards])
          #pair = self.getPairs(words[3:3+num_board_cards])
          #(aces,kings,queens) = self.getCards(words[3:3+num_board_cards], ['A','K','Q'])
          
          #for name,player in self._players.iteritems():
            #if not player._is_me:
              #hand.addFeature(name, state, 'STRAIGHTDRAW', straight_draw)
              #hand.addFeature(name, state, 'STRAIGHT', straight)
              #hand.addFeature(name, state, 'FLUSHDRAW', flush_draw)
              #hand.addFeature(name, state, 'FLUSH', flush)
              #hand.addFeature(name, state, 'PAIRS', pair)
              #hand.addFeature(name, state, 'ACES', aces)
              #hand.addFeature(name, state, 'KINGS', kings)
              #hand.addFeature(name, state, 'QUEENS', queens)
              

        # Predict player hand strengths 
        opponent_hand_strengths = []
        for name,player in self._players.iteritems():
          if not player._is_me and player._is_active:
            
            if name in hand._player_LB:
              LB = hand._player_LB[name]
              UB = hand._player_UB[name]
            else:
              LB = 0.0
              UB = 1.0
            
            num_trials = len(self._aggregate_hand_strength[name, state]['UB'])
            if num_trials >= 50 and num_trials%25 == 0:

              #FIXME: Right now just using upper bound - should use upper and lower
              X = self._aggregate_hand_strength[name, state]['UB']
              Y = self._aggregate_hand_strength[name, state]['actual']
             
              self.regression_model[name, state].fit(X,Y)

            if num_trials > 50:
              hand_strength = self.regression_model[name, state].predict(UB)
              hand._hand_strength_predict[name, state] = hand_strength
            
            else:
              hand_strength = 0.5 * (LB + UB)

            opponent_hand_strengths.append(hand_strength)

         
        # Compute hand equity
        hand = self._hands[-1]
        board = hand._board
        state = hand._state
        for name,player in self._players.iteritems():
          if player._is_me:
            hand_strength = self.computeHandStrength(hand._cards[name], board)
            hand._hand_strength_actual[name, state] = hand_strength

        hand_strength = hand_strength / (hand_strength + sum(opponent_hand_strengths))

        # Make decision based on equity
        num_legal_actions = int(words[11+num_board_cards+num_actions])
        legal_actions = [a.split(':') for a in words[12+num_board_cards+num_actions:12+num_board_cards+num_actions+num_legal_actions]]
        action = self.getAction(hand_strength, pot_size, legal_actions, state)
        s.send(action)


      elif words[0] == "REQUESTKEYVALUES":
        # At the end, the engine will allow your bot save key/value pairs.
        # Send FINISH to indicate you're done.
        s.send("FINISH\n")
        
        
      elif words[0] == "NEWGAME":
        
        # Create the players for this game
        self._me = Player(words[1], int(words[4]), me=True)
        self._players[words[1]] = self._me
        self._players[words[2]] = Player(words[2], int(words[4]))
        self._players[words[3]] = Player(words[3], int(words[4]))

        # Create k nearest matrices and value dicts for each player and state combo
        for name,player in self._players.iteritems():
          if not player._is_me:
            rounds = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
            for rd in rounds:
              self._k_nearest_matrices[name,rd] = None
              self._k_nearest_values[name,rd] = np.array([])
              
              #FIXME: change to ridge regression???
              self.regression_model[name,rd] = \
                  LinearRegression(fit_intercept=True, normalize=False, \
                  copy_X=True)

              self._aggregate_hand_strength[name,rd] = {}
              comps = ['LB','UB','actual']
              for comp in comps:
                self._aggregate_hand_strength[name,rd][comp] = []

       # Set the game parameters
        self._big_blind  = int(words[5])
        self._num_hands  = int(words[6])
        self._time_bank  = float(words[7])
        
          
      elif words[0] == "NEWHAND":

        # Update the k nearest matrices and values from previous hand
        if len(self._hands) > 0:
          hand = self._hands[-1]
          if hand._state == 'RIVER':
            board = hand._board
            for name,cards in hand._cards.iteritems():
              if not self._players[name]._is_me:
               
                rounds = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
                num_cards_shown = {'PREFLOP':0, 'FLOP':3, 'TURN':4, 'RIVER':5}
                for rd in rounds:
                  
                  # calculate hand strength
                  shown = num_cards_shown[rd]
                  hs = self.computeHandStrength(cards, board[:shown])

                  # save hand strength
                  hand._hand_strength[name, rd]['actual'].append(hs)
                  comps = ['LB','UB','actual']
                  for comp in comps:
                    self._aggregate_hand_strength[name, rd][comp] += \
                        hand._hand_strength[name, rd][comp]

        
        # Create a new hand and add to Bot's list of hands
        hand = Hand(words, self._players)
        self._hands.append(hand)
        self._players[words[8]].setSeat(1)
        self._players[words[9]].setSeat(2)
        self._players[words[10]].setSeat(3)
        self._players[words[8]].setIsActive(words[12])
        self._players[words[9]].setIsActive(words[13])
        self._players[words[10]].setIsActive(words[14])

        # Set seat features for each player
        if not self._players[words[8]]._is_me:
          hand.addFeature(words[8], 'PREFLOP', 'SEAT0')
        if not self._players[words[9]]._is_me:
          hand.addFeature(words[9], 'PREFLOP', 'SEAT1')
        if not self._players[words[10]]._is_me:
          hand.addFeature(words[10], 'PREFLOP', 'SEAT2')

        # Set my player's cards in this hand and remove from opponents weight tables
        self._hands[-1].setCards(self._me.getName(), words[3:5])
        
        # Update my time bank
        self._time_bank = float(words[15])

        
      elif words[0] == "HANDOVER":
        
        # get current hand
        hand = self._hands[-1]

        # Update the stack size for each player
        self.setStackSizeBySeat(1, int(words[1]))
        self.setStackSizeBySeat(2, int(words[2]))
        self.setStackSizeBySeat(3, int(words[3]))
        
        # Set the board cards for this hand
        num_board_cards = int(words[4])
        hand.setBoard(words[5:5+num_board_cards])

        # Update actions for this hand
        num_actions = int(words[5+num_board_cards])
        hand.addPerformedActions(words[6+num_board_cards:6+num_board_cards+num_actions], self._players)
        
        # Update my time bank
        self._time_bank = float(words[-1])

                  
    # Clean up the socket.
    s.close()


  def getStraight(self, board):

    board_ids = []
    for card in board:
      card_id = card[0]
      if card_id in ['2', '3', '4', '5', '6', '7', '8', '9']:
        board_ids.append(int(card_id))
      elif card_id == 'T':
        board_ids.append(10)
      elif card_id == 'J':
        board_ids.append(11)
      elif card_id == 'Q':
        board_ids.append(12)
      elif card_id == 'K':
        board_ids.append(13)
      elif card_id == 'A':
        board_ids.append(14)

    num_cards = len(board_ids)
    id_difs = []
    for i in board_ids[1:]:
      id_difs.append(abs(board_ids[0] - i))

    draw = False
    if 1 or 2 or 3 in id_difs:
      draw = True

    straight = False
    if 1 and 3 in id_difs:
      straight = True
    elif 1 and 2 in id_difs:
      straight = True
    elif 2 and 3 in id_difs:
      straight = True

    return (straight,draw)


  def getPairs(self, board):

    board_ids = []
    for card in board:
      board_ids.append(card[0])

    if board_ids.count('2') >= 2 or board_ids.count('3') >= 2 or board_ids.count('4') >= 2 or board_ids.count('5') >= 2 or board_ids.count('6') >= 2 or board_ids.count('7') >= 2 or board_ids.count('8') >= 2 or board_ids.count('9') >= 2 or board_ids.count('T') >= 2 or board_ids.count('J') >= 2 or board_ids.count('Q') >= 2 or board_ids.count('K') >= 2 or board_ids.count('A') >= 2: 
      pair = True
    else:
      pair = False

    return pair


  def getCards(self, board, cards):

    board_ids = []
    for board_card in board:
      board_ids.append(board_card[0])

    cards_present = []
    for card in cards:
      if card in board_ids:
        cards_present.append(True)
      else:
        cards_present.append(False)
        
    return tuple(cards_present)


  def getFlush(self, board):

    suits = []
    for card in board:
      suits.append(card[1])

    draw = False
    if suits.count('s') >= 2 or suits.count('d') >= 2 or suits.count('c') >= 2 or suits.count('h') >= 2:
      draw = True

    flush = False
    if suits.count('s') >= 3 or suits.count('d') >= 3 or suits.count('c') >= 3 or suits.count('h') >= 3:
      flush = True

    return (flush,draw)


  def getAction(self, equity, pot_size, legal_actions, state):

    equity_bet = equity*pot_size

    action_dict = {}
    for legal_action in legal_actions:
      action_dict[legal_action[0]] = legal_action[1:]

    # set default action
    action = "CHECK\n"

    # get call threshold value. We have this so we are more loose early on
    if state == 'PREFLOP':
      call_thresh = 0.5
    elif state == 'FLOP':
      call_thresh = 0.7
    elif state == 'TURN':
      call_thresh = 0.9
    else:
      call_thresh = 1.1
      

    if 'CALL' in action_dict.keys():
      call_amount = action_dict['CALL'][0]
      print 'equity bet: ' + str(equity_bet) + ', call amount: ' + call_amount 
      if equity_bet < float(call_amount):
        #val = random.random()
        if equity_bet > call_thresh * float(call_amount):
          action = "CALL:" + call_amount + "\n"
        else:
          action = "FOLD\n"
      elif 'RAISE' in action_dict.keys():
        raise_max = action_dict['RAISE'][1]
        raise_min = action_dict['RAISE'][0]
        if equity_bet > float(raise_max):
          action = "RAISE:" + raise_max + "\n"
        elif equity_bet > float(raise_min):
          action = "RAISE:" + str(round(equity_bet)) + "\n"
        else:
          action = "CALL:" + call_amount + "\n"
      else:
          action = "CALL:" + call_amount + "\n"
    elif 'CHECK' in action_dict.keys() and 'BET' in action_dict.keys():
      bet_max = action_dict['BET'][1]
      bet_min = action_dict['BET'][0]
      if equity_bet > float(bet_max):
        action = "BET:" + bet_max + "\n"
      elif equity_bet >  (2.0 - call_thresh) * float(bet_min):
        action = "BET:" + str(round(equity_bet)) + "\n"
      else: 
        action = "CHECK\n"
    else:
      raise_max = action_dict['RAISE'][1]
      raise_min = action_dict['RAISE'][0]
      if equity_bet > float(raise_max):
        action = "RAISE:" + raise_max + "\n"
      elif equity_bet >  (2.0 - call_thresh) * float(raise_min):
        action = "RAISE:" + str(round(equity_bet)) + "\n"
      else: 
        action = "CHECK\n"

    return action


  def setStackSizeBySeat(self, seat, stack_size):

    for player in self._players.itervalues():
      if player._seat == seat:
        player.setStackSize(stack_size)
        break


  def setIsActiveBySeat(self, seat, is_active):

    for player in self._players.itervalues():
      if player._seat == seat:
        player.setIsActive(is_active)
        break


  def computeHandStrength(self, hand, board, iters=250):

    hand_cards = []
    for c in hand:
      hand_cards.append(Card.new(c))
  
    board_cards_init = []
    for c in board:
      board_cards_init.append(Card.new(c))

    win = 0
    lose = 0
    evaluator = Evaluator()
    deck = Deck()

    for i in xrange(iters):      

      # Create new deck and remove hand and board cards
      deck.shuffle()
      
      for card in hand_cards:
        deck.cards.remove(card)

      for card in board_cards_init:
        deck.cards.remove(card)

      # draw opponent cards
      opp_cards = deck.draw(2)
      
      # complete board
      board_cards = deepcopy(board_cards_init)
      for j in xrange(5 - len(board_cards_init)):
        board_cards.append(deck.draw(1))

      # rank hands
      rank_me = evaluator.evaluate(board_cards, hand_cards)
      rank_opp = evaluator.evaluate(board_cards, opp_cards)
      
      if rank_opp < rank_me:
        lose += 1
      else:
        win += 1

    hand_strength = float(win) / (win + lose)
    return hand_strength


  def kNearest(self, x, features, values):
    
    diff = np.matrix( (x - features)**2 ).sum(axis=1).flatten().tolist()[0]
    ordered = [b for (a,b) in sorted(zip(diff, values))]

    return np.mean(ordered[:self._k_nearest_points])

        
if __name__ == '__main__':
  parser = argparse.ArgumentParser(description='A Pokerbot.', add_help=False, prog='pokerbot')
  parser.add_argument('-h', dest='host', type=str, default='localhost', help='Host to connect to, defaults to localhost')
  parser.add_argument('port', metavar='PORT', type=int, help='Port on host to connect to')
  args = parser.parse_args()
  
  # Create a socket connection to the engine.
  print 'Connecting to %s:%d' % (args.host, args.port)
  try:
    s = socket.create_connection((args.host, args.port))
  except socket.error as e:
    print 'Error connecting! Aborting'
    exit()

  bot = Bot()
  bot.run(s)
