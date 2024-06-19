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
    GHOST_NEIGH = -25
    CAPSULE_REWARD = 15
    BLANK_REWARD = -3
    WALL_REWARD = -10

    SAFETY_DISTANCE = 2
    DISCOUNT_FACTOR = 0.6
    GHOSTBUSTER_MODE = False

    INTENDED_DIRECTION_PROBABILITY = 0.8
    UNINTENDED_DIRECTION_PROBABILITY = 0.1


    def __init__(self,iterations=100):

        # Game Entities Positions Storage
        self.food_position = api.food(state)
        self.ghost_positions =
        self.capsule_positions = []
        self.wall_Positions = []

        # Map dimensions initialisation
        self.map_width = None
        self.map_height = None

        self.iterations = iterations

        self.values = util.Counter()
        self.__value_iteration()

    def __set_map_dimensions(self, state):
        """
        Register the dimensions of the map on start up.

        @param self: the class itself
        @param state: the current game state
        @return None
        """
        corners = api.corners(state)
        return corners[3][0] - corners[0][0] + 1, corners[3][1] - corners[0][1] + 1

    def __initialize_rewards(self):
        """
        Initialize the rewards for each cell in the map.

        @param self: the class itself
        @return None
        """
        return {
            (x, y): self.BLANK_REWARD
            for x in range(self.map_width)
            for y in range(self.map_height)
        }

    def registerInitialState(self, state):
        print("Round " + str(self.__round) + " running...")

        self.map_width, self.map_height = self.__set_map_dimensions(state)
        self.Rewards = self.__initialize_rewards()

    """
    Reset internal memories and log record at the end of each round

    @param self: the class itself
    @param state: the current game state
    @param log_mode: (optional) a boolean value to indicate whether the log mode is active; the default value is false
    @return None
    """

    def final(self, state):
        print("The game is over!")

    def __mapping_operation(self, state, debug_mode):
        # first step of each round: populate internal memories
        if self.__states == None:
            self.__states = []
        if self.__capsules == None:
            self.__capsules = set(api.capsules(state))
        if self.__foods == None:
            self.__foods = set(api.food(state))
        if self.__walls == None:
            self.__walls = api.walls(state)
        if self.__corners == None:
            self.__corners = api.corners(state)

            for i in range(len(self.__corners)):
                x = self.__corners[i][0]
                y = self.__corners[i][1]
                if x == 0:
                    x += 1
                else:
                    x -= 1
                if y == 0:
                    y += 1
                else:
                    y -= 1
                self.__corners[i] = (x, y)

        if self.__floors == None:
            self.__floors = []
            x_coordinates = []
            y_coordinates = []
            for wall in self.__walls:
                x_coordinates.append(wall[0])
                y_coordinates.append(wall[1])
            x_minimum, x_maximum = min(x_coordinates), max(x_coordinates)
            y_minimum, y_maximum = min(y_coordinates), max(y_coordinates)
            for x in range(x_minimum, x_maximum + 1):
                for y in range(y_minimum, y_maximum + 1):
                    if (x, y) not in self.__walls:
                        self.__floors.append((x, y))
        if self.__neighbors == None:
            self.__neighbors = dict()
            # displacements: [East, West, North, South]
            displacements = {
                (1, 0): Directions.EAST,
                (-1, 0): Directions.WEST,
                (0, 1): Directions.NORTH,
                (0, -1): Directions.SOUTH,
            }
            for floor in self.__floors:
                self.__neighbors[floor] = dict()
                for displacement, direction in displacements.items():
                    neighbor = (floor[0] + displacement[0], floor[1] + displacement[1])
                    self.__neighbors[floor][direction] = neighbor
        # log game state history
        self.__states.append(state)
        # the location of agent
        agent_location = api.whereAmI(state)
        # this location won't have capsule any more in the future
        if agent_location in self.__capsules:
            self.__capsules.remove(agent_location)
        # this location won't have food any more in the future
        if agent_location in self.__foods:
            self.__foods.remove(agent_location)
        # if at a corner: set the target corner to another one
        if agent_location in self.__corners:
            self.__counter = self.__corners.index(agent_location)
            self.__counter += random.choice([1, 2, 3])

    """
    Initialize data structures of rewards and utilities for value iteration on Bellman's Equation

    @param self: the class itself
    @param targets: a set of locations of targets
    @param target_value: a tuple of (1) target identifier, and (2) reward value
    @param walls: a list of locations of walls
    @param floors: a list of locations of floors (free spaces)
    @param ghosts: a list of locations of ghosts
    @param safety_distance: (optional) the range of the early warning system; the default value is 4
    @param threat_decay_rate: (optional) the decay rate of negative threat utility initialized to spaces surrounding a ghost; the default value is 50.0
    @return
    """

    def __initialize_data_structures(
        self,
        targets,
        target_value,
        walls,
        floors,
        ghosts,
        safety_distance=4,
        threat_decay_rate=50.0,
    ):
        # initialize empty data structures
        rewards = dict()
        utilities = dict()
        # assign 0.0 reward value to each wall
        # assign 0.0 utility value to each wall
        for wall in walls:
            rewards[wall] = self.__WALL
            utilities[wall] = self.__WALL
        # assign 0.0 reward value to each free space
        # assign +10.0 reward value to each target
        # assign 0.0 utility value each floor
        for floor in floors:
            rewards[floor] = self.__FREE
            if floor in targets:
                rewards[floor] = target_value
            utilities[floor] = self.__FREE
        # assign -500.0 reward value to each ghost
        # assign decaying threat reward values recursively to locations surrounding each ghost
        for ghost in ghosts:
            ghost = (int(ghost[0]), int(ghost[1]))
            rewards[ghost] = self.__HOSTILE
            queue = util.Queue()
            queue.push(ghost)
            visited = set([ghost])
            while not queue.isEmpty():
                curr_location = queue.pop()
                if rewards[curr_location][1] >= (
                    self.__HOSTILE[1] + threat_decay_rate * (safety_distance - 1)
                ) or rewards[curr_location][1] >= (0.0 - threat_decay_rate):
                    continue
                displacements = [(1, 0), (-1, 0), (0, 1), (0, -1)]
                for displacement in displacements:
                    next_location = (
                        curr_location[0] + displacement[0],
                        curr_location[1] + displacement[1],
                    )
                    if next_location in walls:
                        continue
                    if next_location in visited:
                        continue
                    if rewards[next_location][1] <= rewards[curr_location][1]:
                        continue
                    rewards[next_location] = (
                        self.__HOSTILE[0],
                        rewards[curr_location][1] + threat_decay_rate,
                    )
                    queue.push(next_location)
                    visited.add(next_location)
        return (rewards, utilities)

    """
    Update expected utilities based on Bellman's Equation (Note: just 1 iteration)

    @param self: the class itself
    @param walls: a list of locations of walls
    @param neighbors: a dictionary that point from a location (key) to its neighbors (value)
    @param utilities: a dictionary that point from a location (key) to its utilities (value)
    @param discount_factor: (optional) the discount factor gamma (range between 0.0 and 1.0) in the Bellman's equation; the default value is 1.0
    @param convergence_tolerance: (optional) the threshold to decide whether the expected utility of each location converges; the default value is 0.0001
    @return
    """

    def __update_utilities(
        self,
        walls,
        neighbors,
        rewards,
        utilities,
        discount_factor=1.0,
        convergence_tolerance=0.0001,
        ignoring_walls=False,
        maximum_mode=True,
    ):
        previous_utilities = copy.deepcopy(utilities)  # old version of utilities
        fully_convergent = True
        total_entropy = 0.0
        for location in utilities.keys():
            if utilities[location][0] == self.__FREE[0]:
                fully_convergent = False
                east_utility = 0.0
                west_utility = 0.0
                north_utility = 0.0
                south_utility = 0.0
                if ignoring_walls:
                    east_utility += (
                        0.8
                        * previous_utilities[neighbors[location][Directions.EAST]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.NORTH]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.SOUTH]][1]
                    )
                    west_utility += (
                        0.8
                        * previous_utilities[neighbors[location][Directions.WEST]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.SOUTH]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.NORTH]][1]
                    )
                    north_utility += (
                        0.8
                        * previous_utilities[neighbors[location][Directions.NORTH]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.WEST]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.EAST]][1]
                    )
                    south_utility += (
                        0.8
                        * previous_utilities[neighbors[location][Directions.SOUTH]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.EAST]][1]
                        + 0.1
                        * previous_utilities[neighbors[location][Directions.WEST]][1]
                    )
                else:
                    """neighbor to the east"""
                    # east
                    if neighbors[location][Directions.EAST] not in walls:
                        east_utility += (
                            0.8
                            * previous_utilities[neighbors[location][Directions.EAST]][
                                1
                            ]
                        )
                    else:
                        east_utility += 0.8 * previous_utilities[location][1]
                    # left of east: north
                    if neighbors[location][Directions.NORTH] not in walls:
                        east_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.NORTH]][
                                1
                            ]
                        )
                    else:
                        east_utility += 0.1 * previous_utilities[location][1]
                    # right of east: south
                    if neighbors[location][Directions.SOUTH] not in walls:
                        east_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.SOUTH]][
                                1
                            ]
                        )
                    else:
                        east_utility += 0.1 * previous_utilities[location][1]
                    """neighbor to the west"""
                    # west
                    if neighbors[location][Directions.WEST] not in walls:
                        west_utility += (
                            0.8
                            * previous_utilities[neighbors[location][Directions.WEST]][
                                1
                            ]
                        )
                    else:
                        west_utility += 0.8 * previous_utilities[location][1]
                    # left of west: south
                    if neighbors[location][Directions.SOUTH] not in walls:
                        west_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.SOUTH]][
                                1
                            ]
                        )
                    else:
                        west_utility += 0.1 * previous_utilities[location][1]
                    # right of west: north
                    if neighbors[location][Directions.NORTH] not in walls:
                        west_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.NORTH]][
                                1
                            ]
                        )
                    else:
                        west_utility += 0.1 * previous_utilities[location][1]
                    """neighbor to the north"""
                    # north
                    if neighbors[location][Directions.NORTH] not in walls:
                        north_utility += (
                            0.8
                            * previous_utilities[neighbors[location][Directions.NORTH]][
                                1
                            ]
                        )
                    else:
                        north_utility += 0.8 * previous_utilities[location][1]
                    # left of north: west
                    if neighbors[location][Directions.WEST] not in walls:
                        north_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.WEST]][
                                1
                            ]
                        )
                    else:
                        north_utility += 0.1 * previous_utilities[location][1]
                    # right of north: east
                    if neighbors[location][Directions.EAST] not in walls:
                        north_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.EAST]][
                                1
                            ]
                        )
                    else:
                        north_utility += 0.1 * previous_utilities[location][1]
                    """neighbor to the south"""
                    # south
                    if neighbors[location][Directions.SOUTH] not in walls:
                        south_utility += (
                            0.8
                            * previous_utilities[neighbors[location][Directions.SOUTH]][
                                1
                            ]
                        )
                    else:
                        south_utility += 0.8 * previous_utilities[location][1]
                    # left of south: east
                    if neighbors[location][Directions.EAST] not in walls:
                        south_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.EAST]][
                                1
                            ]
                        )
                    else:
                        south_utility += 0.1 * previous_utilities[location][1]
                    # right of south: west
                    if neighbors[location][Directions.WEST] not in walls:
                        south_utility += (
                            0.1
                            * previous_utilities[neighbors[location][Directions.WEST]][
                                1
                            ]
                        )
                """update expected utility"""
                if maximum_mode:
                    utilities[location] = (
                        previous_utilities[location][0],
                        rewards[location][1]
                        + discount_factor
                        * max(
                            [east_utility, west_utility, north_utility, south_utility]
                        ),
                    )
                else:
                    utilities[location] = (
                        previous_utilities[location][0],
                        rewards[location][1]
                        + discount_factor
                        * min(
                            [east_utility, west_utility, north_utility, south_utility]
                        ),
                    )
                # if abs(utilities[location][1] - previous_utilities[location][1]) < convergence_tolerance:
                #     utilities[location] = (self.__CONVERGENT[0], utilities[location][1])
                total_entropy += abs(
                    utilities[location][1] - previous_utilities[location][1]
                )
            if total_entropy < convergence_tolerance:
                fully_convergent = True
        return (utilities, fully_convergent, total_entropy)

    """
    Print the data structure of utilities or rewards in a user-friendly grid display

    @param self: the class itself
    @param walls: a list of locations of walls
    @param grid: a dictionary that point from a location (key) to its reward or utility (value)
    @return None
    """

    def __print_data_structure(self, walls, grid):
        x_coordinates = []
        y_coordinates = []
        for wall in walls:
            x_coordinates.append(wall[0])
            y_coordinates.append(wall[1])
        x_minimum, x_maximum = min(x_coordinates), max(x_coordinates)
        y_minimum, y_maximum = min(x_coordinates), max(y_coordinates)
        for y in range(y_maximum, y_minimum - 1, -1):
            line = "{:4s}:".format("y=" + str(y))
            for x in range(x_minimum, x_maximum + 1, 1):
                grid_value = grid[(x, y)]
                line += "({:2s},{:>13s})".format(
                    grid_value[0], "{:+9.3f}".format(grid_value[1])
                )
            print(line)
        x_axis = "     "
        for x in range(x_minimum, x_maximum + 1, 1):
            x_axis += "{:18s}".format(" x=" + str(x))
        print(x_axis)

    """
    Value iteration of Markov Decision Process

    @param self: the class itself
    @param state: the current game state
    @param debug_mode: a boolean value to indicate whether the debug mode is active
    @param ghostbuster_mode: (optional) a string to indicate which ghostbuster mode (inactive/defensive/offensive) is in use; the default value is inactive
    @return None
    """

    def __value_iteration(self, state, debug_mode, deep_debug_mode, ghostbuster_mode):

        theta = 0.001
        delta = 0
    
        for k in range(self.iterations):
            newQValues = self.values.copy()
            for state in self

        # -------------------------
        """initialize data structures for value iteration"""
        ghosts_states = api.ghostStates(state)
        edible_ghosts = []
        hostile_ghosts = []
        early_stopping_point = self.__NORMAL_EARLY_STOPPING_POINT
        for ghost_state in ghosts_states:
            if ghost_state[1] == 1:
                edible_ghosts.append((int(ghost_state[0][0]), int(ghost_state[0][1])))
            else:
                hostile_ghosts.append(ghost_state[0])
        if debug_mode:
            print("\tedible_ghosts=" + str(edible_ghosts))
            print("\thostile_ghosts=" + str(hostile_ghosts))
        # inactive ghostbuster mode
        self.__rewards, self.__utilities = self.__initialize_data_structures(
            self.__foods,
            self.__FOOD,
            self.__walls,
            self.__floors,
            hostile_ghosts,
            safety_distance=self.__SAFETY_DISTANCE,
            threat_decay_rate=self.__THREAT_DECAY_RATE,
        )
        early_stopping_point = self.__NORMAL_EARLY_STOPPING_POINT
        if len(self.__foods) < 10:
            early_stopping_point = self.__SPARSE_EARLY_STOPPING_POINT
        # defensive ghostbuster mode
        if ghostbuster_mode == self.__DEFENSIVE_GHOSTBUSTER_MODE:
            if len(edible_ghosts) > 0:
                self.__rewards, self.__utilities = self.__initialize_data_structures(
                    edible_ghosts,
                    self.__EDIBLE,
                    self.__walls,
                    self.__floors,
                    hostile_ghosts,
                    safety_distance=self.__SAFETY_DISTANCE,
                    threat_decay_rate=self.__THREAT_DECAY_RATE,
                )
                early_stopping_point = self.__SPARSE_EARLY_STOPPING_POINT
        # offensive ghostbuster_mode
        if ghostbuster_mode == self.__OFFENSIVE_GHOSTBUSTER_MODE:
            if len(edible_ghosts) > 0:
                self.__rewards, self.__utilities = self.__initialize_data_structures(
                    edible_ghosts,
                    self.__EDIBLE,
                    self.__walls,
                    self.__floors,
                    hostile_ghosts,
                    safety_distance=self.__SAFETY_DISTANCE,
                    threat_decay_rate=self.__THREAT_DECAY_RATE,
                )
                early_stopping_point = self.__SPARSE_EARLY_STOPPING_POINT
            elif len(self.__capsules) > 0:
                self.__rewards, self.__utilities = self.__initialize_data_structures(
                    self.__capsules,
                    self.__CAPSULE,
                    self.__walls,
                    self.__floors,
                    hostile_ghosts,
                    safety_distance=self.__SAFETY_DISTANCE,
                    threat_decay_rate=self.__THREAT_DECAY_RATE,
                )
                early_stopping_point = self.__SPARSE_EARLY_STOPPING_POINT
        """use value iteration to update utilites until convergence or early stopping point"""
        stopping_point = None
        for i in range(early_stopping_point):
            stopping_point = i + 1
            self.__utilities, fully_convergent, total_entropy = self.__update_utilities(
                self.__walls,
                self.__neighbors,
                self.__rewards,
                self.__utilities,
                discount_factor=self.__DISCOUNT_FACTOR,
                convergence_tolerance=self.__CONVERGENCE_TOLERANCE,
                ignoring_walls=False,
                maximum_mode=True,
            )
            if deep_debug_mode:
                self.__print_data_structure(self.__walls, self.__rewards)
                self.__print_data_structure(self.__walls, self.__utilities)
                print("\ttotal_entropy=" + "{:+10.3f}".format(total_entropy))
            if fully_convergent:
                break
        if debug_mode:
            self.__print_data_structure(self.__walls, self.__rewards)
            self.__print_data_structure(self.__walls, self.__utilities)
            print("\ttotal_entropy=" + "{:+10.3f}".format(total_entropy))
            print("\tstopping_point=" + str(stopping_point))

    """
    Use maximum expected utility to decide which direction to go next

    @param self: the class itself
    @param state: the current game state
    @param debug_mode: a boolean value to indicate whether the debug mode is active
    @return the direction towards the neighbor location with maximum expected utility
    """

    def __maximum_expected_utility(self, state, debug_mode):
        # the location of agent
        agent_location = api.whereAmI(state)
        if debug_mode:
            print("\tagent_location=" + str(agent_location))
        # discover the legal actions
        legal = api.legalActions(state)
        # remove STOP to increase mobility
        legal.remove(Directions.STOP)
        # decide next move based on maximum expected utility
        action, maximum_expected_utility = None, None
        for direction in legal:
            utility = self.__utilities[self.__neighbors[agent_location][direction]][1]
            if action == None or maximum_expected_utility == None:
                action = direction
                maximum_expected_utility = utility
            expected_utility = utility
            if debug_mode:
                print(
                    "\tdirection="
                    + str(direction)
                    + "\texpected_utility="
                    + str(expected_utility)
                )
            if expected_utility > maximum_expected_utility:
                action = direction
                maximum_expected_utility = expected_utility
        if debug_mode:
            print("\taction=" + str(action))
        return action

    """
    Decide which direction to go based on the current game state

    @param self: the class itself
    @param state: the current game state
    @param debug_mode: (optional) a boolean value to indicate whether the debug mode is active; the default value is false
    @return the direction the agent decides to go (non-deterministic)
    """

    def getAction(self, state, debug_mode=False, deep_debug_mode=False):
        """mapping operation"""
        self.__mapping_operation(state, debug_mode=debug_mode)
        """value iteration"""
        self.__value_iteration(
            state,
            debug_mode=debug_mode,
            deep_debug_mode=deep_debug_mode,
            ghostbuster_mode=self.__GHOSTBUSTER_MODE,
        )
        """maximum expected utility"""
        meu_action = self.__maximum_expected_utility(state, debug_mode=debug_mode)
        """step-by-step demo"""
        if deep_debug_mode:
            breaker = raw_input()
        return api.makeMove(meu_action, api.legalActions(state))
