import sys
import json
import socket
import math
import random

# Used https://barberalec.github.io/pdf/An_Analysis_of_Othello_AI_Strategies.pdf for reference for factor weights.
factors = { # Used to define importance of certain features
  "corner": .64,
  "cornerNeighbor": .39,
  "cornerDiagonal": .81,
  "edge": .4,
  "central": .1,
  "pieceCount": .57,
  "mobility": .56
}

def checkBoard(player, board, currentPlayer, turn):
  """
    Function to evaluate the board at it's current position

    Parameters:
    - player (int): The identification of our player.
    - board (list): The board positions to be checked.
    - currentPlayer (int): The value of the current player.
    - turn (int): The amount of turns that have passed.

    Returns:
    A factor score to evaluate the player's position in the game.

  """

  factorScore = 0

  factorScore += evaluateCorners(board, currentPlayer)

  factorScore += evaluateEdges(board, currentPlayer)

  factorScore += evaluateDiagonal(board, currentPlayer)
  
  factorScore += evaluateMobility(board, currentPlayer)

  
  if(gamePhase(turn) == 2): 
    for (row, column) in ((3, 3), (3, 4), (4, 3), (4, 4)):
      if(board[row][column] == currentPlayer):
        factorScore += factors['central']
  
  elif(gamePhase(turn) == 3):
    playerChips = opponentChips = 0
    
    for row in range(0, 8):
      for column in range(0, 8):
        if board[row][column] == currentPlayer:
          playerChips += 1
        elif board[row][column] == getOpponent(currentPlayer):
          opponentChips += 1
    
    factorScore += ((playerChips - opponentChips) * factors["pieceCount"])

  factorScore += checkNeighbors(board, currentPlayer)

  if player == currentPlayer:
    return factorScore # Our player
  return factorScore * -1 # Our opponent

def evaluateMobility(board, currentPlayer):
  """
    Function to evaluate the mobility of the player.

    Parameters:
    - board (list): The board positions to be checked.
    - currentPlayer (int): The value of the current player.

    Returns:
    A mobility score to evaluate the player's mobility in the game.  
  """
  currentMobility = len(getValidMoves(currentPlayer, board))
  opponentMobility = len(getValidMoves(getOpponent(currentPlayer), board))

  mobilityScore = (currentMobility - opponentMobility) * factors["mobility"]

  return mobilityScore

def checkNeighbors(board, currentPlayer):
  """
    Function to check corner neighbors to evaluate the weight.

    Parameters:
    - board (list): The board positions to be checked.
    - currentPlayer (int): The value of the current player.

    Returns:
    An evaluation score to evaluate the player's corner neighbor positions.
    
  """
  evaluation = 0

  for(row, column) in ((0, 1), (1, 0), (6, 0), (1, 7), (7, 1), (7, 6), (6, 7), (0, 6)):
    if(board[row][column] == currentPlayer):
      evaluation -= factors["cornerNeighbor"]
  
  return evaluation

def evaluateCorners(board, currentPlayer):
  """
    Function to evaluate the corners of the current player.

    Parameters:
    - board (list): The board positions to be checked.
    - currentPlayer (int): The value of the current player.

    Returns:
    An evaluation score to evaluate the player's position for the corners.  
  
  """
  evaluation = 0
  
  for(row, column) in ((0, 0), (0, 7), (7, 0), (7, 7)):
    if(board[row][column] == currentPlayer):
      evaluation += factors['corner']
  
  return evaluation

def evaluateEdges(board, currentPlayer):
  """
    Function to evaluate the edges of the current player.

    Parameters:
    - board (list): The board positions to be checked.
    - currentPlayer (int): The value of the current player.

    Returns:
    An evaluation score to evaluate the player's position for the edges.  
    
  """
  evaluation = 0

  for i in range(1, 7):
        if board[0][i] == currentPlayer:
            evaluation += factors["edge"]
        if board[7][i] == currentPlayer:
            evaluation += factors["edge"]

  for i in range(1, 7):
        if board[i][0] == currentPlayer:
            evaluation += factors["edge"]
        if board[i][7] == currentPlayer:
            evaluation += factors["edge"]
    
  return evaluation

