# main.py
"""
Module for interactively running a 2D robot on a tabletop.

The user can enter commands in the standard input to move the robot.

Author: Sönke Niemann
Email: soenke.niemann@gmail.com
Date: 2025-05-16
"""

import logging

from robot import Robot


logging.basicConfig(
    level=logging.INFO,
    format='[%(asctime)s - %(levelname)s - %(module)s:%(lineno)d] %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('toy_robot_simulator.log')
    ]
)


if __name__ == "__main__":
    logging.info("Welcome to Toy Robot Simulator!")
    logging.info("The user can place a 2D robot with a 1x1 footprint on a 5x5 table top "
                 "and move it around.")
    logging.info("Remember that before the robot can be moved, it has to be placed on "
                 "the table first. ")
    logging.info("Please note that the tabletop's X-axis points EAST, "
                 "the Y-axis points NORTH. ")
    logging.info("Good Luck!")

    r = Robot()
    r.print_help()
    r.draw_map()

    try:
        while True:
            logging.info("Please enter your command: ")
            input_str = input()
            verb, params = r.parse_command_input(input_str)
            r.execute_parsed_command(verb, params)
    except KeyboardInterrupt:
        logging.info("Application stopped by user.")
