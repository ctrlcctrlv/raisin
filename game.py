#!/usr/bin/env python
# -*- coding: utf-8 -*-

import random

# Last rolls
# last_rolls['user'] = [last_roll]
last_rolls = {}

# Roll and store in rolls log
def roll_dice(user):
    roll = random.randint(1, 6)
    last_rolls[user] = roll
    return roll

# Show last roll of user
def last_roll(user):
    return last_rolls[user]
