from math import *
from tables import *

class Hand(object):

  def __init__(self, words):
    
    self._cards = {}
    self._board = []
    self._id = None
    self._state = None
    self._actions = {}
    self._seats = {}
    self._num_active = None
    self._pot_size = {}
    self._updated_weight_tables = {}

    # Initialize variables
    self.setState('PREFLOP')
    self.setId(int(words[1]))
    self._seats[words[8]] = 1
    self._seats[words[9]] = 2
    self._seats[words[10]] = 3
    self._updated_weight_tables[words[8]] = False
    self._updated_weight_tables[words[9]] = False
    self._updated_weight_tables[words[10]] = False
    self._num_active = self.setNumActive(int(words[11]))


  def setId(self, id):

    self._id = id

    
  def setBoard(self, board):
    
    self._board = board


  def setCards(self, name, cards):

    self._cards[name] = cards

    
  def setNumActive(self, num_active):

    self._num_active = num_active
    
    
  def addPerformedActions(self, actions, players):

    for action in actions:
      words = action.split(':')

      # Performed actions
      if words[0] == 'DEAL':
        self.setState(words[1])

      elif words[0] in ['BET', 'CALL', 'POST', 'RAISE']:
        self._actions[self._state].append((words[2], words[0], int(words[1])))
        self._pot_size[self._state] += int(words[1])
        
        if self._updated_weight_tables[words[2]] is False and not players[words[2]]._is_me and self._state is not 'PREFLOP':
          players[words[2]].updateWeightTable(self._board, words[0])
          self._updated_weight_tables[words[2]] = True
          
      elif words[0] in ['REFUND', 'TIE', 'WIN']:
        self._actions[self._state].append((words[2], words[0], int(words[1])))

      elif words[0] in ['CHECK']:
        self._actions[self._state].append((words[1], words[0]))

        if self._updated_weight_tables[words[1]] is False and not players[words[1]]._is_me and self._state is not 'PREFLOP':
          players[words[1]].updateWeightTable(self._board, 'CHECK')
          self._updated_weight_tables[words[1]] = True

      elif words[0] in ['FOLD']:
        self._actions[self._state].append((words[1], words[0]))

      elif words[0] == 'SHOW':
        self._actions[self._state].append((words[3], words[0], words[1:3]))
        self.setCards(words[3], words[1:3])
        continue


  def setState(self, state):

    self._state = state
    self._actions[self._state] = []
    self._pot_size[self._state] = 0

    if self._state == 'FLOP':
      self._pot_size[self._state] = self._pot_size['PREFLOP']
    elif self._state == 'TURN':
      self._pot_size[self._state] = self._pot_size['FLOP']
    elif self._state == 'RIVER':
      self._pot_size[self._state] = self._pot_size['TURN']

    for key in self._updated_weight_tables.keys():
      self._updated_weight_tables[key] = False


  def reprRound(self, actions):
    
    string = ''
    for action in actions:
      if action[1] in ['BET', 'CALL', 'POST', 'RAISE', 'REFUND', 'TIE', 'WIN']:
        string += '\t\t Player: {:15s}, Action: {:6s}, Amount: {:5d} \n'.format(action[0], action[1], action[2])
      elif action[1] in ['CHECK', 'FOLD']:
        string += '\t\t Player: {:15s}, Action: {:6s}\n'.format(action[0], action[1])
      elif action[1] == 'SHOW':
        string += '\t\t Player: {:15s}, Action: {:6s}, Cards: {:2s} {:2s} \n'.format(action[0], action[1], action[2][0], action[2][1])

    return string


  def __repr__(self):

    string = 'PokerBot Hand\n'
    string += ' Id \t\t\t\t = {0} \n'.format(self._id)
    string += ' State \t\t\t = {0} \n'.format(self._state)

    string += ' Board \t\t\t = '.format()    
    for card in self._board:
      string += '{0} '.format(card)

    string += '\n'

    string += ' Cards \n'.format()    
    for player,cards in self._cards.iteritems():
      string += '\t {:15s} - {:2s} {:2s} \n'.format(player, cards[0], cards[1])

    string += ' Actions \n'.format()    
    streets = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
    for street in streets:
      if street in self._actions.keys():
        string += '\t ROUND = {:8s}, POTSIZE = {:3d} \n'.format(street, self._pot_size[street])
        string += self.reprRound(self._actions[street])

    return string


