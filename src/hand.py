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
    self._hand_strength_predict = {}
    self._hand_strength_actual = {}
    self._hand_strength = {}
    self._player_LB = {}
    self._player_UB = {}
    self._prev_bet = 2
    
    # Initialize variables
    self.setState('PREFLOP')
    self.setId(int(words[1]))
    self._num_active = self.setNumActive(int(words[11]))

    for name,player in players.iteritems():
      player.resetPotentialHands()
      rounds = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
      for rd in rounds:
        self._features[name, rd] = np.zeros(67, dtype=float)
        self._hand_strength[name, rd] = {'LB':[], 'UB':[], 'actual':[]}
    

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

      elif current_action in ['POST']:
        player = words[2]
        self._actions[self._state].append((player, current_action, int(words[1])))
        self._pot_size[self._state] += int(words[1])

      elif current_action in ['CALL']:
        player = words[2]
        amount = int(words[1])
        
        # calculate predicted lower and upper bounds for player hand strength
        LB = float(amount) / self._pot_size[self._state]
        UB = 2 * float(amount) / self._pot_size[self._state]
        self._hand_strength[player, self._state]['LB'].append(LB)
        self._hand_strength[player, self._state]['UB'].append(UB)

        self._actions[self._state].append((player, current_action, amount))
        self._pot_size[self._state] += amount
        self.addFeature(player, self._state, current_action)

      elif current_action in ['BET', 'RAISE']:
        player = words[2]
        amount = int(words[1])

        # store current bet
        if current_action == 'BET':
          self._prev_bet = amount
        else:
          self._prev_bet = amount - self._prev_bet
        
        # calculate predicted lower and upper bounds for player hand strength
        LB = min( float(amount) / self._pot_size[self._state], 1)
        UB = min( float(amount + 1) / self._pot_size[self._state], 1)
        self._player_LB[player] = LB
        self._player_UB[player] = UB
        self._hand_strength[player, self._state]['LB'].append(LB)
        self._hand_strength[player, self._state]['UB'].append(UB)
        
        self._actions[self._state].append((player, current_action, amount))
        self._pot_size[self._state] += amount
        self.addFeature(player, self._state, current_action)
        if amount == 2:
          self.addFeature(player, self._state, 'BETMIN')
        elif amount == self._pot_size[self._state] - amount:
          self.addFeature(player, self._state, 'BETMAX')
        else:
          self.addFeature(player, self._state, 'BETMID')                  

      elif current_action in ['REFUND', 'TIE', 'WIN']:
        player = words[2]
        self._actions[self._state].append((player, current_action, int(words[1])))

      elif current_action in ['CHECK']:
        player = words[1]
        
        # calculate predicted lower and upper bounds for player hand strength
        LB = 0
        UB = float(self._prev_bet)/self._pot_size[self._state]
        self._player_LB[player] = LB
        self._player_UB[player] = UB
        self._hand_strength[player, self._state]['LB'].append(LB)
        self._hand_strength[player, self._state]['UB'].append(UB)
        
        self._actions[self._state].append((player, current_action))
        self.addFeature(player, self._state, current_action)

      elif current_action in ['FOLD']:
        player = words[1]
        
        # calculate predicted lower and upper bounds for player hand strength
        LB = 0
        UB = float(self._prev_bet)/self._pot_size[self._state]
        self._player_LB[player] = LB
        self._player_UB[player] = UB
        self._hand_strength[player, self._state]['LB'].append(LB)
        self._hand_strength[player, self._state]['UB'].append(UB) 
        
        self._actions[self._state].append((player, current_action))

      elif current_action == 'SHOW':
        player = words[3]
        self._actions[self._state].append((player, current_action, words[1:3]))
        self.setCards(words[3], words[1:3])


  def addFeature(self, player, current_state, action, value=True):

    if value is not False:
      states = []
      if current_state == 'RIVER':
        states.append('RIVER')
      if current_state == 'FLOP':
        states.append('RIVER')
        states.append('TURN')
        states.append('FLOP')
      elif current_state == 'TURN':
        states.append('RIVER')
        states.append('TURN')
      elif current_state == 'PREFLOP':
        states.append('RIVER')
        states.append('TURN')
        states.append('FLOP')
        states.append('PREFLOP')
        
      # add feature to correct feature vector
      (feature_id, weight) = FEATURE_TUPLE_TO_ID_MAP[(current_state, action)]
      for state in states:
        self._features[(player, state)][feature_id] = weight*value


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

    for player_state,hs in self._hand_strength_actual.iteritems():
        string += '\t ACTUAL  HS {:15s} - {:5.4f}\n'.format(player_state[0] + ' - ' + player_state[1], hs)

    for player_state,hs in self._hand_strength_predict.iteritems():
        string += '\t PREDICT HS {:15s} - {:5.4f}\n'.format(player_state[0] + ' - ' + player_state[1], hs)

    string += ' Actions \n'.format()    
    streets = ['PREFLOP', 'FLOP', 'TURN', 'RIVER']
    for street in streets:
      if street in self._actions.keys():
        string += '\t ROUND = {:8s}, POTSIZE = {:3d} \n'.format(street, self._pot_size[street])
        string += self.reprRound(self._actions[street])

    # print the True features for each player
    #for key,f_vector in self._features.iteritems():
    #  if not self._players[key[0]]._is_me:
    #    string += '\t Player: {:15s} - State: {:10s} \n'.format(key[0], key[1])
    #    for f_key,f_value in FEATURE_TUPLE_TO_ID_MAP.iteritems():
    #        if f_vector[f_value] == True:
    #          string += '\t Feature = {0}\n'.format(f_key) 

    return string

