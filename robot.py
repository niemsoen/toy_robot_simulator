# robot.py
"""
This module defines a 2D tabletop robot and necessary constants.

Author: Sönke Niemann
Email: soenke.niemann@gmail.com
Date: 2025-05-16
"""

import logging
import sys
from typing import Tuple

from scipy.spatial.transform import Rotation as R
import numpy as np


logger = logging.getLogger(__name__)

ROT_LEFT = R.from_euler('xyz', [0, 0, 90], degrees=True)
ROT_RIGHT = R.from_euler('xyz', [0, 0, -90], degrees=True)
TABLE_DIM_MAX = 4
TABLE_DIM_MIN = 0

COMMANDS_AND_ARGS = (
    ("PLACE", (int, int, str)),
    ("MOVE", ()),
    ("LEFT", ()),
    ("RIGHT", ()),
    ("REPORT", ()),
    ("HELP", ()),
    ("EXIT", ()),
)

DIRVECTOR_FROM_COMPASS_DIRECTION = {
    "NORTH" : np.array([0,1,0]),
    "SOUTH" : np.array([0,-1,0]),
    "WEST" : np.array([-1,0,0]),
    "EAST" : np.array([1,0,0])
}

MAPCHAR_FROM_COMPASS_DIRECTION = {
    "NORTH" : "^",
    "SOUTH" : "v",
    "WEST" : "<",
    "EAST" : ">"
}

def get_compass_direction_from_dirvec(dirvec: np.ndarray) -> str:
    """Obtain compass direction from a direction vector.

    Args:
        dirvec (np.ndarray): a 3x1 direction vector

    Returns:
        str: compass direction NORTH, SOUTH, EAST or WEST or ERROR
    """
    if np.shape(np.array([0,0,0])) != np.shape(dirvec):
        logger.error("Invalid shape of input array!")
        return "ERROR"
    if np.isclose(dirvec, np.array([0,1,0])).all():
        return "NORTH"
    if np.isclose(dirvec, np.array([0,-1,0])).all():
        return "SOUTH"
    if np.isclose(dirvec, np.array([-1,0,0])).all():
        return "WEST"
    if np.isclose(dirvec, np.array([1,0,0])).all():
        return "EAST"
    logger.error("Invalid input direction vector.")
    return "ERROR"


