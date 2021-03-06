# searchAgents.py
# ---------------
# Licensing Information:  You are free to use or extend these projects for 
# educational purposes provided that (1) you do not distribute or publish 
# solutions, (2) you retain this notice, and (3) you provide clear 
# attribution to UC Berkeley, including a link to 
# http://inst.eecs.berkeley.edu/~cs188/pacman/pacman.html
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero 
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and 
# Pieter Abbeel (pabbeel@cs.berkeley.edu).

"""
This file contains all of the agents that can be selected to
control Pacman.  To select an agent, use the '-p' option
when running pacman.py.  Arguments can be passed to your agent
using '-a'.  For example, to load a SearchAgent that uses
depth first search (dfs), run the following command:

> python pacman.py -p SearchAgent -a fn=depthFirstSearch

Commands to invoke other search strategies can be found in the
project description.

Please only change the parts of the file you are asked to.
Look for the lines that say

"*** YOUR CODE HERE ***"

The parts you fill in start about 3/4 of the way down.  Follow the
project description for details.

Good luck and happy searching!
"""
from game import Directions
from game import Agent
from game import Actions
import util
import time
import search
import math
import code

class GoWestAgent(Agent):
    "An agent that goes West until it can't."

    def getAction(self, state):
        "The agent receives a GameState (defined in pacman.py)."
        if Directions.WEST in state.getLegalPacmanActions():
            return Directions.WEST
        else:
            return Directions.STOP

#######################################################
# This portion is written for you, but will only work #
#       after you fill in parts of search.py          #
#######################################################

class SearchAgent(Agent):
    """
    This very general search agent finds a path using a supplied search algorithm for a
    supplied search problem, then returns actions to follow that path.

    As a default, this agent runs DFS on a PositionSearchProblem to find location (1,1)

    Options for fn include:
      depthFirstSearch or dfs
      breadthFirstSearch or bfs

    Note: You should NOT change any code in SearchAgent
    """

    def __init__(self, fn='depthFirstSearch', prob='PositionSearchProblem', heuristic='nullHeuristic'):
        # Warning: some advanced Python magic is employed below to find the right functions and problems

        # Get the search function from the name and heuristic
        if fn not in dir(search):
            raise AttributeError, fn + ' is not a search function in search.py.'
        func = getattr(search, fn)
        if 'heuristic' not in func.func_code.co_varnames:
            print('[SearchAgent] using function ' + fn)
            self.searchFunction = func
        else:
            if heuristic in globals().keys():
                heur = globals()[heuristic]
            elif heuristic in dir(search):
                heur = getattr(search, heuristic)
            else:
                raise AttributeError, heuristic + ' is not a function in searchAgents.py or search.py.'
            print('[SearchAgent] using function %s and heuristic %s' % (fn, heuristic))
            # Note: this bit of Python trickery combines the search algorithm and the heuristic
            self.searchFunction = lambda x: func(x, heuristic=heur)

        # Get the search problem type from the name
        if prob not in globals().keys() or not prob.endswith('Problem'):
            raise AttributeError, prob + ' is not a search problem type in SearchAgents.py.'
        self.searchType = globals()[prob]
        print('[SearchAgent] using problem type ' + prob)

    def registerInitialState(self, state):
        """
        This is the first time that the agent sees the layout of the game board. Here, we
        choose a path to the goal.  In this phase, the agent should compute the path to the
        goal and store it in a local variable.  All of the work is done in this method!

        state: a GameState object (pacman.py)
        """
        if self.searchFunction == None: raise Exception, "No search function provided for SearchAgent"
        starttime = time.time()
        problem = self.searchType(state) # Makes a new search problem
        self.actions  = self.searchFunction(problem) # Find a path
        totalCost = problem.getCostOfActions(self.actions)
        print('Path found with total cost of %d in %.1f seconds' % (totalCost, time.time() - starttime))
        if '_expanded' in dir(problem): print('Search nodes expanded: %d' % problem._expanded)

    def getAction(self, state):
        """
        Returns the next action in the path chosen earlier (in registerInitialState).  Return
        Directions.STOP if there is no further action to take.

        state: a GameState object (pacman.py)
        """
        if 'actionIndex' not in dir(self): self.actionIndex = 0
        i = self.actionIndex
        self.actionIndex += 1
        if i < len(self.actions):
            return self.actions[i]
        else:
            return Directions.STOP

