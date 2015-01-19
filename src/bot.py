import argparse
import socket
import sys
from player import *
from hand import *
from tables import *
import random
import numpy as np
import pbots_calc


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
 
        # Compute hand equity
        equity = self.computeEquity(100)
        print 'equity = ' + str(equity)

        # Make decision based on equity
        num_legal_actions = int(words[11+num_board_cards+num_actions])
        legal_actions = [a.split(':') for a in words[12+num_board_cards+num_actions:12+num_board_cards+num_actions+num_legal_actions]]
        action = self.getAction(equity, pot_size, legal_actions)        
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


    # Clean up the socket.
    s.close()


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


  def computeEquity(self, iters=100):

    hand = self._hands[-1]
    myhand = hand._cards[self._me._name][0] + hand._cards[self._me._name][1]
    equity = 0.0

    if hand._state == 'PREFLOP':
      all_active = True
      num_active = 0
      for player in self._players.itervalues():
        if not player._is_me and player._is_active:
          num_active += 1
          if len(player._potential_hands) != 9:
            all_active = False
            break

      # Compute the equity
      if all_active:
        if num_active == 1:
          equity = pbots_calc.calc(myhand + ':xx', '', '', 100)
        else:        
          equity = pbots_calc.calc(myhand + ':xx:xx', '', '', 100)    

        if equity is not None:
          return equity.ev[0]
        else:
          return 0.1
          
      else:
        return self.computeEHS(iters)

    else:
      return self.computeEHS(iters)


  def computeEHS(self, iters=100):

    hand = self._hands[-1]
    myhand = hand._cards[self._me._name][0] + hand._cards[self._me._name][1]
    board = ""
    for card in hand._board:
      board += card

    ahead = 0
    behind = 0

    # Find number of active players
    active_players = []
    for name, player in self._players.iteritems():
      if not player._is_me and player._is_active:
        active_players.append(name)

    if len(active_players) == 2:
      for cards1 in self._players[active_players[0]]._potential_hands:
        equity = pbots_calc.calc(myhand + ':' + cards1, board, '', iters)
        if equity is not None:
          if equity.ev[0] > equity.ev[1]:
            ahead += 1
          else:
            behind += 1

    else:
      for cards1 in self._players[active_players[0]]._potential_hands:
        equity = pbots_calc.calc(myhand + ':' + cards1, board, '', iters)
        if equity is not None:
          if equity.ev[0] > equity.ev[1]:
            ahead += 1
          else:
            behind += 1

    EHS = float(ahead) / (ahead + behind)
    return EHS


        
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
