from math import *
from tables import *

class Hand(object):

  def __init__(self, words, players):
    
    self._cards = {}
    self._board = []
    self._id = None
    self._state = None
    self._actions = {}
    self._num_active = None
    self._pot_size = {}
    self._players = players
    self._features = {}
    
    # Initialize variables
    self.setState('PREFLOP')
    self.setId(int(words[1]))
    self._num_active = self.setNumActive(int(words[11]))

    for player in players.itervalues():
      player.resetPotentialHands()
    

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
      current_action = words[0]

      # Performed actions
      if current_action == 'DEAL':
        self.setState(words[1])

      elif current_action in ['BET', 'CALL', 'POST', 'RAISE']:
        player = players[words[2]]
        self._actions[self._state].append((player, current_action, int(words[1])))
        self._pot_size[self._state] += int(words[1])
        self.addFeature(player, self._state, action)
                  
      elif current_action in ['REFUND', 'TIE', 'WIN']:
        player = players[words[2]]
        self._actions[self._state].append((player, current_action, int(words[1])))

      elif current_action in ['CHECK']:
        player = players[words[1]]
        self._actions[self._state].append((player, current_action))
        self.addFeature(player, self._state, action)

      elif current_action in ['FOLD']:
        player = words[1]
        self._actions[self._state].append((player, current_action))

      elif current_action == 'SHOW':
        player = words[3]
        self._actions[self._state].append((player, current_action, words[1:3]))
        self.setCards(words[3], words[1:3])


  def addFeature(self, player, state, action, value=True):

    # Get the state to determine which feature vectors to set
    max_state_id = 3
    if state == 'FLOP':
      max_state_id = 2
    elif state == 'TURN':
      max_state_id = 1
    elif state == 'RIVER':
      max_state_id = 0

    # add feature to correct feature vector
    for state_id in xrange(max_state_id+1):
      feature_ids = self.getFeatureIds(state_id, action)
      for feature_id in feature_ids:
        self._features[(player._id, state_id)][feature_id] = value


  def getFeatureIds(self, state_id, action):

    state_offset = 0
    if state_id == 0:
      state_offset = 1

    feature_ids = []
    if action == 'CALL':
      feature_ids.append(1)
    elif action == 'CHECK':
      feature_ids.append(2)
    elif action == 'BET':
      feature_ids.append(3)
    elif action == 'RAISE':
      feature_ids.append(4)
    elif action == 'CHECK':
      feature_ids.append(2)



  def setState(self, state):

    self._actions[state] = []
    self.updatePotentialHands()

    self._state = state
    self._pot_size[self._state] = 0

    if self._state == 'FLOP':
      self._pot_size[self._state] = self._pot_size['PREFLOP']
    elif self._state == 'TURN':
      self._pot_size[self._state] = self._pot_size['FLOP']
    elif self._state == 'RIVER':
      self._pot_size[self._state] = self._pot_size['TURN']



  def updatePotentialHands(self):
    
    if self._state is not None:
      for player in self._players.itervalues():
        if not player._is_me and player._is_active:
          
          actions = []
          
          # Get player actions
          for action in self._actions[self._state]:
            if action[0] == player._name:
              actions.append(action[1])
              
          if 'BET' or 'RAISE' in actions:
            player._potential_hands = player._potential_hands[:16]
          elif 'CALL' in actions:
            player._potential_hands = player._potential_hands[:24]
          else:
            player._potential_hands = player._potential_hands[:51]

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