class PositionSearchProblem(search.SearchProblem):
    """
    A search problem defines the state space, start state, goal test,
    successor function and cost function.  This search problem can be
    used to find paths to a particular point on the pacman board.

    The state space consists of (x,y) positions in a pacman game.

    Note: this search problem is fully specified; you should NOT change it.
    """

    def __init__(self, gameState, costFn = lambda x: 1, goal=(1,1), start=None, warn=True, visualize=True):
        """
        Stores the start and goal.

        gameState: A GameState object (pacman.py)
        costFn: A function from a search state (tuple) to a non-negative number
        goal: A position in the gameState
        """
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        if start != None: self.startState = start
        self.goal = goal
        self.costFn = costFn
        self.visualize = visualize
        if warn and (gameState.getNumFood() != 1 or not gameState.hasFood(*goal)):
            print 'Warning: this does not look like a regular search maze'

        # For display purposes
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def getStartState(self):
        return self.startState

    def isGoalState(self, state):
        isGoal = state == self.goal

        # For display purposes only
        if isGoal and self.visualize:
            self._visitedlist.append(state)
            import __main__
            if '_display' in dir(__main__):
                if 'drawExpandedCells' in dir(__main__._display): #@UndefinedVariable
                    __main__._display.drawExpandedCells(self._visitedlist) #@UndefinedVariable

        return isGoal

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """

        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextState = (nextx, nexty)
                cost = self.costFn(nextState)
                successors.append( ( nextState, action, cost) )

        # Bookkeeping for display purposes
        self._expanded += 1
        if state not in self._visited:
            self._visited[state] = True
            self._visitedlist.append(state)

        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999
        """
        if actions == None: return 999999
        x,y= self.getStartState()
        cost = 0
        for action in actions:
            # Check figure out the next state and see whether its' legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
            cost += self.costFn((x,y))
        return cost

class StayEastSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the West side of the board.

    The cost function for stepping into a position (x,y) is 1/2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: .5 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

class StayWestSearchAgent(SearchAgent):
    """
    An agent for position search with a cost function that penalizes being in
    positions on the East side of the board.

    The cost function for stepping into a position (x,y) is 2^x.
    """
    def __init__(self):
        self.searchFunction = search.uniformCostSearch
        costFn = lambda pos: 2 ** pos[0]
        self.searchType = lambda state: PositionSearchProblem(state, costFn)

def manhattanHeuristic(position, problem, info={}):
    "The Manhattan distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return abs(xy1[0] - xy2[0]) + abs(xy1[1] - xy2[1])

def euclideanHeuristic(position, problem, info={}):
    "The Euclidean distance heuristic for a PositionSearchProblem"
    xy1 = position
    xy2 = problem.goal
    return ( (xy1[0] - xy2[0]) ** 2 + (xy1[1] - xy2[1]) ** 2 ) ** 0.5

#####################################################
# This portion is incomplete.  Time to write code!  #
#####################################################

class CornersProblem(search.SearchProblem):
    """
    This search problem finds paths through all four corners of a layout.

    You must select a suitable state space and successor function
    """

    def __init__(self, startingGameState):
        """
        Stores the walls, pacman's starting position and corners.
        """
        self.walls = startingGameState.getWalls()
        self.startingPosition = startingGameState.getPacmanPosition()
        top, right = self.walls.height-2, self.walls.width-2
        self.corners = ((1,1), (1,top), (right, 1), (right, top))
        for corner in self.corners:
            if not startingGameState.hasFood(*corner):
                print 'Warning: no food in corner ' + str(corner)
        self._expanded = 0 # Number of search nodes expanded
        # Please add any code here which you would like to use
        # in initializing the problem
        self.visitedCorner = (False,False,False,False)
    def getStartState(self):
        "Returns the start state (in your state space, not the full Pacman state space)"
        return (self.startingPosition, self.visitedCorner)
    def isGoalState(self, state):
        "Returns whether this search state is a goal state of the problem"
        return state[1][0] and state[1][1] and state[1][2] and state[1][3]

    def getSuccessors(self, state):
        """
        Returns successor states, the actions they require, and a cost of 1.

         As noted in search.py:
             For a given state, this should return a list of triples,
         (successor, action, stepCost), where 'successor' is a
         successor to the current state, 'action' is the action
         required to get there, and 'stepCost' is the incremental
         cost of expanding to that successor
        """
        successors = []
        for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(action)
            nextx, nexty = int(x + dx), int(y + dy)
            hitsWall = self.walls[nextx][nexty]
            if hitsWall:
              continue

            nextState = ()
            for i in range(len(self.corners)):
              if self.corners[i] == (nextx, nexty):
                nextState += (True,)
              else:
                nextState += (state[1][i],)

            successor = (((nextx, nexty), nextState), action, 1)
            successors.append(successor)

        self._expanded += 1
        return successors

    def getCostOfActions(self, actions):
        """
        Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999.  This is implemented for you.
        """
        if actions == None: return 999999
        x,y= self.startingPosition
        for action in actions:
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]: return 999999
        return len(actions)

