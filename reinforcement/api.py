def corners(state):
    return state.getCorners()


def food(state):
    return state.getFood().asList()


def walls(state):
    return state.getWalls().asList()


def capsules(state):
    return state.getCapsules()


def ghostStates(state):
    ghostPositions = state.getGhostPositions()
    ghostStates = state.getGhostStates()
    return zip(ghostPositions, ghostStates)


def whereAmI(state):
    return state.getPacmanPosition()


def legalActions(state):
    return state.getLegalActions()


def makeMove(state, action):
    return state.generateSuccessor(0, action)
