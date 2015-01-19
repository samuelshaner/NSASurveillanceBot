from math import *
import numpy as np
from tables import *
import pbots_calc

class Player(object):

  def __init__(self, name, stack_size, me=False):
    
    self._name = name
    self._stack_size = stack_size
    self._is_me = me
    self._seat = None
    self._is_alive = True
    self._is_active = True
    self._weight_table = None
    self.resetWeightTable()


  def resetWeightTable(self):
    self._weight_table = np.copy(DEFAULT_WT_TABLE)
    
  def setStackSize(self, stack_size):
      
    self._stack_size = stack_size
    
    if stack_size == 0:
      self._is_alive = False
      
      
  def setSeat(self, seat):

    self._seat = seat


  def setIsActive(self, active):

    if active == 'true':
      self._is_active = True
    else:
      self._is_active = False


  def getName(self):
                                   
    return self._name


  def updateWeightTable(self, board_list, action):
    
    board = ''
    for card in board_list:
      board += card

    # Compute the effective hand strength for each hand in hand matrix
    for i in xrange(13):
      for j in xrange(13):
        card_combo = PBOT_CARD_COMBOS[i][j]
        ehs = pbots_calc.calc(card_combo + ':xx', board, '', 100)
        if ehs is not None:
          fold = exp(-1*ehs.ev[0])
          raise_bet = exp(1*(ehs.ev[0]-1))
          check_call = sin(pi*ehs.ev[0])
          total = fold + raise_bet + check_call
          raise_bet = raise_bet / total
          check_call = check_call / total

          if action in ['CHECK', 'CALL']:
            self._weight_table[i,j] *= check_call
          elif action in ['RAISE', 'BET']:
            self._weight_table[i,j] *= raise_bet


  def __repr__(self):

    string = 'PokerBot Player\n'
    string += ' Name \t\t\t\t\t = {0} \n'.format(self._name)

    if (self._is_me):
      string += ' Is me? \t\t\t\t = True \n'.format()
    else:
      string += ' Is me? \t\t\t\t = False \n'.format()

    if (self._is_active):
      string += ' Is active? \t\t = True \n'.format()
    else:
      string += ' Is active? \t\t = False \n'.format()

    if (self._is_alive):
      string += ' Is alive? \t\t\t = True \n'.format()
    else:
      string += ' Is alive? \t\t\t = False \n'.format()

    string += ' Stack size \t\t = {0} \n'.format(self._stack_size)
    string += ' Seat \t\t\t\t\t = {0} \n'.format(self._seat)

    return string

