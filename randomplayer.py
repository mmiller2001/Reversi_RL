import random
import math

# decide if pieces are flippable in this direction
def flips( board, index, piece, step ):
   other = ('X' if piece == 'O' else 'O')
   # is an opponent's piece in first spot that way?
   here = index + step
   if here < 0 or here >= 36 or board[here] != other:
      return False
      
   if( abs(step) == 1 ): # moving left or right along row
      while( here // 6 == index // 6 and board[here] == other ):
         here = here + step
      # are we still on the same row and did we find a matching endpiece?
      return( here // 6 == index // 6 and board[here] == piece )
   
   else: # moving up or down (possibly with left/right tilt)
      while( here >= 0 and here < 36 and board[here] == other ):
         here = here + step
      # are we still on the board and did we find a matching endpiece?
      return( here >= 0 and here < 36 and board[here] == piece )
   
# decide if this is a valid move
def isValidMove( b, x, p ): # board, index, piece
   # invalid index
   if x < 0 or x >= 36:
      return False
   # space already occupied
   if b[x] != '-':
      return False 
   # otherwise, check for flipping pieces
   up    = x >= 12   # at least third row down
   down  = x <  24   # at least third row up
   left  = x % 6 > 1 # at least third column
   right = x % 6 < 4 # not past fourth column
   return (          left  and flips(b,x,p,-1)  # left
         or up   and left  and flips(b,x,p,-7)  # up/left
         or up             and flips(b,x,p,-6)  # up
         or up   and right and flips(b,x,p,-5)  # up/right
         or          right and flips(b,x,p, 1)  # right
         or down and right and flips(b,x,p, 7)  #down/right
         or down           and flips(b,x,p, 6)  # down
         or down and left  and flips(b,x,p, 5)) # down/left

class Agent:
   
   def __init__( self, xORo ):
      self.symbol = xORo
      self.board_states = list()
      self.board_switch = list()
      self.dictionary = {}

      with open("__pycache__\\agent_kb.pyc",'r+') as file:
         content = file.read()
         
         for line in content.split('\n'):
            if len(line.strip()) != 0:
               substrings = line.split()
               # if len(substrings) == 2 and len(substrings[0]) == 9:
               gameboard = substrings[0]
               probabilities = [float(e) for e in substrings[1].split(',')]
               self.dictionary[gameboard] = probabilities

         # print(self.symbol, self.dictionary)
         file.close()
         pass

   def getMove( self, gameboard ):
      # picks a random point, then cycles to the next available space
      number_list = list()
      scope = 0

      for i in range(36):
         if isValidMove(gameboard,i,self.symbol):
            number_list.append(i)
            scope += 1

      if gameboard in self.dictionary:
         probs = self.dictionary.get(gameboard)
         square = random.choices(number_list, weights=probs, k=1)
         self.board_states.append([gameboard,square[0],number_list,probs])
         move = square[0]
      else:
         probs = [(1/scope)*100 for i in range(len(number_list))]
         square = random.choices(number_list, weights=((1/scope)*100,) * len(number_list), k=1) 
         self.dictionary[gameboard] = probs
         self.board_states.append([gameboard,square[0],number_list,probs])
         move = square[0]

      return move
         
   def endGame( self, status, gameboard ):
      
      reversed_board_states = list(reversed(self.board_states))

      if status == 1: 
         i = 0
         for game, move, options, probs in reversed_board_states:
            index = 0
            while move != options[index]:
               index += 1
            if i == 0:
               probs[index] == 100
               for j in range(len(probs)):
                  if index != j:
                     probs[j] = 0
            else:
               probs[index] += probs[index]*(1/(math.pow(2,i+1)))
               if probs[index] >= 99.8000:
                  probs[index] = 100

            update = {game: probs}
            self.dictionary.update(update)
            self.board_switch.append([game,move,options,probs])
            i += 1

      elif status == -1:
         i = 0
         for game, move, options, probs in reversed_board_states:            
            index = 0
            while move != options[index]:
               index += 1

            probs[index] -= probs[index]*(1/(math.pow(2,i+1)))
            update = {game: probs}
            self.dictionary.update(update)
            self.board_switch.append([game,move,options,probs])
            
            i += 1
      else: # status == 0
         i = 0
         for game, move, options, probs in reversed_board_states:
            
            index = 0
            while move != options[index]:
               index += 1

            update = {game: probs}
            self.dictionary.update(update)
            self.board_switch.append([game,move,options,probs])
            i += 1
      
      self.board_states.clear()

   def stopPlaying( self ):

      for game, move, options, probs in self.board_switch:
         self.dictionary[game] = probs
      
      with open("__pycache__\\agent_kb.pyc",'r+') as file:
         file.truncate()
         for game_state in self.dictionary:
            probs_int = [str(a) for a in self.dictionary[game_state]]
            file.write(game_state + " " + (','.join(probs_int)) + "\n")
         file.close()
         pass
         
      print("Agent stopped training")
      self.dictionary = {}

class RandomPlayer:
   
   def __init__( self, xORo ):
      self.symbol = xORo

   def getMove( self, gameboard ):
      # picks a random point, then cycles to the next available space
      m = random.randint(0,36)
      while not isValidMove(gameboard,m,self.symbol):
         m = ( m + 1 ) % 36
      return m
         
   def endGame( self, status, gameboard ):
      # a good agent would learn here
      status = status

   def stopPlaying( self ):
      # a good agent would write out to file here
      eight = 8