def evaluateDiagonal(board, currentPlayer):
  """
    Function to evaluate the diagonals of the current player.

    Parameters:
    - board (list): The board positions to be checked.
    - currentPlayer (int): The value of the current player.

    Returns:
    An evaluation score to evaluate the player's position for the diagonals.  
    
  """
  evaluation = 0
  
  for(row, column) in ((1, 1), (1, 6), (6, 1), (6, 6)):
    if(board[row][column] == currentPlayer):
      evaluation += factors['cornerDiagonal']
    return evaluation
      
def getOpponent(player):
  """
    Function to determine if the player is the opponent

    Parameters:
    - player (int): The value of the current player.

    Returns:
    2 if it is the opponent's turn, else 1.     
  """
  if player == 1:
    return 2
  return 1

def gamePhase(turn):
  """
    Function to determine the phase of the game. 

    Parameters:
    - turn (int): The amount of turns that have been played.

    Returns:
    An integer depending on the status of the game    
  """
  if(turn > 25):
    if(turn > 45):
      return 3 # Late-Game
    return 2 # Mid-Game
  return 1 # Early-Game

def getCornerMoves(player, board):
  """
    Function to gather all corner moves for the player. 

    Parameters:
    - player (int): The given player to check moves for.
    - board (list): The board to check moves on.

    Returns:
    A list containing all valid corner moves.
  """
  validMoves = getValidMoves(player, board)
  cornerMoves = []
  cornerPositions = [[0, 0], [0, 7], [7, 0], [7, 7]]

  for move in validMoves:
    if move in cornerPositions:
      cornerMoves.append(move)

  return cornerMoves

def getEdge(player, board):
  """
    Function to gather all valid edge moves for the player.

    Parameters:
    - player (int): The given player to check moves for.
    - board (list): The board to check moves on.

    Returns:
    A list containing all valid edge moves.
  """
  validMoves = getValidMoves(player, board)
  edgeMoves = []
  edgePositions = [[0, 2], [0, 3], [0, 4], [0, 5], [7, 2], [2, 0], [3, 0], [4, 0], [5, 0], [7, 3], [7, 4], [7, 5], [2, 7], [3, 7], [4, 7], [5, 7]]

  for move in validMoves:
    if move in edgePositions:
      edgeMoves.append(move)
  return edgeMoves

def getMove(player, board, turn):
    """
    Function to call on algorithm with valid moves to return a move to the server. 

    Parameters:
    - player (int): The given player to check moves for.
    - board (list): The board to check moves on.
    - turn (int): The amount of turns that have passed.

    Returns:
    A valid move to be used within the game.
  """  
    depth = 0
    phase = gamePhase(turn)

    if phase == 1:
        depth = 6
    elif phase == 2:
        depth = 3
    elif phase == 3:   
        depth = 2
  
    if getCornerMoves(player, board):
      print('Prioritizing Corner...')
      move = calculateBestMove(player, board, depth, player, turn, -math.inf, math.inf, getCornerMoves(player, board))[0]
    elif getEdge(player, board):
       print('Prioritizing Edge...')
       move = calculateBestMove(player, board, depth, player, turn, -math.inf, math.inf, getEdge(player, board))[0]
    else:
      print('Finding Non-Edge/Corner Move...')
      move = calculateBestMove(player, board, depth, player, turn, -math.inf, math.inf, getValidMoves(player, board))[0]
    
    print('Current Factor Score:', checkBoard(player, board, player, turn))
    
    return move

