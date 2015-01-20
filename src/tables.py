from math import *
import numpy as np

CARDS = np.array(['Ad', 'As', 'Ac', 'Ah', 'Kd', 'Ks', 'Kc', 'Kh', 'Qd', 'Qs', 'Qc', 'Qh',
         'Jd', 'Js', 'Jc', 'Jh', 'Td', 'Ts', 'Tc', 'Th', '9d', '9s', '9c', '9h',
         '8d', '8s', '8c', '8h', '7d', '7s', '7c', '7h', '6d', '6s', '6c', '6h',
         '5d', '5s', '5c', '5h', '4d', '4s', '4c', '4h', '3d', '3s', '3c', '3h',
         '2d', '2s', '2c', '2h'])

CARD_COMBOS = np.array([['AA' , 'AKs', 'AQs', 'AJs', 'ATs', 'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s'],
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
                        ['2Ao', '2Ko', '2Qo', '2Jo', '2To', '29o', '28o', '27o', '26o', '25o', '24o', '23o', '22' ]])
                
lengths = [5, 5, 6, 8, 17, 10, 19, 15, 84]
lengths2 = [5, 10, 16, 24, 41, 51, 70, 85, 169]
CARD_COMBOS_RANKED = [['AA' , 'KK' , 'QQ' , 'JJ' , 'AKs']]
#CARD_COMBOS_RANKED = [['AA' , 'KK' , 'QQ' , 'JJ' , 'AKs'], 
#                      ['AQs', 'AJs', 'AKo', 'KQs', 'TT' ], 
#                      ['ATs', 'KJs', 'AQo', 'QJs', 'JTs', '99' ], 
#                      ['KTs', 'KQo', 'QTs', 'AJo', 'J9s', 'T9s', '98s', '88' ], 
#                      ['A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', 
#                       'Q9s', 'KJo', 'QJo', 'JTo', 'T8s', '97s', '87s', '77' , '76s'],
#                      ['K9s', 'J8s', 'ATo', 'KTo', 'QTo', '86s', '75s', '66' , '55' , '54s'], 
#                      ['K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s', 'Q8s', 'T7s', 'J9o',
#                       'T9o', '98o', '65s', '64s', '53s', '44' , '43s', '33' , '22' ],
#                      ['J7s', 'A9o', 'K9o', 'Q9o', '96s', 'J8o', 'T8o', '85s', '87o', '74s', 
#                       '76o', '65o', '54o', '42s', '32s'],
#                      ['Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s',
#                       'T6s', 'T5s', 'T4s', 'T3s', 'T2s', '95s', '94s', '93s', '92s', 'A8o', 'K8o', 
#                       'Q8o', '84s', '83s', '82s', 'A7o', 'K7o', 'Q7o', 'J7o', 'T7o', '97o', '73s', 
#                       '72s', 'A6o', 'K6o', 'Q6o', 'J6o', 'T6o', '96o', '86o', '63s', '62s', 'A5o', 
#                       'K5o', 'Q5o', 'J5o', 'T5o', '95o', '85o', '75o', '52s', 'A4o', 'K4o', 'Q4o', 
#                       'J4o', 'T4o', '94o', '84o', '74o', '64o', 'A3o', 'K3o', 'Q3o', 'J3o', 'T3o', 
#                       '93o', '83o', '73o', '63o', '53o', '43o', 'A2o', 'K2o', 'Q2o', 'J2o', 'T2o', 
#                       '92o', '82o', '72o', '62o', '52o', '42o', '32o']]