def cornersHeuristic(state, problem):
    """
    A heuristic for the CornersProblem that you defined.

      state:   The current search state
               (a data structure you chose in your search problem)

      problem: The CornersProblem instance for this layout.

    This function should always return a number that is a lower bound
    on the shortest path from the state to a goal of the problem; i.e.
    it should be admissible (as well as consistent).
    """
    corners = problem.corners # These are the corner coordinates
    walls = problem.walls # These are the walls of the maze, as a Grid (game.py)
    distance = 0
    for i in range(len(corners)):
      if not state[1][i]:
        distance = max(distance, abs(state[0][0] - corners[i][0]) + abs(state[0][1] - corners[i][1]))
    return distance

class AStarCornersAgent(SearchAgent):
    "A SearchAgent for FoodSearchProblem using A* and your foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, cornersHeuristic)
        self.searchType = CornersProblem

class FoodSearchProblem:
    """
    A search problem associated with finding the a path that collects all of the
    food (dots) in a Pacman game.

    A search state in this problem is a tuple ( pacmanPosition, foodGrid ) where
      pacmanPosition: a tuple (x,y) of integers specifying Pacman's position
      foodGrid:       a Grid (see game.py) of either True or False, specifying remaining food
    """
    def __init__(self, startingGameState):
        self.start = (startingGameState.getPacmanPosition(), startingGameState.getFood())
        self.walls = startingGameState.getWalls()
        self.startingGameState = startingGameState
        self._expanded = 0
        self.heuristicInfo = {} # A dictionary for the heuristic to store information

    def getStartState(self):
        return self.start

    def isGoalState(self, state):
        return state[1].count() == 0

    def getSuccessors(self, state):
        "Returns successor states, the actions they require, and a cost of 1."
        successors = []
        self._expanded += 1
        for direction in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
            x,y = state[0]
            dx, dy = Actions.directionToVector(direction)
            nextx, nexty = int(x + dx), int(y + dy)
            if not self.walls[nextx][nexty]:
                nextFood = state[1].copy()
                nextFood[nextx][nexty] = False
                successors.append( ( ((nextx, nexty), nextFood), direction, 1) )
        return successors

    def getCostOfActions(self, actions):
        """Returns the cost of a particular sequence of actions.  If those actions
        include an illegal move, return 999999"""
        x,y= self.getStartState()[0]
        cost = 0
        for action in actions:
            # figure out the next state and see whether it's legal
            dx, dy = Actions.directionToVector(action)
            x, y = int(x + dx), int(y + dy)
            if self.walls[x][y]:
                return 999999
            cost += 1
        return cost

class AStarFoodSearchAgent(SearchAgent):
    "A SearchAgent for FoodSearchProblem using A* and your foodHeuristic"
    def __init__(self):
        self.searchFunction = lambda prob: search.aStarSearch(prob, foodHeuristic)
        self.searchType = FoodSearchProblem

