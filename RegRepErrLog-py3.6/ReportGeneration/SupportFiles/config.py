#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# Module handles reading the configuration file

from yaml import load
import os
import logging

# Global variables accessed by other modules
# ALM
almUrl = ""

# Transaction Details and SLA
transactions = {}

# Test Cases to execute
testCases = ""

# Teams Connection
teamsUrl = ""

# Teams result long/short
teamsResult = ""

# Output File Location
fileLoc = ""

# Log File Location
logLoc = ""

# Log level
logLevel = ""

logger = logging.getLogger('rr.sf.config')
# Input Arguments: None
# Output Arguments: None
# Function: Reads the yaml formatted configuration and assigns the appropriate values to the global variables.
def fetchfromconfig():
    global almUrl, transactions, testCases, teamsUrl, fileLoc, logLoc, logLevel, teamsResult
    currdir = os.getcwd()
    with open(currdir + "\\rrconfig.yml", "r") as ymlfile:
        cfg = load(ymlfile)

    if not cfg:
        logger.error('Config file not present or not parsed. Check config location.')
    else:
        logger.debug('Config file parsed successfully')
        almUrl = cfg['almurl']
        transactions = cfg['transactions']
        testCases = ",".join(map(str, cfg['testcases']))
        teamsUrl = cfg['teamsurl']
        teamsResult = cfg['teamsResult']
        fileLoc = cfg['fileloc']
        logLoc = cfg['logLoc']
        logLevel = cfg['logLevel']


