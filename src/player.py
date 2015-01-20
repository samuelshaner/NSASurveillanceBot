from math import *
import numpy as np
from tables import *
import copy

class Player(object):

  def __init__(self, name, stack_size, me=False):
    
    self._name = name
    self._stack_size = stack_size
    self._is_me = me
    self._seat = None
    self._is_alive = True
    self._is_active = True
    self.resetPotentialHands()

  def resetPotentialHands(self):
    if not self._is_me:
      self._potential_hands = np.copy(CARD_COMBOS_RANKED2)


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
    
