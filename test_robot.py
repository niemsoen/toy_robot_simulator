# test_robot.py
"""
Module for testing the module robot.py.

The tests can be run from this workdir with 'pytest'.

Author: Sönke Niemann
Email: soenke.niemann@gmail.com
Date: 2025-05-16
"""

from typing import List

from robot import Robot


def exec_robot_commands(commands: List[str]) -> str:
    """Execute commands on the robot to test the output.

    Args:
        commands (List[str]): sequence of commands

    Returns:
        str: output of the robot
    """
    r = Robot()
    output = ""
    for c in commands:
        verb, params = r.parse_command_input(c)
        output = r.execute_parsed_command(verb, params)
    return output


def test_example_case_a():
    """Test example case A from the task."""
    commands = [
        "PLACE 0,0,NORTH",
        "MOVE",
        "REPORT"
    ]
    output_wanted = "0,1,NORTH"
    assert output_wanted == exec_robot_commands(commands)


def test_example_case_b():
    """Test example case B from the task."""
    commands = [
        "PLACE 0,0,NORTH",
        "LEFT",
        "REPORT"
    ]
    output_wanted = "0,0,WEST"
    assert output_wanted == exec_robot_commands(commands)


def test_example_case_c():
    """Test example case C from the task."""
    commands = [
        "PLACE 1,2,EAST",
        "MOVE",
        "MOVE",
        "LEFT",
        "MOVE",
        "REPORT"
    ]
    output_wanted = "3,3,NORTH"
    assert output_wanted == exec_robot_commands(commands)


def test_place():
    """Test that placing results in the correct position and heading of the robot."""
    commands = [
        "PLACE 3,2,NORTH",
        "REPORT"
    ]
    output_wanted = "3,2,NORTH"
    assert output_wanted == exec_robot_commands(commands)


def test_forget_place():
    """Test that placing is required before any other command is issued."""
    commands = [
        "MOVE",
        "MOVE",
        "LEFT",
        "MOVE",
        "REPORT"
    ]
    output_wanted = "Error: please first issue a in-bounds PLACE command"
    assert output_wanted == exec_robot_commands(commands)


def test_place_override():
    """Test that a second place operation overrides the state of the robot."""
    commands = [
        "MOVE",
        "MOVE",
        "LEFT",
        "PLACE 1,2,EAST",
        "MOVE",
        "REPORT",
        "PLACE 1,2,EAST",
        "REPORT"
    ]
    output_wanted = "1,2,EAST"
    assert output_wanted == exec_robot_commands(commands)


def test_move():
    """Test that the robot moves by one unit in the direction of heading."""
    commands = [
        "PLACE 3,2,NORTH",
        "MOVE",
        "REPORT"
    ]
    output_wanted = "3,3,NORTH"
    assert output_wanted == exec_robot_commands(commands)


def test_left():
    """Test that turning left from NORTH yields WEST and doesn't change position."""
    commands = [
        "PLACE 3,2,NORTH",
        "LEFT",
        "REPORT"
    ]
    output_wanted = "3,2,WEST"
    assert output_wanted == exec_robot_commands(commands)


def test_right():
    """Test that turning right from SOUTH yields WEST and doesn't change position."""
    commands = [
        "PLACE 3,2,SOUTH",
        "RIGHT",
        "REPORT"
    ]
    output_wanted = "3,2,WEST"
    assert output_wanted == exec_robot_commands(commands)


def test_not_moving_out_of_bounds():
    """Test that the robot doesn't move out of bounds."""
    commands = [
        "PLACE 1,2,EAST",
        "MOVE",
        "MOVE",
        "MOVE",
        "MOVE",
        "MOVE",
        "REPORT"
    ]
    output_wanted = "4,2,EAST"
    assert output_wanted == exec_robot_commands(commands)


def test_complex_move():
    """Test correct result of a complex sequence of commands."""
    commands = [
        "PLACE 3,3,NORTH",
        "MOVE",
        "LEFT",
        "MOVE",
        "LEFT",
        "MOVE",
        "RIGHT",
        "LEFT",
        "LEFT",
        "MOVE",
        "REPORT"
    ]
    output_wanted = "3,3,EAST"
    assert output_wanted == exec_robot_commands(commands)


def test_not_placing_out_of_bounds():
    """Test that the robot can't be placed out of bounds of the tabletop."""
    commands = [
        "PLACE -1,7,EAST",
        "REPORT"
    ]
    output_wanted = "Error: please first issue a in-bounds PLACE command"
    assert output_wanted == exec_robot_commands(commands)


def test_wrong_input_1():
    """Test that a command with missing space between command verb and parameters is ignored."""
    commands = [
        "PLACE1,2,EAST",
        "REPORT"
    ]
    output_wanted = "Error: please first issue a in-bounds PLACE command"
    assert output_wanted == exec_robot_commands(commands)


def test_wrong_input_2():
    """Test that a command with spaces instead of commas between parameters is ignored."""
    commands = [
        "PLACE 1 2 EAST",
        "REPORT"
    ]
    output_wanted = "Error: please first issue a in-bounds PLACE command"
    assert output_wanted == exec_robot_commands(commands)


def test_wrong_input_3():
    """Test that a command with float instead of int as parameters is ignored."""
    commands = [
        "PLACE 1.0,2.0,EAST",
        "REPORT"
    ]
    output_wanted = "Error: please first issue a in-bounds PLACE command"
    assert output_wanted == exec_robot_commands(commands)


def test_wrong_input_recovery():
    """Test that the program continues when a correct command is issued after a malformed."""
    commands = [
        "PLACE 1 2 EAST",
        "PLACE 3,4,WEST",
        "REPORT"
    ]
    output_wanted = "3,4,WEST"
    assert output_wanted == exec_robot_commands(commands)


def test_no_input():
    """Test that nothing happens when an empty command is sent to the robot."""
    commands = []
    output_wanted = ""
    assert output_wanted == exec_robot_commands(commands)
