# Simplified and optimized version of MDPAgent class in myVapAgents.py

from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys
import copy


class MDPAgent(Agent):
    # Entity rewards
    FOOD_REWARD = 20
    GHOST_REWARD = -50
    DANGER_ZONE_REWARD = -25
    CAPSULE_REWARD = 15
    BLANK_REWARD = -3
    WALL_REWARD = -10
    THETA = 0.1
    SAFETY_DISTANCE = 1

    def __init__(self, discount=0.9, iterations=100, noise=0.2):
        self.map_width = None
        self.map_height = None

        # positions
        self.floors = None
        self.walls = None
        self.blank = None
        self.capsules = None
        self.pacman = None
        self.rewards = dict()

        self.iterations = iterations
        self.values = util.Counter()
        self.noise = noise
        self.discount = discount

    def registerInitialState(self, game_state):
        # self.corners = api.get_corners(game_state)
        # self.corners = api.get_inner_corners(game_state)
        self.map_width, self.map_height = api.get_map_dimensions(game_state)
        self.floors = api.get_floors(game_state)
        self.walls = api.get_walls(game_state)
        # self.adj_list = api.get_adjacency_list(self.floors)
        self.rewards = {
            (x, y): self.BLANK_REWARD
            for x in range(self.map_width)
            for y in range(self.map_height)
        }

    def final(self, game_state):
        print("Il gioco è finito")
        print("Punteggio: ", game_state.getScore())

    # def update_internal_map_state(self, game_state):

    def value_iteration(self, game_state):
        delta = 0

        for i in range(self.iterations):
            new_q_values = self.values.copy()
            for cell in self.rewards.keys():
                best_action = self.__get_best_policy(game_state, cell)
                new_q_values[cell] = self.__compute_q_value_from_values(
                    cell, best_action, game_state
                )

                delta = max(delta, abs(self.values[cell] - new_q_values[cell]))
            self.values = new_q_values
            if delta < self.THETA:
                return i

    def __compute_q_value_from_values(self, cell, action, state):
        q_value = 0
        for next_cell, prob in self.__get_transition_states_and_probs(
            cell, action, state
        ):
            reward = self.rewards[next_cell]
            q_value += prob * (reward + self.discount * self.values[next_cell])
        return q_value

    def __get_transition_states_and_probs(self, cell, action, state):
        if action == Directions.STOP:
            return [(cell, 1.0)]

        move_offsets = {
            Directions.NORTH: (0, 1),
            Directions.SOUTH: (0, -1),
            Directions.EAST: (1, 0),
            Directions.WEST: (-1, 0),
        }

        primary_offset = move_offsets[action]
        primary_cell = self.__next_cell(cell, primary_offset, state)

        successors = [(primary_cell, 1 - self.noise)]

        for side_action in (
            [Directions.EAST, Directions.WEST]
            if action in [Directions.NORTH, Directions.SOUTH]
            else [Directions.NORTH, Directions.SOUTH]
        ):
            side_offset = move_offsets[side_action]
            side_cell = self.__next_cell(cell, side_offset, state)
            successors.append((side_cell, self.noise / 2))

        return successors

    def __next_cell(self, cell, offset, state):
        next_cell = (cell[0] + offset[0], cell[1] + offset[1])
        return next_cell if self.__isAllowed(next_cell, state) else cell

    def __isAllowed(self, cell, state):
        x, y = cell
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return False
        return not state.data.layout.isWall(cell)

    def __update_rewards(self, state):
        self.foods = api.get_food(state)
        self.capsules = api.get_capsules(state)
        self.ghosts = api.get_ghosts(state)
        self.blank = api.get_blank(
            self.foods, self.ghosts, self.capsules, self.walls, self.rewards
        )

        self.rewards.update({pos: self.FOOD_REWARD for pos in api.get_food(state)})
        self.rewards.update(
            {pos: self.CAPSULE_REWARD for pos in api.get_capsules(state)}
        )
        self.rewards.update({pos: self.WALL_REWARD for pos in self.walls})
        self.rewards.update({pos: self.BLANK_REWARD for pos in self.blank})

        danger_zones = api.get_danger_zones(
            state,
            api.whereAmI(state),
            self.ghosts,
            self.map_width,
            self.map_height,
            self.SAFETY_DISTANCE,
        )

        ghost_reward, danger_reward = api.calculate_ghost_and_danger_zone_rewards(
            state, self.GHOST_REWARD, self.DANGER_ZONE_REWARD
        )

        self.rewards.update({zone: danger_reward for zone in danger_zones})
        self.rewards.update({ghost: ghost_reward for ghost in self.ghosts})

    def __get_best_policy(self, state, cell):
        legal_actions = api.legalActions(state)
        legal_actions.remove(Directions.STOP)
        best_action = None
        best_value = float("-inf")
        for action in legal_actions:
            q_value = self.__compute_q_value_from_values(cell, action, state)
            if q_value > best_value:
                best_value = q_value
                best_action = action
        return best_action

    def getAction(self, state):
        self.pacman = api.whereAmI(state)
        self.__update_rewards(state)
        self.value_iteration(state)
        best_action = self.__get_best_policy(state, self.pacman)
        return api.makeMove(best_action, api.legalActions(state))