CARD_COMBOS_RANKED2 = np.array(['AA' , 'KK' , 'QQ' , 'JJ' , 'AKs',
                                'AQs', 'AJs', 'AKo', 'KQs', 'TT' , 
                                'ATs', 'KJs', 'AQo', 'QJs', 'JTs', '99' , 
                                'KTs', 'KQo', 'QTs', 'AJo', 'J9s', 'T9s', '98s', '88' , 
                                'A9s', 'A8s', 'A7s', 'A6s', 'A5s', 'A4s', 'A3s', 'A2s', 
                                'Q9s', 'KJo', 'QJo', 'JTo', 'T8s', '97s', '87s', '77' , '76s',
                                'K9s', 'J8s', 'ATo', 'KTo', 'QTo', '86s', '75s', '66' , '55' , '54s', 
                                'K8s', 'K7s', 'K6s', 'K5s', 'K4s', 'K3s', 'K2s', 'Q8s', 'T7s', 'J9o',
                                'T9o', '98o', '65s', '64s', '53s', '44' , '43s', '33' , '22' ,
                                'J7s', 'A9o', 'K9o', 'Q9o', '96s', 'J8o', 'T8o', '85s', '87o', '74s', 
                                '76o', '65o', '54o', '42s', '32s',
                                'Q7s', 'Q6s', 'Q5s', 'Q4s', 'Q3s', 'Q2s', 'J6s', 'J5s', 'J4s', 'J3s', 'J2s',
                                'T6s', 'T5s', 'T4s', 'T3s', 'T2s', '95s', '94s', '93s', '92s', 'A8o', 'K8o', 
                                'Q8o', '84s', '83s', '82s', 'A7o', 'K7o', 'Q7o', 'J7o', 'T7o', '97o', '73s', 
                                '72s', 'A6o', 'K6o', 'Q6o', 'J6o', 'T6o', '96o', '86o', '63s', '62s', 'A5o', 
                                'K5o', 'Q5o', 'J5o', 'T5o', '95o', '85o', '75o', '52s', 'A4o', 'K4o', 'Q4o', 
                                'J4o', 'T4o', '94o', '84o', '74o', '64o', 'A3o', 'K3o', 'Q3o', 'J3o', 'T3o', 
                                '93o', '83o', '73o', '63o', '53o', '43o', 'A2o', 'K2o', 'Q2o', 'J2o', 'T2o', 
                                '92o', '82o', '72o', '62o', '52o', '42o', '32o'])


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


# Feature map map[key] = (index, weight)
FEATURE_TUPLE_TO_ID_MAP = {}
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'SEAT0')]      = (0,  1)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'SEAT1')]      = (1,  1)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'SEAT2')]      = (2,  1)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'CALL')]       = (3,  1)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'CHECK')]      = (4,  1)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'RAISE')]      = (5,  2)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'BET')]        = (6,  2)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'BETMIN')]     = (7,  2)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'BETMID')]     = (8,  2)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'BETMAX')]     = (9,  2)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'STACKMIN')]   = (10, 1)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'STACKMID')]   = (11, 1)
FEATURE_TUPLE_TO_ID_MAP[('PREFLOP', 'STACKMAX')]   = (12, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'CALL')]          = (13, 2)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'CHECK')]         = (14, 2)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'RAISE')]         = (15, 3)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'BET')]           = (16, 3)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'BETMIN')]        = (17, 3)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'BETMID')]        = (18, 3)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'BETMAX')]        = (19, 3)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'STACKMIN')]      = (20, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'STACKMID')]      = (21, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'STACKMAX')]      = (22, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'FLUSH')]         = (23, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'FLUSHDRAW')]     = (24, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'STRAIGHT')]      = (25, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'STRAIGHTDRAW')]  = (26, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'ACES')]          = (27, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'KINGS')]         = (28, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'QUEENS')]        = (29, 1)
FEATURE_TUPLE_TO_ID_MAP[('FLOP', 'PAIRS')]         = (30, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'CALL')]          = (31, 3)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'CHECK')]         = (32, 3)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'RAISE')]         = (33, 4)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'BET')]           = (34, 4)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'BETMIN')]        = (35, 4)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'BETMID')]        = (36, 4)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'BETMAX')]        = (37, 4)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'STACKMIN')]      = (38, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'STACKMID')]      = (39, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'STACKMAX')]      = (40, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'FLUSH')]         = (41, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'FLUSHDRAW')]     = (42, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'STRAIGHT')]      = (43, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'STRAIGHTDRAW')]  = (44, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'ACES')]          = (45, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'KINGS')]         = (46, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'QUEENS')]        = (47, 1)
FEATURE_TUPLE_TO_ID_MAP[('TURN', 'PAIRS')]         = (48, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'CALL')]         = (49, 4)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'CHECK')]        = (50, 4)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'RAISE')]        = (51, 5)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'BET')]          = (52, 5)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'BETMIN')]       = (53, 5)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'BETMID')]       = (54, 5)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'BETMAX')]       = (55, 5)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'STACKMIN')]     = (56, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'STACKMID')]     = (57, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'STACKMAX')]     = (58, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'FLUSH')]        = (59, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'FLUSHDRAW')]    = (60, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'STRAIGHT')]     = (61, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'STRAIGHTDRAW')] = (62, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'ACES')]         = (63, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'KINGS')]        = (64, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'QUEENS')]       = (65, 1)
FEATURE_TUPLE_TO_ID_MAP[('RIVER', 'PAIRS')]        = (66, 1)

