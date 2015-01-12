from math import *
import numpy as np

CARDS = ['Ad', 'As', 'Ac', 'Ah', 'Kd', 'Ks', 'Kc', 'Kh', 'Qd', 'Qs', 'Qc', 'Qh',
         'Jd', 'Js', 'Jc', 'Jh', 'Td', 'Ts', 'Tc', 'Th', '9d', '9s', '9c', '9h',
         '8d', '8s', '8c', '8h', '7d', '7s', '7c', '7h', '6d', '6s', '6c', '6h',
         '5d', '5s', '5c', '5h', '4d', '4s', '4c', '4h', '3d', '3s', '3c', '3h',
         '2d', '2s', '2c', '2h']

PBOT_CARD_COMBOS = [['AA' , 'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s'],
                    ['KAo', 'KK' , 'KQs', 'KJs', 'KTs', 'K9s', 'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s'],
                    ['QAo', 'QKo', 'QQ' , 'QJs', 'QTs', 'Q9s', 'Q8s', 'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s'],
                    ['JAo', 'JKo', 'JQo', 'JJ' , 'JTs', 'J9s', 'J8s', 'J7s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s'],
                    ['TAo', 'TKo', 'TQo', 'TJo', 'TT' , 'T9s', 'T8s', 'T7s', 'T6s', 'T5s', 'T4s', 'T3s', 'T2s'],
                    ['9Ao', '9Ko', '9Qo', '9Jo', '9To', '99' , '98s', '97s', '96s', '95s', '94s', '93s', '92s'],
                    ['8Ao', '8Ko', '8Qo', '8Jo', '8To', '89o', '88' , '87s', '86s', '85s', '84s', '83s', '82s'],
                    ['7Ao', '7Ko', '7Qo', '7Jo', '7To', '79o', '78o', '77' , '76s', '75s', '74s', '73s', '72s'],
                    ['6Ao', '6Ko', '6Qo', '6Jo', '6To', '69o', '68o', '67o', '66' , '65s', '64s', '63s', '62s'],
                    ['5Ao', '5Ko', '5Qo', '5Jo', '5To', '59o', '58o', '57o', '56o', '55' , '54s', '53s', '52s'],
                    ['4Ao', '4Ko', '4Qo', '4Jo', '4To', '49o', '48o', '47o', '46o', '45o', '44' , '43s', '42s'],
                    ['3Ao', '3Ko', '3Qo', '3Jo', '3To', '39o', '38o', '37o', '36o', '35o', '34o', '33' , '32s'],
                    ['2Ao', '2Ko', '2Qo', '2Jo', '2To', '29o', '28o', '27o', '26o', '25o', '24o', '23o', '22' ]]
                

CARD_STRING_TO_WT_INDEX = {}
CARD_STRING_TO_WT_INDEX['Ad'] = 0
CARD_STRING_TO_WT_INDEX['As'] = 1
CARD_STRING_TO_WT_INDEX['Ac'] = 2
CARD_STRING_TO_WT_INDEX['Ah'] = 3
CARD_STRING_TO_WT_INDEX['Kd'] = 4
CARD_STRING_TO_WT_INDEX['Ks'] = 5
CARD_STRING_TO_WT_INDEX['Kc'] = 6
CARD_STRING_TO_WT_INDEX['Kh'] = 7
CARD_STRING_TO_WT_INDEX['Qd'] = 8
CARD_STRING_TO_WT_INDEX['Qs'] = 9
CARD_STRING_TO_WT_INDEX['Qc'] = 10
CARD_STRING_TO_WT_INDEX['Qh'] = 11
CARD_STRING_TO_WT_INDEX['Jd'] = 12
CARD_STRING_TO_WT_INDEX['Js'] = 13
CARD_STRING_TO_WT_INDEX['Jc'] = 14
CARD_STRING_TO_WT_INDEX['Jh'] = 15
CARD_STRING_TO_WT_INDEX['Td'] = 16
CARD_STRING_TO_WT_INDEX['Ts'] = 17
CARD_STRING_TO_WT_INDEX['Tc'] = 18
CARD_STRING_TO_WT_INDEX['Th'] = 19
CARD_STRING_TO_WT_INDEX['9d'] = 20
CARD_STRING_TO_WT_INDEX['9s'] = 21
CARD_STRING_TO_WT_INDEX['9c'] = 22
CARD_STRING_TO_WT_INDEX['9h'] = 23
CARD_STRING_TO_WT_INDEX['8d'] = 24
CARD_STRING_TO_WT_INDEX['8s'] = 25
CARD_STRING_TO_WT_INDEX['8c'] = 26
CARD_STRING_TO_WT_INDEX['8h'] = 27
CARD_STRING_TO_WT_INDEX['7d'] = 28
CARD_STRING_TO_WT_INDEX['7s'] = 29
CARD_STRING_TO_WT_INDEX['7c'] = 30
CARD_STRING_TO_WT_INDEX['7h'] = 31
CARD_STRING_TO_WT_INDEX['6d'] = 32
CARD_STRING_TO_WT_INDEX['6s'] = 33
CARD_STRING_TO_WT_INDEX['6c'] = 34
CARD_STRING_TO_WT_INDEX['6h'] = 35
CARD_STRING_TO_WT_INDEX['5d'] = 36
CARD_STRING_TO_WT_INDEX['5s'] = 37
CARD_STRING_TO_WT_INDEX['5c'] = 38
CARD_STRING_TO_WT_INDEX['5h'] = 39
CARD_STRING_TO_WT_INDEX['4d'] = 40
CARD_STRING_TO_WT_INDEX['4s'] = 41
CARD_STRING_TO_WT_INDEX['4c'] = 42
CARD_STRING_TO_WT_INDEX['4h'] = 43
CARD_STRING_TO_WT_INDEX['3d'] = 44
CARD_STRING_TO_WT_INDEX['3s'] = 45
CARD_STRING_TO_WT_INDEX['3c'] = 46
CARD_STRING_TO_WT_INDEX['3h'] = 47
CARD_STRING_TO_WT_INDEX['2d'] = 48
CARD_STRING_TO_WT_INDEX['2s'] = 49
CARD_STRING_TO_WT_INDEX['2c'] = 50
CARD_STRING_TO_WT_INDEX['2h'] = 51


# Create lower triangular matrix of ones as default weights
DEFAULT_WT_TABLE = np.ones((13,13), dtype=float)
DEFAULT_WT_TABLE = DEFAULT_WT_TABLE / np.sum(DEFAULT_WT_TABLE) 