def calculateBestMove(player, board, depth, currentPlayer, turn, alpha, beta, moves):
    """
    Function to call the minimax algorithm to determine the best move for the given player and board.

    Parameters:
    - player (int): The given player to check moves for.
    - board (list): The board to check moves on.
    - depth (int): The amount to recurse for to predict future moves.
    - currentPlayer (int): The integer of the current turn's player.
    - turn (int): The number of turns that have passed.
    - alpha (float): The best value known to the maximizingPlayer.
    - beta (float): The best value known to the minimizingPlayer.
    - moves (list): The list of valid moves that are traversed through to find the best.

    Returns:
    A list containing the best move and the best score.
  """
    maximizingPlayer = player == currentPlayer

    if depth == 0 or not moves:
        return ([0, 0], checkBoard(player, board, currentPlayer, turn))

    bestMove, bestScore = None, -math.inf if maximizingPlayer else math.inf

    for move in moves:
      makeMove(currentPlayer, board, move)
      result = calculateBestMove(player, board, depth - 1, getOpponent(currentPlayer), turn + (1 if maximizingPlayer else 0), alpha, beta, moves)
      makeMove(getOpponent(currentPlayer), board, move)

      if maximizingPlayer and result[1] > bestScore:
            bestMove = move
            bestScore = result[1]
            alpha = max(alpha, bestScore)
      elif not maximizingPlayer and result[1] < bestScore:
            bestMove, bestScore = move, result[1]
            beta = min(beta, bestScore)

      if beta <= alpha:
        break
    return (bestMove, bestScore)

def makeMove(currentPlayer, board, move):
  """
    Function to take action and make the move.

    Parameters:
    - currentPlayer (int): The current turn's player.
    - board (list): The board to check moves on.
    - move (list): The given move to make.

    Returns:
    Null
  """

  for tile in getValidMoves(currentPlayer, board):
    board[tile[0]][tile[1]] = currentPlayer

  board[move[0]][move[1]] = currentPlayer

def checkMove(currentPlayer, board, move):
  """
    Function to check what tiles would be flipped for a given move.

    Parameters:
    - currentPlayer (int): The current turn's player.
    - board (list): The board to check moves on.
    - move (list): The given move to make.

    Returns:
    A list containing all tiles that would be flipped.
  """

  if board[move[0]][move[1]] != 0:
      return []

  tilesToFlip = []
  
  for xDir, yDir in [[0, 1], [1, 1], [1, 0], [1, -1], [0, -1], [-1, -1], [-1, 0], [-1, 1]]:
    x = move[0] + xDir
    y = move[1] + yDir

    while isOnBoard([x, y]) and board[x][y] == getOpponent(currentPlayer):
      x += xDir
      y += yDir

      if isOnBoard([x, y]) and board[x][y] == currentPlayer:
        x -= xDir
        y -= yDir
        
        while not ([x, y] == move):
          tilesToFlip.append([x, y])
          x -= xDir
          y -= yDir
        break

  return tilesToFlip

def isOnBoard(move):
    """
    Function to check if the move is valid and on the board.

    Parameters:
    - move (list): The given move to check.

    Returns:
    True if the move is valid, else false.
    """
    return 0 <= move[0] < 8 and 0 <= move[1] < 8

def getValidMoves(currentPlayer, board):
  """
    Function to gather all valid moves that can be made.

    Parameters:
    - currentPlayer (int): The current turn's player.
    - board (list): The board to check moves on.

    Returns:
    A list containing all valid moves that can be made.
  """
  validMoves = []
  for row in range(0, 8):
    for column in range(0, 8):
      if checkMove(currentPlayer, board, [row, column]):
        validMoves.append([row, column])
  random.shuffle(validMoves)
  return validMoves

def prepare_response(move):
  """
    Provided by Atomic Object to prepare response for the server.

    Parameters:
    - move (list): The given move to make.

    Returns:
    Response to send to server.
  """
  response = '{}\n'.format(move).encode()
  print('sending {!r}'.format(response))
  return response

if __name__ == "__main__":
  port = int(sys.argv[1]) if (len(sys.argv) > 1 and sys.argv[1]) else 1337
  host = sys.argv[2] if (len(sys.argv) > 2 and sys.argv[2]) else socket.gethostname()

  sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
  try:
    sock.connect((host, port))
    turn = 0
    while True:
      print(turn)
      data = sock.recv(1024)
      if not data:
        print('connection to server closed')
        break
      json_data = json.loads(str(data.decode('UTF-8')))
      board = json_data['board']
      max_turn_time = json_data['maxTurnTime']
      player = json_data['player']

      move = getMove(player, board, turn)
      response = prepare_response(move)
      sock.sendall(response)
      turn += 2
  finally:
    sock.close()