def foodHeuristic(state, problem):
    """
    Your heuristic for the FoodSearchProblem goes here.

    This heuristic must be consistent to ensure correctness.  First, try to come up
    with an admissible heuristic; almost all admissible heuristics will be consistent
    as well.

    If using A* ever finds a solution that is worse uniform cost search finds,
    your heuristic is *not* consistent, and probably not admissible!  On the other hand,
    inadmissible or inconsistent heuristics may find optimal solutions, so be careful.

    The state is a tuple ( pacmanPosition, foodGrid ) where foodGrid is a
    Grid (see game.py) of either True or False. You can call foodGrid.asList()
    to get a list of food coordinates instead.

    If you want access to info like walls, capsules, etc., you can query the problem.
    For example, problem.walls gives you a Grid of where the walls are.

    If you want to *store* information to be reused in other calls to the heuristic,
    there is a dictionary called problem.heuristicInfo that you can use. For example,
    if you only want to count the walls once and store that value, try:
      problem.heuristicInfo['wallCount'] = problem.walls.count()
    Subsequent calls to this heuristic can access problem.heuristicInfo['wallCount']
    """
    position, foodGrid = state
    largest = 0
    for food in foodGrid.asList(): largest = max(largest, mazeDistance(food, position, problem.startingGameState))
    return largest

class ClosestDotSearchAgent(SearchAgent):
    "Search for all food using a sequence of searches"
    def registerInitialState(self, state):
        self.actions = []
        currentState = state
        while(currentState.getFood().count() > 0):
            nextPathSegment = self.findPathToClosestDot(currentState) # The missing piece
            self.actions += nextPathSegment
            for action in nextPathSegment:
                legal = currentState.getLegalActions()
                if action not in legal:
                    t = (str(action), str(currentState))
                    raise Exception, 'findPathToClosestDot returned an illegal move: %s!\n%s' % t
                currentState = currentState.generateSuccessor(0, action)
        self.actionIndex = 0
        print 'Path found with cost %d.' % len(self.actions)

    def findPathToClosestDot(self, gameState):
        "Returns a path (a list of actions) to the closest dot, starting from gameState"
        # Here are some useful elements of the startState
        startPosition = gameState.getPacmanPosition()
        food = gameState.getFood()
        walls = gameState.getWalls()
        problem = AnyFoodSearchProblem(gameState)
        return search.aStarSearch(problem)

class AnyFoodSearchProblem(PositionSearchProblem):
    """
      A search problem for finding a path to any food.

      This search problem is just like the PositionSearchProblem, but
      has a different goal test, which you need to fill in below.  The
      state space and successor function do not need to be changed.

      The class definition above, AnyFoodSearchProblem(PositionSearchProblem),
      inherits the methods of the PositionSearchProblem.

      You can use this search problem to help you fill in
      the findPathToClosestDot method.
    """

    def __init__(self, gameState):
        "Stores information from the gameState.  You don't need to change this."
        # Store the food for later reference
        self.food = gameState.getFood()

        # Store info for the PositionSearchProblem (no need to change this)
        self.walls = gameState.getWalls()
        self.startState = gameState.getPacmanPosition()
        self.costFn = lambda x: 1
        self._visited, self._visitedlist, self._expanded = {}, [], 0

    def isGoalState(self, state):
        """
        The state is Pacman's position. Fill this in with a goal test
        that will complete the problem definition.
        """
        return self.food[state[0]][state[1]]

##################
# Mini-contest 1 #
##################

from functools import wraps
def memo(func):
    cache = {}
    @ wraps(func)
    def wrap(*args):
        if args not in cache:
            cache[args] = func(*args)
        return cache[args]
    return wrap

class Vertex:
  def __init__(self, x, y):
    self.x = x
    self.y = y
    self.edges = []
  def getCoord(self):
    return (self.x, self.y)
  def getEdges(self):
    return self.edges
  def __str__(self):
    return "Vertex"+ str(self.getCoord())
  def __repr__(self):
    return "Vertex"+str(self.getCoord())
  def __eq__(self, other):
    return self.getCoord() == other.getCoord()
  def __hash__(self):
    return hash(self.getCoord())

class Edge:
  def __init__(self, v1, v2, actions):
    self.u = v1
    self.v = v2
    self.actions = actions
  def __repr__(self):
    return str(self.u) + '->' + str(self.v)
  def dest(self, origin):
    if self.u == origin: return self.v
    return self.u
  def __len__(self):
    return max([ len(action) for action in self.actions.values()])

