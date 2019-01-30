#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# The module encapsulates the functions written in all the other modules. This module primarily acts as the
# presentation layer. Generation of results and writing to the specified outputs and other operations required to
# achieve them are written in this module.

import os
import sys
from pathlib import Path
from threading import Thread
from numpy import percentile
from ReportGeneration.SupportFiles.ALMOperations import almOperations
from ReportGeneration.SupportFiles.ProcessReports import processReports
from ReportGeneration.SupportFiles.GenerateHTML import postTeams
import ReportGeneration.SupportFiles.config as cnf
import logging
from datetime import datetime

# Global Variables:
# posResult - Holds all the ingredients that is required to obtain the output
# rawResults - Dictionary to hold the individual results obtained from processing each of the html report
# runList - Holds the run ids, in case the user chooses to provide the test case names as the input
posResult = {'almUrl': '', 'userName': '', 'password': '', 'runIdList': [],
             'outputLoc': '', 'testCaseList': [], 'hostname': '', 'iterations': 1}
rawResults = {}
runList = []
runStatus = {}

logger = logging.getLogger('rr.posresult')
# Input Arguments: argv
# Output Arguments: opts
# Function: Captures all the inputs that are provided through command line.
def processSysArgs(argv):
    opts = {}
    while argv:
        if argv[0][0] == '-':
            opts[argv[0]] = argv[1]
        argv = argv[1:]
    return opts


# Input Arguments: None
# Output Arguments: None
# Function: Generates the output results as a csv or sends the output to teams.
def createPosResult():
    global runList
    logger.debug('Start fetching configuration!')
    logger.debug('Configuration fetch completed.')
    posResult['almUrl'] = cnf.almUrl
    posResult['testCaseList'] = cnf.testCases.split(",")
    logger.debug('Start reading the command line arguments.')

    try:
        opts = processSysArgs(sys.argv)
        posResult['userName'] = opts['-u']
        posResult['password'] = opts['-p']
        posResult['outputLoc'] = opts['-o']
        posResult['hostname'] = opts['-h']
        posResult['iterations'] = int(opts['-i'])
        if '-r' in opts.keys():
            posResult['runIdList'] = opts['-r'].split(",")
        logger.debug('Successfully read the command line arguments.')
    except IndexError:
        logger.error('Error occurred while reading command line arguments.')
        logger.error('The following arguments are mandatory -\n'
                     '-u <almusername> -p <almpassword> -o file/teams'
                     '-h <hostname> -i <number of iterations to consider>')
        sys.exit(1)
    except ValueError:
        logger.error('The command line arguments are not in the right format')
        logger.error('The following arguments are mandatory -\n'
                     '-u <string> -p <string> -o file/teams'
                     '-h <string> -i <character>')
        sys.exit(1)
    except AttributeError:
        logger.error('The command line arguments are not in the right type')
        logger.error('The following arguments are mandatory -\n'
                     '-u <string> -p <string> -o file/teams'
                     '-h <string> -i <character>')
        sys.exit(1)

    try:
        almObj = almOperations(posResult['almUrl'], posResult['userName'], posResult['password'])
        logger.info('Start ALM Connection.')
        almSession = almObj.almLogin()
    except ValueError:
        logger.error('An error occurred while securing a connection to ALM.')
        sys.exit(1)

    processedResult = {}
    try:
        if len(posResult['runIdList']) < 1:
            logger.info('Fetching the run id list based on the test case names in configuration.')
            testidthreads = []
            logger.debug('Starting threads to fetch the run ids for each test case based on the iterations requested.')
            for testcase in posResult['testCaseList']:
                datalist = [almSession, posResult['hostname'], posResult['iterations']]
                t = Thread(target=threadTest, args=(datalist, testcase))
                t.start()
                testidthreads.append(t)
            for thread in testidthreads:
                thread.join()
            posResult['runIdList'] = runList
        else:
            logger.info('Ignoring the test case names as specific run id list provided for processing.')
            runList = posResult['runIdList']
        threads = []
        logger.debug('Starting threads to fetch response time of each run id.')
        for runId in runList:
            almSession = almSession.almSession()
            details = almSession.fetchStatusNameByRunId(runId)
            runStatus[runId] = [details[2], details[3]]
            if details[3] == 'Passed':
                t = Thread(target=threadProcess, args=(almSession, runId))
                t.start()
                threads.append(t)
        for thread in threads:
            thread.join()
        processedResult = processRawResults(rawResults)
        logger.info('Successfully processed the data received.')
    except ValueError:
        logger.error('Data returned after processing the results are incorrect.')
        sys.exit(1)
    except IOError:
        logger.error('An error occurred while processing the results from html report.')
        sys.exit(1)

    if posResult['outputLoc'] == 'teams':
        logger.info('Sent the results to teams channel.')
        postTeams(updateKeys(processedResult), posResult['hostname'], runStatus)
    elif posResult['outputLoc'] == 'file':
        logger.info('Sent the results to the output file.')
        createOutputFile(updateKeys(processedResult))
    elif posResult['outputLoc'] == 'tf':
        logger.info('Sent the results to the output file.')
        createOutputFile(updateKeys(processedResult))
        logger.info('Sent the results to teams channel.')
        postTeams(updateKeys(processedResult), posResult['hostname'], runStatus)



