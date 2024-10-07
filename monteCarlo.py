
import copy
import random
import time
import sys
import math
from collections import namedtuple

from games import random_player

#import numpy as np

GameState = namedtuple('GameState', 'to_move, move, utility, board, moves')

# MonteCarlo Tree Search support

class MCTS: #Monte Carlo Tree Search implementation
    class Node:
        def __init__(self, state, par=None):
            self.state = copy.deepcopy(state)

            self.parent = par
            self.children = []
            self.visitCount = 0
            self.winScore = 0

        def getChildWithMaxScore(self):
            maxScoreChild = max(self.children, key=lambda x: x.visitCount)
            return maxScoreChild



    def __init__(self, game, state):
        self.root = self.Node(state)
        self.state = state
        self.game = game
        self.exploreFactor = math.sqrt(2)

    def isTerminalState(self, utility, moves):
        return utility != 0 or len(moves) == 0
    def monteCarloPlayer(self, timelimit = 4):
        """Entry point for Monte Carlo tree search"""
        start = time.perf_counter()
        end = start + timelimit
        """
        Use time.perf_counter() above to apply iterative deepening strategy.
         At each iteration we perform 4 stages of MCTS: 
         SELECT, EXPEND, SIMULATE, and BACKUP. Once time is up
        we use getChildWithMaxScore() to pick the node to move to
        """
        # print("MCTS: your code goes here. -10")

        while time.perf_counter() < end:
            print("\n\n===================================== Selecting Node =====================================")
            selectedNode = self.selectNode(self.root)
            print("Selected Node: ", selectedNode.state.moves)
            print("\nExpanding Node =====================================")
            if self.isTerminalState(selectedNode.state.utility, selectedNode.state.moves) == 0:
                self.expandNode(selectedNode)

            print("\nSimulating Random Play =====================================")
            winningPlayer = self.simulateRandomPlay(selectedNode)
            print("Winning Player: ", winningPlayer)
            print("\nBack Propagation =====================================")
            self.backPropagation(selectedNode, winningPlayer)

        winnerNode = self.root.getChildWithMaxScore()
        print("Winner Node: ", winnerNode.state)
        assert(winnerNode is not None)
        # self.root = winnerNode
        return winnerNode.state.move


    """SELECT stage function. walks down the tree using findBestNodeWithUCT()"""
    def selectNode(self, nd):
        node = nd
        # print("selectNode: Your code goes here -5pt")
        if len(node.children) == 0:
            self.expandNode(node)
        while len(node.children) != 0:
            node = self.findBestNodeWithUCT(node)
        return node

    def findBestNodeWithUCT(self, nd):
        """finds the child node with the highest UCT. Parse nd's children and use uctValue() to collect uct's for the
        children....."""
        childUCT = []
        # print("findBestNodeWithUCT: Your code goes here -2pt")

        for child in nd.children:
            value = self.uctValue(child.parent.visitCount, child.winScore, child.visitCount)
            childUCT.append(value)

        maxUCT = max(childUCT)
        idx = childUCT.index(maxUCT)
        return nd.children[idx]


    def uctValue(self, parentVisit, nodeScore, nodeVisit):
        """compute Upper Confidence Value for a node"""
        # print("UCT: Your code goes here -3pt")
        if nodeVisit == 0:
            return sys.maxsize
            # return 0 if self.exploreFactor == 0 else sys.maxsize
        return (nodeScore / nodeVisit) + self.exploreFactor * math.sqrt(math.log(parentVisit) / nodeVisit)
        # pass

    """EXPAND stage function. """
    def expandNode(self, nd):
        """generate all the possible child nodes and append them to nd's children"""
        # print("expandNode: Your code goes here -5pt")
        stat = nd.state
        if not nd.children:
            tempState = GameState(to_move=stat.to_move, move=stat.move, utility=stat.utility, board=stat.board, moves=stat.moves)
            for a in self.game.actions(tempState):
                childNode = self.Node(self.game.result(tempState, a), nd)
                nd.children.append(childNode)
                print("Child Node: ", childNode.state)

    """SIMULATE stage function"""
    def simulateRandomPlay(self, nd):
        # first use compute_utility() to check win possibility for the current node. IF so, return the winner's symbol X, O or N representing tie

        winStatus = self.game.compute_utility(nd.state.board, nd.state.move, nd.state.board[nd.state.move])
        if winStatus > 0:
            assert(nd.state.board[nd.state.move] == 'X')
            if nd.parent is not None:
                nd.parent.winScore = -sys.maxsize
            return 'X' if winStatus > 0 else 'O'

        """ now roll out a random play down to a terminating state """

        tempState = copy.deepcopy(nd.state)
        to_move = tempState.to_move

        while not(self.game.terminal_test(tempState)):
            action = random_player(self.game, tempState)
            tempState = self.game.result(tempState, action)

        return 'X' if winStatus > 0 else 'O' if winStatus < 0 else 'N'

    # def backPropagation(self, nd, winningPlayer):
    #     """propagate upword to update score and visit count from
    #     the current leaf node to the root node."""
    #     tempNode = nd
    #     # print("Your code goes here -5pt")
    #     while tempNode.parent:
    #         score = 0
    #         if tempNode.state.to_move == winningPlayer:  # win
    #             score = 1
    #         elif winningPlayer == "N":
    #             score = 0.5
    #         tempNode.visitCount += 1
    #         tempNode.winScore += score
    #         tempNode = tempNode.parent
    #     score = 0
    #     if tempNode.state.to_move == winningPlayer:  # win
    #         score = 1
    #     elif winningPlayer == "N":
    #         score = 0.5
    #     tempNode.visitCount += 1
    #     tempNode.winScore += score

    def backPropagation(self, nd, winningPlayer):
        """propagate upword to update score and visit count from
        the current leaf node to the root node."""
        tempNode = nd
        # print("backpropograte: Your code goes here -5pt")
        print("Winning Player: ", winningPlayer)
        while tempNode.parent:
            tempNode.visitCount += 1
            print("nd.visitCount: ", tempNode.visitCount)
            print("to move: ", tempNode.state.to_move)
            if tempNode.state.to_move == winningPlayer:
                tempNode.winScore += 1
                print("winscore: ", tempNode.winScore)
            elif winningPlayer == "N":
                tempNode.winScore += 0.5
                print("winscore: ", tempNode.winScore)
            else:
                tempNode.winScore += 0
                print("winscore: ", tempNode.winScore)
            tempNode = tempNode.parent

        tempNode.visitCount += 1
        print("nd.visitCount: ", tempNode.visitCount)
        print("to move: ", tempNode.state.to_move)
        if tempNode.state.to_move == winningPlayer:
            tempNode.winScore += 1
            print("winscore: ", tempNode.winScore)
        elif winningPlayer == "N":
            tempNode.winScore += 0.5
            print("winscore: ", tempNode.winScore)
        else:
            tempNode.winScore += 0
            print("winscore: ", tempNode.winScore)


