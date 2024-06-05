from pacman import Directions
from game import Agent
import util
import layout
import reinforcement.api as api

# Probabilities
INTENDED_DIRECTION_PROB = 0.8
NOT_INTENDED_DIRECTION_PROB = 0.1

# Entity rewards
FOOD_REWARD = 25
GHOST_REWARD = -55
GHOST_NEIGH = -30
CAPSULE_REWARD = 20
BLANK_REWARD = -6
WALL_REWARD = -15


class MDPAgent(Agent):
    def __init__(self):
        # Default initial value
        initial = 0

        self.positions = {
            "food": [],
            "ghost": [],
            "capsule": [],
            "wall": [],
        }

        self.map_dimensions = {
            "width": 0,
            "height": 0,
        }


def registerInitialState(self, state):

    print("Running MDPAgent successfully!")

    self.Corners = api.getCorners(state)
    self.MapHeight = max(self.Corners)[1] + 1
    self.MapWidth = max(self.Corners)[0] + 1

    self.Rewards = {
        (x, y): self.BLANK_REWARD
        for x in range(self.MapWidth)
        for y in range(self.MapHeight)
    }

    def final(self, state):
        print("Looks like the game just ended!")

    def __is_medium_map(self):
        """Returns `True` if the map width is more than 10px. Otherwise, it's `False`."""
        if self.MapWidth >= 10:
            return True
        return False

    def getFood(self, state):
        """Returns food positions."""
        return api.food(state)

    def getWalls(self, state):
        """Returns wall positions."""
        return api.walls(state)

    def getCapsules(self, state):
        """Returns capsule positions."""
        return api.capsules(state)

    def getGhosts(self, state):
        """Returns a dictionary with the ghosts' position (as tuples of integers) as key and states as key value."""