# Input Arguments: almSess, runId
# Output Arguments: None
# Function: The call takes the valid alm session and run id and fetches the html report from ALM, processes the data
#           and adds to the global raw results dictionary the result captured. The function is executed by multiple
#           threads in parallel depending on the number of test cases/run ids that were provided at input.
def threadProcess(almSess, runId):
    global rawResults
    objProcess = processReports(almSess, runId)
    objProcess.almObj.almSession()
    objProcess.fetchRawDataByReport()
    rawResults = objProcess.combineRawResults(rawResults)


# Input Arguments: datlist, testName
# Output Arguments: None
# Function: The call takes in the alm session, the store number and the test case name and fetches the corresponding
#           run id of the latest run of the test case from ALM. This run id is then added to the global runList
#           variable
def threadTest(datlist, testName):
    global runList
    objProcess = processReports(datlist[0])
    objProcess.almObj.almSession()
    val = objProcess.fetchRunIdByTestCase(datlist[1], testName, datlist[2])
    if isinstance(val, str):
        runList.append(val)
    else:
        runList.extend(val)


# Input Arguments: rwResult
# Output Arguments: processedResult
# Function: The raw data fetched from each html reports are processed to find the average, 95th percentile and the
#           total count of occurrences for each transaction.
def processRawResults(rwResult):
    processedResult = {}
    for key in rwResult:
        count = len(rwResult[key])
        average = round(sum(rwResult[key]) / count, 3)
        perc95 = round(percentile(rwResult[key], 95), 3)
        processed = [count, average, perc95]
        processedResult[key] = processed
    return processedResult


# Input Arguments: fileName
# Output Arguments: boolean
# Function: Checks the presence of the csv file.
def checkOutputFilePresent(fileName):
    outputFile = Path(fileName + "\\outResult.csv")
    return outputFile.is_file()


# Input Arguments: processResult
# Output Arguments: None
# Function: Takes in the dictionary containing the processed results and writes the contents in to a csv file.
def createOutputFile(processResult):
    fileName = 'outResult_' + posResult['hostname'] + '_' + datetime.today().strftime('%Y_%m_%dT%H%M%S') +'.csv'

    try:
        if checkOutputFilePresent(cnf.fileLoc):
            logger.debug('Removing the existing output file.')
            os.remove(cnf.fileLoc + '\\' + fileName)

        csvfile = open(cnf.fileLoc + '\\' + fileName, 'a')
        logger.debug('Successfully created and opened the output file to write results.')
        csvfile.write("Host Register:" + posResult['hostname'] + '\n')
        csvfile.write("Transaction Name" + "," + "Count" + "," + "Average Response Time" + "," + "95th Percentile" + '\n')
        for key, value in processResult.items():
            csvfile.write(str(key) + "," + ','.join(str(e) for e in value) + '\n')
        csvfile.write("\n")
        csvfile.write("Status of the latest run:")
        csvfile.write("Run ID" + "," + "Test Name" + "," + "Status" + "\n")
        for key, value in runStatus.items():
            csvfile.write(str(key) + "," + ','.join(str(e) for e in value) + '\n')
        csvfile.write("\n")
    except IOError:
        logger.error('An error occurred in writing the report to the csv.')
        sys.exit(1)


# Input Arguments: rawResults
# Output Arguments: workRes
# Function: Maps the transaction names in the html report to the actual ones sent to the clients.
def updateKeys(rawResults):
    transactionNames = {'POSLaunch': 'POS_Launch', 'POS_Associate_Entry': 'POS_AssociateEntry',
                        'POS_Item_Entry': 'POS_AddItem', 'POS_FirstTotal': 'POS_ItemAmountCalc',
                        'POS_SecondTotal': 'POS_TotalAmountCalc', 'POS_TenderType': 'POS_SelectModeofPayment',
                        'POS_AmountEnteredCASH': 'POS_CashPayment',
                        'POS_AmountEnteredDISCOVER': 'POS_DiscoverCardPayment',
                        'POS_AmountEnteredPLCC': 'POS_PLCCPayment',
                        'POS_AmountEnteredDUAL CARD': 'POS_DualCardPayment',
                        'POS_Print_Receipt': 'POS_PrintReceipt'}
    workRes = {}
    for key in rawResults:
        if key in transactionNames.keys():
            workRes[transactionNames[key]] = rawResults[key]
        else:
            workRes[key] = rawResults[key]
    logger.debug('Successfully mapped the transaction names according to convention.')
    return workRes