import itertools
class Graph:
  def __init__(self):
    self.vertices = {}
    self.edges = {}
  def add(self, k1, k2, actions):
    if k1 not in self.vertices:
      self.vertices[k1] = Vertex(k1[0], k1[1])
    if k2 not in self.vertices:
      self.vertices[k2] = Vertex(k2[0], k2[1])
    if k1 not in self.edges:
      self.edges[k1] = {}
    if k2 not in self.edges:
      self.edges[k2] = {}
    self.edges[k1][k2] = self.edges[k2][k1] = Edge(self.vertices[k1], self.vertices[k2], actions)
    self.vertices[k1].edges.append(self.edges[k1][k2])
    self.vertices[k2].edges.append(self.edges[k1][k2])
  def edgeExists(self, k1, k2):
    return k1 in self.edges and k2 in self.edges[k1]
  def getEdges(self):
    return set(itertools.chain(*[ self.edges[v].values() for v in self.edges ])) 
  def getVertices(self):
    return self.vertices
  def getVertex(self, pos):
    return self.vertices[pos]

class MinPathCover:
  def __init__(self, graph):
    self.graph = graph
  def closestUnvisited(self, v, visited, k=3):
    closest = {} 
    root = v
    Q = util.PriorityQueue()
    Q.push((root, []), 0)
    while not Q.isEmpty() and len(visited) < len(self.graph.getVertices()) and len(closest) < k:
      current, actions = Q.pop()
      if (current not in visited) and (current not in closest): 
        closest[current] = actions
      for e in current.getEdges():
        newCost = len(actions) + len(e)
        Q.push((e.dest(current), actions + [e]), newCost)
    return closest

  def path(self, start, visited = [], edges = []):
    visited += [start]
    options  = []
    if len(visited) == len(self.graph.getVertices()):
      print(visited)
    for v,actions in self.closestUnvisited(start, visited).iteritems():
      options += self.path(v, visited, edges + actions)
    code.interact(local=locals())
    return min(options, key=lambda actions: reduce( lambda x, y: x + len(y), actions))



class PairDict:
  def __init__(self):
    self.dictionary = {}

  def setValue(self, k1, k2, v):
    if k1 not in self.dictionary and k2 not in self.dictionary:
      self.dictionary[k1] = {k2: v}
    elif k1 in self.dictionary and k2 not in self.dictionary[k1]:
      self.dictionary[k1][k2] = v
    elif k2 in self.dictionary and k1 not in self.dictionary[k2]:
      self.dictionary[k2][k1] = v
    else:
      pass #both in dict already

  def getValue(self, k1, k2):
    if self.hasValue(k1, k2):
      if k1 in self.dictionary and k2 in self.dictionary[k1]: return self.dictionary[k1][k2]
      return self.dictionary[k2][k1]

    return None
  
  def getNeighbors(self, k):
    ret = []
    for k1 in self.dictionary:
      if k1 == k:
        ret += list(self.dictionary[k1].keys())
        continue
      for k2 in self.dictionary[k1]:
        if k2 == k:
          ret.append(k1)
          break
    return ret

  def hasValue(self, k1, k2):
    return (k1 in self.dictionary and k2 in self.dictionary[k1]) or (k2 in self.dictionary and k1 in self.dictionary[k2])

  def __str__(self):
    ret = ''
    for k1 in self.dictionary:
      for k2 in self.dictionary[k1]:
        if k1 < k2: ret = ret + str(k1) + ' <-> ' + str(k2) + ' : ' + str(self.dictionary[k1][k2]) + '\n'
        else: ret = ret + str(k2) + ' <-> ' + str(k1) + ' : ' + str(self.dictionary[k1][k2]) + '\n'
    return ret

