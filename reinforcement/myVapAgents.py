from pacman import Directions
from game import Agent
import api
import random
import game
import util
import sys
import copy


class MDPAgent(Agent):
    """
    Contrustor: initialize internal memories

    @param self: the class itself
    @return None
    """

    # Entity rewards
    FOOD_REWARD = 20
    GHOST_REWARD = -50
    DANGER_ZONE_REWARD = -25
    CAPSULE_REWARD = 15
    BLANK_REWARD = -3
    WALL_REWARD = -10

    SAFETY_DISTANCE = 2
    DISCOUNT_FACTOR = 0.9
    GHOSTBUSTER_MODE = False

    # SUCCESSFUL_MOVE_PROBABILITY = 0.8
    # ACCIDENTAL_MOVE_PROBABILITY = 0.1

    def __init__(self, iterations=100, noise=0):

        # Game Entities Positions Storage
        self.food_positions = []
        self.ghost_positions = []
        self.capsule_positions = []
        self.wall_positions = []
        self.danger_zones = []
        self.pacman_position = None

        # Initialisation of map dimensions
        self.map_width = None
        self.map_height = None
        self.rewards = dict()
        self.iterations = iterations

        self.values = util.Counter()
        self.noise = noise

    def registerInitialState(self, state):
        self.corners = api.get_corners(state)
        self.map_width = max(self.corners)[0] + 1
        self.map_height = max(self.corners)[1] + 1

        self.__update_position_rewards(api.get_blank(state), self.BLANK_REWARD)
        self.__update_position_rewards(api.get_walls(state), self.WALL_REWARD)

        self.value_iteration(state)

    def final(self, state):
        print("The game is over!")

    def value_iteration(self, game_state):

        theta = 0.001
        delta = 0

        for k in range(self.iterations):
            new_q_values = self.values.copy()
            for cell in new_q_values.keys():
                action = self.__compute_action_from_values(game_state, cell)
                q_value = self.__compute_q_value_from_values(cell, action, game_state)
                new_q_values[cell] = q_value
                delta = max(delta, abs(self.values[cell] - q_value))

            self.values = new_q_values
            if delta < theta:
                return k

    def __compute_action_from_values(self, game_state, cell):
        """
        La policy è l'azione migliore nel dato stato
        in base ai valori attualmente memorizzati in self.values.

        Puoi rompere le tie in qualsiasi modo ritieni opportuno. Nota che se
        non ci sono azioni legali, che è il caso dello stato terminale, dovresti restituire None.
        """

        """
        if self.mdp.isTerminal(state):
            return None

        qValues = util.Counter()
        actions = self.mdp.getPossibleActions(state)

        for action in actions:
            qValues[action] = self.computeQValueFromValues(state, action)

        # bestAction = qValues.argMax()
        # return bestAction
        # return max(qValues, key=qValues.get)
        return max(qValues, key=lambda x: qValues[x])
        """

        q_values = util.Counter()
        legal_actions = self.__get_possible_actions(game_state)
        legal_actions.remove(Directions.STOP)

        for action in legal_actions:
            q_values[action] = self.__compute_q_value_from_values(
                cell, action, game_state
            )

        return max(q_values, key=lambda x: q_values[x])

    def __get_possible_actions(self, game_state):
        """
        Restituisce le azioni possibili.
        """
        return api.legalActions(game_state)

    def __compute_q_value_from_values(self, cell, action, state):
        """
        Calcola il valore Q dell'azione nello stato dalla
        funzione di valore memorizzata in self.values.
        """

        """
           qValue = 0
        for nextState, prob in self.mdp.getTransitionStatesAndProbs(state, action):
            reward = self.mdp.getReward(state, action, nextState)
            qValue += prob * (reward + self.discount * self.getValue(nextState))

        return qValue
        """
        q_value = 0
        reward = self.__get_rewards(state)

        for next_cell, prob in self.__get_transition_states_and_probs(
            cell, action, state
        ):
            reward = self.rewards[next_cell]
            q_value += prob * (reward + self.DISCOUNT_FACTOR * self.values[next_cell])

        return q_value

    def __get_transition_states_and_probs(self, cell, action, state):
        # if action == Directions.STOP:
        #    return [(cell, 1.0)]

        directions = {
            Directions.NORTH: (0, 1),
            Directions.SOUTH: (0, -1),
            Directions.EAST: (1, 0),
            Directions.WEST: (-1, 0),
        }

        secondary_directions = {
            Directions.NORTH: [Directions.EAST, Directions.WEST],
            Directions.SOUTH: [Directions.EAST, Directions.WEST],
            Directions.EAST: [Directions.NORTH, Directions.SOUTH],
            Directions.WEST: [Directions.NORTH, Directions.SOUTH],
        }

        # Calculate primary move based on action
        print("action", action)
        dx, dy = directions[action]
        x, y = cell
        primary_cell = (
            (x + dx, y + dy) if self.__isAllowed((x + dx, y + dy), state) else cell
        )
        print("primary cell", primary_cell, "cell", cell)

        # Initialize successors with primary move if allowed
        successors = [(primary_cell, 1 - self.noise)]

        # Calculate secondary moves (all other directions with accidental probability)
        for secondary_action in secondary_directions[action]:
            dx, dy = directions[secondary_action]
            secondary_cell = (
                (x + dx, y + dy) if self.__isAllowed((x + dx, y + dy), state) else cell
            )
            print("secondary cell", secondary_cell)
            successors.append((secondary_cell, self.noise / 2.0))

        return self.__aggregate(successors)

    def __aggregate(self, successors):
        counter = util.Counter()
        for state, prob in successors:
            counter[state] += prob
        return list(counter.items())

    def __isAllowed(self, cell, state):
        x, y = cell
        if not (0 <= x < self.map_width and 0 <= y < self.map_height):
            return False
        return not state.data.layout.isWall(cell)

    def __get_rewards(self, state):

        self.food_positions = api.get_food(state)
        self.ghost_positions = api.get_ghosts(state)
        self.capsule_positions = api.get_capsules(state)
        self.wall_positions = api.get_walls(state)
        self.blank_positions = api.get_blank(
            self.food_positions,
            self.ghost_positions,
            self.capsule_positions,
            self.wall_positions,
            self.rewards,
        )
        self.pacman_position = api.whereAmI(state)
        self.danger_zones = api.get_danger_zones(
            state,
            self.pacman_position,
            self.ghost_positions,
            self.map_width,
            self.map_height,
            self.SAFETY_DISTANCE,
        )

        self.__update_rewards(state)

    def __update_rewards(self, state):
        self.__update_position_rewards(self.blank_positions, self.BLANK_REWARD)
        self.__update_position_rewards(self.food_positions, self.FOOD_REWARD)
        self.__update_position_rewards(self.capsule_positions, self.CAPSULE_REWARD)
        self.__update_position_rewards(self.wall_positions, self.WALL_REWARD)
        self.__update_ghost_and_danger_rewards(state)

    def __update_position_rewards(self, positions, reward):
        self.rewards.update({pos: reward for pos in positions})

    def __update_ghost_and_danger_rewards(self, state):
        ghost_reward, danger_reward = api.calculate_ghost_and_danger_zone_rewards(
            state, self.GHOST_REWARD, self.DANGER_ZONE_REWARD
        )

        self.rewards.update({zone: danger_reward for zone in self.danger_zones})
        self.rewards.update({ghost: ghost_reward for ghost in self.ghost_positions})

    def getPolicy(self, game_state, cell):
        return self.__compute_action_from_values(game_state, cell)

    def __get_best_policy(self, state):
        self.__get_rewards(state)
        current_position = api.whereAmI(state)
        return self.__compute_action_from_values(state, current_position)

    def getAction(self, state):
        best_action = self.__get_best_policy(state)
        return api.makeMove(best_action, api.legalActions(state))

        # return self.__compute_action_from_values(game_state, cell)

    def getQValue(self, cell, action, state):
        return self.__compute_q_value_from_values(cell, action, state)