class Robot:
    """A 2D Toy Robot that can be placed, moved and rotated on top of a tabletop.
    """

    def __init__(self) -> None:
        self.pos = np.array([0, 0, 0])
        self.heading_vector = np.array([0, 0, 0])
        self.placed = False


    def check_pos_in_bounds(self, pos: np.ndarray) -> bool:
        """Check if input position is in bounds of table.

        Args:
            pos (np.ndarray): 3x1 ndarray (x,y,z)

        Raises:
            ValueError: x-coordinate out of bounds
            ValueError: y-coordinate out of bounds

        Returns:
            bool: whether input position is valid
        """
        try:
            if pos[0] < TABLE_DIM_MIN or pos[0] > TABLE_DIM_MAX:
                raise ValueError(f"X must be between inclusive {TABLE_DIM_MIN} and "
                                 f"{TABLE_DIM_MAX}, demanded X = {pos[0]}")
            if pos[1] < TABLE_DIM_MIN or pos[1] > TABLE_DIM_MAX:
                raise ValueError(f"Y must be between inclusive {TABLE_DIM_MIN} and "
                                 f"{TABLE_DIM_MAX}, demanded Y = {pos[1]}")
        except ValueError as ve:
            logger.error("Error: robot must be within the bounds of the tabletop: %s", ve)
            return False
        return True


    def place(self, x: int, y: int, compass_direction: str) -> bool:
        """Put the toy robot on the table in position X,Y and facing NORTH, SOUTH, EAST or WEST.

        Args:
            x (int): x-coordinate on the table [0-4]
            y (int): y-coordinate on the table [0-4]
            compass_direction (str): NORTH, SOUTH, EAST or WEST

        Returns:
            bool: success
        """
        place_pos = np.array([x, y, 0])
        if not self.check_pos_in_bounds(place_pos):
            return False

        try:
            self.heading_vector = DIRVECTOR_FROM_COMPASS_DIRECTION[compass_direction]
        except KeyError:
            logger.error("Only directions %s are allowed", DIRVECTOR_FROM_COMPASS_DIRECTION.keys())
            return False

        self.pos = place_pos
        self.placed = True
        logger.info("placed robot at X=%i, Y=%i, facing %s ([x,y,z] = %s)",
                    x, y, compass_direction, self.heading_vector)
        return True


    def move(self) -> bool:
        """Move the toy robot one unit forward in the direction it is currently facing.

        Returns:
            bool: success
        """
        if not self.placed:
            logger.error("Error: please first issue a in-bounds PLACE command")
            return False
        new_pos = self.pos + self.heading_vector
        if not self.check_pos_in_bounds(new_pos):
            return False
        self.pos = new_pos
        logger.debug("executed MOVE")
        return True


    def left(self) -> bool:
        """Turn the robot left (anti-clockwise).

        Returns:
            bool: success
        """
        if not self.placed:
            logger.error("Error: please first issue a in-bounds PLACE command")
            return False
        logger.debug("turning LEFT")
        self.heading_vector = ROT_LEFT.apply(self.heading_vector)
        self.heading_vector = np.round(self.heading_vector, 0)
        return True


    def right(self) -> bool:
        """Turn the robot right (clockwise).

        Returns:
            bool: success
        """
        if not self.placed:
            logger.error("Error: please first issue a in-bounds PLACE command")
            return False
        logger.debug("turning RIGHT")
        self.heading_vector = ROT_RIGHT.apply(self.heading_vector)
        self.heading_vector = np.round(self.heading_vector, 0)
        return True


    def report(self) -> str:
        """Report the current robot pose.

        Returns:
            str: current robot pose as X,Y,COMPASS_DIRECTION
        """
        if not self.placed:
            logger.error("Error: please first issue a in-bounds PLACE command")
            return "Error: please first issue a in-bounds PLACE command"
        direction_str = get_compass_direction_from_dirvec(self.heading_vector)
        logger.info("Current robot pose: X = %i, Y = %i, HEADING = %s / %s",
                    self.pos[0], self.pos[1], direction_str, self.heading_vector)
        logger.debug("executed REPORT")
        return f"{int(self.pos[0])},{int(self.pos[1])},{direction_str}"


    def print_help(self):
        """Print a help message with valid commands.
        """
        logger.info("")
        logger.info("Help: valid commands are")
        logger.info("  'PLACE X,Y,F'  places the robot onto the tabletop with coordinates "
                    "X: int, Y: int ")
        logger.info("                 (both [%i-%i]) and orientation "
                    "F: str ('NORTH', 'SOUTH', 'EAST', 'WEST')", TABLE_DIM_MIN, TABLE_DIM_MAX)
        logger.info("  'MOVE'         moves the robot by one unit in the direction it is "
                    "currently facing")
        logger.info("  'LEFT'         rotates the robot by 90 degrees to the left")
        logger.info("  'RIGHT'        rotates the robot by 90 degrees to the right")
        logger.info("  'REPORT'       announces X,Y, and orientation F of the robot")
        logger.info("  'EXIT'         to close this application")
        logger.info("  'HELP'         to print this message")
        logger.info("  Please note that the tabletop's X-axis points EAST, the Y-axis points NORTH")


    def parse_command_input(self, command_str: str) -> Tuple[str, list]:
        """Parse commands into actionable commands for the robot.

        Args:
            command_str (str): command input from the user

        Raises:
            ValueError: Invalid command verb
            ValueError: No Parameters given
            ValueError: No Parameters supported
            ValueError: Not enough paramters

        Returns:
            Tuple[str, list]: parsed command verb and parameter list
        """
        verb_params_split = command_str.split(" ")
        input_has_params = len(verb_params_split) > 1
        found_valid_verb = -1
        try:
            for i, c in enumerate(COMMANDS_AND_ARGS):
                # check that command verb is first
                if not verb_params_split[0] == c[0]:
                    continue
                found_valid_verb = i
                break

            if found_valid_verb == -1:
                raise ValueError(f"'{verb_params_split[0]}' is not a valid command verb. "
                                 "Choose from the list below.")

            verb = COMMANDS_AND_ARGS[found_valid_verb][0]
            valid_param_types = COMMANDS_AND_ARGS[found_valid_verb][1]
            logger.debug("found command verb '%s' which allows param types '%s'",
                         verb, valid_param_types)

            if not input_has_params:
                if len(valid_param_types) > 0:
                    raise ValueError(f"The verb '{verb}' can only be called with "
                                     f"{len(valid_param_types)} parameters {valid_param_types}")
                logger.debug("returning verb '%s' with empty param list '%s'", verb, [])
                return verb, []

            # input has params but none supported by verb
            if len(valid_param_types) == 0:
                raise ValueError(f"The verb '{verb}' does not support parameters")

            # check has correct amount of parameters
            params_found = verb_params_split[1].split(",")
            logger.debug("found command params '%s'", params_found)
            if len(params_found) != len(valid_param_types):
                raise ValueError(f"Wrong amount of comma separated params for verb '{verb}'. "
                                 f"(Found: {len(params_found)}, allowed: {len(valid_param_types)})")

            # check correct type of params
            params_casted = []
            for i, p_type in enumerate(valid_param_types):
                params_casted.append(p_type(params_found[i]))
            logger.debug("returning verb '%s' with parsed params '%s'", verb, params_casted)
            return verb, params_casted

        except ValueError as e:
            logger.error("Invalid command '%s': %s", command_str, e)
            return "error", []

    def execute_parsed_command(self, command_verb: str, params: list) -> str:
        """Execute a former parsed command with given parameters.

        Args:
            command_verb (str): either PLACE, MOVE, LEFT, RIGHT or REPORT
            params (list): currently only applicable for PLACE

        Returns:
            str: report message
        """
        success = None
        match command_verb:
            case "PLACE":
                success = self.place(params[0], params[1], params[2])
            case "MOVE":
                success = self.move()
            case "LEFT":
                success = self.left()
            case "RIGHT":
                success = self.right()
            case "REPORT":
                success = True
                return self.report()
            case "EXIT":
                logger.info("Application stopped by user.")
                sys.exit(0)
            case "HELP":
                success = True
                self.print_help()
            case _:
                logger.warning("Nothing to be executed")
        if not success:
            self.print_help()
        self.draw_map()
        return ""

    def draw_map(self):
        """Draw the current map view of the tabletop.
        """
        logger.debug("drawing map")
        rows = TABLE_DIM_MAX
        cols = TABLE_DIM_MAX
        robot_indicator_char = " "
        if self.placed:
            try:
                robot_indicator_char = MAPCHAR_FROM_COMPASS_DIRECTION[
                    get_compass_direction_from_dirvec(self.heading_vector)]
            except KeyError:
                robot_indicator_char = "O"
            print("\n  # # # # # # #  "
                  "Robot position with heading "
                  "North(^), South (v), West(<), East(>)")
        else:
            print("\n  # # # # # # #  Robot not placed yet")
        for r in range(rows, TABLE_DIM_MIN-1, -1):
            draw_row = f"{r} # "
            for c in range(TABLE_DIM_MIN, cols+1):
                if self.pos[0] == c and self.pos[1] == r:
                    draw_row += f"{robot_indicator_char} "
                else:
                    draw_row += "  "
            draw_row += "#"
            print(draw_row)
        print("Y # # # # # # #")
        print("  X 0 1 2 3 4  \n")
        logger.debug("map drawn succesfully")