class ApproximateSearchAgent(Agent):
    "Implement your contest entry here.  Change anything but the class name."

    def drawSquare(self, pos, color='red'):
      import graphicsUtils
      def getColor(c):
        colors = {
          -1 : '#ff0000',
          0 : '#ffffff',
          1 : '#00ff00',
          2 : '#ffff00'
        }
        if c in colors: return colors[c]
        else: return c
      color = getColor(color)
      graphicsUtils.square((pos[0]*15 + 14, 15*(14-pos[1]) + 14), 7.5, color)

    def getNodeType(self, pos):
      walls = self.walls
      food = self.food
      paths = 0
      x, y = pos
      if not self.isValid((pos[0],pos[1])): return -1
      elif self.state.getPacmanPosition() == pos: return 1
      for i in [-1, 1]:
        if self.isValid((pos[0]+i,pos[1])): paths += 1
        if self.isValid((pos[0],pos[1]+i)): paths += 1
        for j in [-1, 1]:
          if self.isValid((pos[0],pos[1]+j)) and self.isValid((pos[0]+i,pos[1])) and self.isValid((pos[0]+i,pos[1]+j)): return 1

      if (paths >= 3 and paths <= 4) or paths == 1: return 1
      return 0

    def isValid(self, pos):
      return (pos[0] >= 0 and pos[1] >= 0 and pos[0] < self.walls.width and pos[1] < self.walls.height) and (not self.walls[pos[0]][pos[1]] and self.food[pos[0]][pos[1]]) or pos == self.state.getPacmanPosition()

    def registerInitialState(self, state):
      "Setup initial state"
      self.actions = []
      self.state = state
      self.food = state.getFood()
      self.walls = state.getWalls()
      self.linksVisited = set()
      self.blocksVisited = set()
      self.graph = Graph()
      self.paths = PairDict() # key: (to, from)
      self.length = 0
      self.p = MinPathCover(self.graph)
      "DFS to generate new graph"
      pos = state.getPacmanPosition()
      self.findLinks(pos, pos, set(), ((),()))
      v = self.graph.getVertex(pos)
      code.interact(local=locals())

    def findLinks(self, parent, pos, seen, actions):
      if self.isValid(pos):
        nodeType = self.getNodeType(pos)
        x, y = pos
        if nodeType == 1 and pos != parent:
          if self.graph.edgeExists(parent, pos): return
          if not self.graph.edgeExists(parent, pos): self.graph.add(parent, pos, {parent: actions[1], pos: actions[0]})
          if pos in self.linksVisited: return
          parent = pos
          actions = ((), ())
          seen = set()
          self.linksVisited.add(pos)
        elif nodeType == 2:
          if pos in self.blocksVisited: return
          self.blocksVisited.add(pos)
        self.drawSquare(pos, nodeType)

       # if  pos == (2,2):
          #import pdb; pdb.set_trace()
        for i in [-1, 1]:
          x1 = pos[0]+i
          y1 = pos[1]+i
          seen.add(pos)

          if self.isValid((x1, y)) and (self.getNodeType((x1,y)) == 1 or (x1, y) not in seen):
            nextActions = self.getDirections(pos, (x1, y))
            self.findLinks(parent, (x1, y), seen, (actions[0] + (nextActions[0],), actions[1] + (nextActions[1],)))
          if self.isValid((x, y1)) and (self.getNodeType((x,y1)) == 1 or (x, y1) not in seen):
            nextActions = self.getDirections(pos, (x, y1))
            self.findLinks(parent, (x, y1), seen, (actions[0] + (nextActions[0],), actions[1] + (nextActions[1],)))

    def getDirections(self, start, end):
      x1, y1 = start
      x2, y2 = end
      displacement = (x1 - x2, y1 - y2)
      if displacement == (1, 0): return (Directions.EAST, Directions.WEST)
      elif displacement == (-1, 0): return (Directions.WEST, Directions.EAST)
      elif displacement == (0, 1): return (Directions.NORTH, Directions.SOUTH)
      elif displacement == (0, -1): return (Directions.SOUTH, Directions.NORTH)
      else: raise Exception('Invalid positions given for getDirections')

    def getAction(self, state):
      """
      From game.py:
      The Agent will receive a GameState and must return an action from
      Directions.{North, South, East, West, Stop}
      """
      "*** YOUR CODE HERE ***"
      return self.actions.pop(0)

@memo
def mazeDistance(point1, point2, gameState):
    """
    Returns the maze distance between any two points, using the search functions
    you have already built.  The gameState can be any game state -- Pacman's position
    in that state is ignored.

    Example usage: mazeDistance( (2,4), (5,6), gameState)

    This might be a useful helper function for your ApproximateSearchAgent.
    """
    x1, y1 = point1
    x2, y2 = point2
    walls = gameState.getWalls()
    assert not walls[x1][y1], 'point1 is a wall: ' + point1
    assert not walls[x2][y2], 'point2 is a wall: ' + str(point2)
    prob = PositionSearchProblem(gameState, start=point1, goal=point2, warn=False, visualize=False)
    return len(search.bfs(prob))
