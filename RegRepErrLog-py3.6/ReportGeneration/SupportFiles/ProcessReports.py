#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# Module handles all the major transformations in creating the final report.

from ReportGeneration.SupportFiles.ProcessHTML import processHtml
import logging
from ReportGeneration.SupportFiles.ALMOperations import almOperations


class processReports:
    rwResult = {}
    runId = ''
    almUrl = ''
    userName = ''
    password = ''
    almConn = ''

    def __init__(self, almObj, runId=''):
        self.runId = runId
        self.rwResult = {}
        self.almObj = almObj
        self.logger = logging.getLogger('rr.sf.processreports')

    # Input Arguments: Object (processReports), rawResults
    # Output Arguments: listNoTag
    # Function: Checks for multiple occurrences of the transactions due to multiple iterations in the data from
    #           multiple html reports and then combines them accordingly such that all the transactions during the
    #           test run are captured and their response times are appropriately represented.
    def combineRawResults(self, rawResults):
        if bool(rawResults):
            for slaveKey in self.rwResult.keys():
                for masterKey in list(rawResults.keys()):
                    if masterKey == slaveKey:
                        rawResults[masterKey] = rawResults[masterKey] + self.rwResult[slaveKey]
                        break
                    elif slaveKey not in list(rawResults.keys()):
                        rawResults[slaveKey] = self.rwResult[slaveKey]
            self.logger.debug('The data dictionary rawResults is processed to combine multiple '
                              'occcurrences/iterations of a transaction in a html report.')
        else:
            self.logger.debug('The data dictionary rawResults is empty. '
                              'The data fetched from the html report is copied for an individual thread.')
            rawResults = self.rwResult.copy()
        return rawResults

    # Input Arguments: Object (processReports)
    # Output Arguments: Object (processReports)
    # Function: Fetches the html report, parses the report and processes the data to fetch the transaction list and
    #           response times and updates the object with the processed data as a dictionary.
    def fetchRawDataByReport(self):
        rwResult = {}
        extractedHtml = self.almObj.almFetchReport(self.runId)
        if extractedHtml:
            reportObject = processHtml(extractedHtml)
            trnList = reportObject.transactionList()
            for val in trnList:
                newVal = val.replace(" ", "\ ")
                rwResult[val] = reportObject.responseTimeListByTransaction(newVal)
            self.rwResult = rwResult.copy()
            self.logger.debug('Html report for a run id is fetched by a thread.')
        else:
            self.logger.error('Html report for ' + self.runId + 'not fetched by thread. Exiting thread...')
            exit(1)
        return self

    # Input Arguments: Object (processReports), host, testName
    # Output Arguments: runId
    # Function: Fetches the latest run Id based on the host and testName.
    def fetchRunIdByTestCase(self, host, testName, iteration):
        testId = self.almObj.almFetchTestId(testName)
        runId = self.almObj.almFetchLatestRunIdByHost(testId[1], host, iteration)
        self.logger.debug('The last ' + str(iteration) + 'run id of ' + testName + ' fetched.')
        return runId






