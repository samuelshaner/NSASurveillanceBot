import argparse
import socket
import sys
from player import *
from hand import *
from tables import *
import random
import numpy as np
import card
import deck 
import evaluator
import copy


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

        #for hand in self._hands:
        #  print hand

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

        # Pot size
        pot_size = int(words[1])

        # Update board for this hand
        num_board_cards = int(words[2])
        self._hands[-1].setBoard(words[3:3+num_board_cards])
        
        # Update the stack size for each player
        self.setStackSizeBySeat(1, int(words[3+num_board_cards]))
        self.setStackSizeBySeat(2, int(words[4+num_board_cards]))
        self.setStackSizeBySeat(3, int(words[5+num_board_cards]))
        
        # Update the active players
        self._hands[-1].setNumActive(int(words[6+num_board_cards]))
        self.setIsActiveBySeat(1, words[7+num_board_cards])
        self.setIsActiveBySeat(2, words[8+num_board_cards])
        self.setIsActiveBySeat(3, words[9+num_board_cards])

        # Update actions for this hand
        num_actions = int(words[10+num_board_cards])
        self._hands[-1].addPerformedActions(words[11+num_board_cards:11+num_board_cards+num_actions], self._players)

        if self._hands[-1]._state is not 'PREFLOP':
          straight_draw = self.getStraightDraw(words[3:3+num_board_cards])
          straight = self.getStraight(words[3:3+num_board_cards])
          flush = self.getFlush(words[3:3+num_board_cards])
          flush_draw = self.getFlushDraw(words[3:3+num_board_cards])
          pair = self.getPairs(words[3:3+num_board_cards])
          aces = self.getCard(words[3:3+num_board_cards], 'A')
          kings = self.getCard(words[3:3+num_board_cards], 'K')
          queens = self.getCard(words[3:3+num_board_cards], 'Q')
          
          for player in self._players.itervalues():
            if not player._is_me:
              if straight_draw:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'STRAIGHTDRAW', straight_draw)
              if straight:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'STRAIGHT', straight)
              if flush_draw:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'FLUSHDRAW', flush_draw)
              if flush:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'FLUSH', flush)
              if pair:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'PAIRS', pair)
              if aces:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'ACES', aces)
              if kings:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'KINGS', kings)
              if queens:
                self._hands[-1].addFeature(player._name, self._hands[-1]._state, 'QUEENS', queens)
                

        hand = self._hands[-1]
        state = hand._state
        equities = []
        for name,player in self._players.iteritems():
          if not player._is_me:
            if np.shape(self._k_nearest_values[name, state])[0] > 10:
              hs = self.kNearest(hand._features[name, state], self._k_nearest_matrices[name, state], self._k_nearest_values[name, state], 5)
              hand._hand_strength_predict[name, state] = hs
              equities.append(hs)
         
        # Compute hand equity
        hand = self._hands[-1]
        board = hand._board
        state = hand._state
        for name,player in self._players.iteritems():
          if player._is_me:
            hs = self.computeEquity(hand._cards[name], board, 100)
            hand._hand_strength_actual[name, state] = hs

        #print 'equity = ' + str(hs)
        if len(equities) > 0:
          hs = hs / (hs + sum(equities))
          #print 'equity mod = ' + str(hs)


        # Make decision based on equity
        num_legal_actions = int(words[11+num_board_cards+num_actions])
        legal_actions = [a.split(':') for a in words[12+num_board_cards+num_actions:12+num_board_cards+num_actions+num_legal_actions]]
        action = self.getAction(hs, pot_size, legal_actions)        
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
            self._k_nearest_matrices[name, 'PREFLOP'] = None
            self._k_nearest_matrices[name, 'FLOP'] = None
            self._k_nearest_matrices[name, 'TURN'] = None
            self._k_nearest_matrices[name, 'RIVER'] = None
            self._k_nearest_values[name, 'PREFLOP'] = np.array([])
            self._k_nearest_values[name, 'FLOP'] = np.array([])
            self._k_nearest_values[name, 'TURN'] = np.array([])
            self._k_nearest_values[name, 'RIVER'] = np.array([])

       # Set the game parameters
        self._big_blind  = int(words[5])
        self._num_hands  = int(words[6])
        self._time_bank  = float(words[7])
        
          
      elif words[0] == "NEWHAND":
        
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
          hand.addFeature(words[8], 'PREFLOP', 'SEAT', 0)
        if not self._players[words[9]]._is_me:
          hand.addFeature(words[9], 'PREFLOP', 'SEAT', 1)
        if not self._players[words[10]]._is_me:
          hand.addFeature(words[10], 'PREFLOP', 'SEAT', 2)

        # Set my player's cards in this hand and remove from opponents weight tables
        self._hands[-1].setCards(self._me.getName(), words[3:5])
        
        # Update my time bank
        self._time_bank = float(words[15])

        
      elif words[0] == "HANDOVER":
        
        # Update the stack size for each player
        self.setStackSizeBySeat(1, int(words[1]))
        self.setStackSizeBySeat(2, int(words[2]))
        self.setStackSizeBySeat(3, int(words[3]))
        
        # Set the board cards for this hand
        num_board_cards = int(words[4])
        self._hands[-1].setBoard(words[5:5+num_board_cards])

        # Update actions for this hand
        num_actions = int(words[5+num_board_cards])
        self._hands[-1].addPerformedActions(words[6+num_board_cards:6+num_board_cards+num_actions], self._players)
        
        # Update my time bank
        self._time_bank = float(words[-1])

        # Update the k nearest matrices and values
        hand = self._hands[-1]
        if hand._state == 'RIVER':
          board = hand._board
          for name,cards in hand._cards.iteritems():
            if not self._players[name]._is_me:

              hs = self.computeEquity(cards, [], 100)
              if self._k_nearest_matrices[name, 'PREFLOP'] is None:
                self._k_nearest_matrices[name, 'PREFLOP'] = np.array([np.copy(hand._features[name, 'PREFLOP'])])
              else:
                self._k_nearest_matrices[name, 'PREFLOP'] = np.append(self._k_nearest_matrices[name, 'PREFLOP'], [hand._features[name, 'PREFLOP']], 0)
              self._k_nearest_values[name, 'PREFLOP'] = np.append(self._k_nearest_values[name, 'PREFLOP'], hs)
              hand._hand_strength_actual[name, 'PREFLOP'] = hs

              hs = self.computeEquity(cards, board[:3], 100)
              if self._k_nearest_matrices[name, 'FLOP'] is None:
                self._k_nearest_matrices[name, 'FLOP'] = np.array([np.copy(hand._features[name, 'FLOP'])])
              else:
                self._k_nearest_matrices[name, 'FLOP'] = np.append(self._k_nearest_matrices[name, 'FLOP'], [hand._features[name, 'FLOP']], 0)

              self._k_nearest_values[name, 'FLOP'] = np.append(self._k_nearest_values[name, 'FLOP'], hs)
              hand._hand_strength_actual[name, 'FLOP'] = hs

              hs = self.computeEquity(cards, board[:4], 100)
              if self._k_nearest_matrices[name, 'TURN'] is None:
                self._k_nearest_matrices[name, 'TURN'] = np.array([np.copy(hand._features[name, 'TURN'])])
              else:
                self._k_nearest_matrices[name, 'TURN'] = np.append(self._k_nearest_matrices[name, 'TURN'], [hand._features[name, 'TURN']], 0)

              self._k_nearest_values[name, 'TURN'] = np.append(self._k_nearest_values[name, 'TURN'], hs)
              hand._hand_strength_actual[name, 'TURN'] = hs

              hs = self.computeEquity(cards, board, 100)
              if self._k_nearest_matrices[name, 'RIVER'] is None:
                self._k_nearest_matrices[name, 'RIVER'] = np.array([np.copy(hand._features[name, 'RIVER'])])
              else:
                self._k_nearest_matrices[name, 'RIVER'] = np.append(self._k_nearest_matrices[name, 'RIVER'], [hand._features[name, 'RIVER']], 0)

              self._k_nearest_values[name, 'RIVER'] = np.append(self._k_nearest_values[name, 'RIVER'], hs)
              hand._hand_strength_actual[name, 'RIVER'] = hs

              # print nearest values for testing
              #print name + ' shape k nearest values ' + str(np.shape(self._k_nearest_values[name, 'FLOP']))
              #print name + ' shape k nearest matrices ' + str(np.shape(self._k_nearest_matrices[name, 'FLOP']))

                  
    # Clean up the socket.
    s.close()


  def getStraightDraw(self, board):

    board_ids = []
    for c in board:
      card_id = c[0]
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

    if 1 or 2 or 3 in id_difs:
      draw = True
    else:
      draw = False

    return draw


  def getStraight(self, board):

    board_ids = []
    for c in board:
      card_id = c[0]
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

    straight = False
    if 1 and 3 in id_difs:
      straight = True
    elif 1 and 2 in id_difs:
      straight = True
    elif 2 and 3 in id_difs:
      straight = True

    return straight


  def getPairs(self, board):

    board_ids = []
    for c in board:
      board_ids.append(c[0])

    if board_ids.count('2') >= 2 or board_ids.count('3') >= 2 or board_ids.count('4') >= 2 or board_ids.count('5') >= 2 or board_ids.count('6') >= 2 or board_ids.count('7') >= 2 or board_ids.count('8') >= 2 or board_ids.count('9') >= 2 or board_ids.count('T') >= 2 or board_ids.count('J') >= 2 or board_ids.count('Q') >= 2 or board_ids.count('K') >= 2 or board_ids.count('A') >= 2: 
      pair = True
    else:
      pair = False

    return pair


  def getCard(self, board, c):

    board_ids = []
    for board_card in board:
      board_ids.append(board_card[0])

    if c in board_ids:
      card_present = True
    else:
      card_present = False

    return card_present


  def getFlushDraw(self, board):

    suits = []
    for c in board:
      suits.append(c[1])

    if suits.count('s') >= 2 or suits.count('d') >= 2 or suits.count('c') >= 2 or suits.count('h') >= 2:
      draw = True
    else:
      draw = False

    return draw


  def getFlush(self, board):

    suits = []
    for c in board:
      suits.append(c[1])

    if suits.count('s') >= 3 or suits.count('d') >= 3 or suits.count('c') >= 3 or suits.count('h') >= 3:
      flush = True
    else:
      flush = False

    return flush


  def getAction(self, equity, pot_size, legal_actions):

    equity_bet = equity*pot_size

    action_dict = {}
    for legal_action in legal_actions:
      action_dict[legal_action[0]] = legal_action[1:]

    action = "CHECK\n"

    if 'CALL' in action_dict.keys():
      if equity_bet < float(action_dict['CALL'][0]):
        val = random.random()
        if val < equity_bet / float(action_dict['CALL'][0]):
          action = "CALL:" + action_dict['CALL'][0] + "\n"
        else:
          action = "FOLD\n"
      elif 'RAISE' in action_dict.keys():
        if equity_bet > float(action_dict['RAISE'][1]) and random.random() > 0.5:
          action = "RAISE:" + action_dict['RAISE'][1] + "\n"
        elif equity_bet > float(action_dict['RAISE'][0]) and random.random() > 0.5:
          action = "RAISE:" + str(round(equity_bet)) + "\n"
        else:
          action = "CALL:" + action_dict['CALL'][0] + "\n"
      else:
          action = "CALL:" + action_dict['CALL'][0] + "\n"
    elif 'CHECK' in action_dict.keys() and 'BET' in action_dict.keys():
      if equity_bet > float(action_dict['BET'][1]) and random.random() > 0.5:
        action = "BET:" + action_dict['BET'][1] + "\n"
      elif equity_bet > float(action_dict['BET'][0]) and random.random() > 0.5:
        action = "BET:" + str(round(equity_bet)) + "\n"
      else: 
        action = "CHECK\n"
    else:
      if equity_bet > float(action_dict['RAISE'][1]) and random.random() > 0.5:
        action = "RAISE:" + action_dict['RAISE'][1] + "\n"
      elif equity_bet > float(action_dict['RAISE'][0]) and random.random() > 0.5:
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


  def computeEquity(self, hand, board, iters=100):

    hand_cards = []
    for c in hand:
      hand_cards.append(card.Card.new(c))
  
    board_cards_init = []
    for c in board:
      board_cards_init.append(card.Card.new(c))

    win = 0
    lose = 0
    eval = evaluator.Evaluator()


    for i in xrange(iters):      

      # Draw opponent cards
      d = deck.Deck()
      opp_cards = []
      while len(opp_cards) < 2:
        c = d.draw(1)
        if c in board_cards_init or c in hand_cards:
          c = d.draw(1)
        else:
          opp_cards.append(c)
      
      # complete board
      board_cards = copy.deepcopy(board_cards_init)
      for j in xrange(5 - len(board_cards_init)):
        c = d.draw(1)
        found = False
        while not found:
          if c in board_cards or c in opp_cards or c in hand_cards:
            c = d.draw(1)
          else:
            board_cards.append(c)
            found = True

      # rank hands
      rank_me = eval.evaluate(board_cards, hand_cards)
      rank_opp = eval.evaluate(board_cards, opp_cards)
      
      if rank_opp < rank_me:
        lose += 1
      else:
        win += 1

    equity = float(win) / (win + lose)
    return equity


  def kNearest(self, x, features, values, k):

    diff = np.matrix( (x - features)**2 ).sum(axis=1).flatten().tolist()[0]
    ordered = [b for (a,b) in sorted(zip(diff, values))]
    return np.mean(ordered[:k])


        
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
