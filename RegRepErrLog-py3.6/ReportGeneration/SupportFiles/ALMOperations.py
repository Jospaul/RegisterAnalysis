#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# Module handles all the integration with ALM, from logging in to fetching the html reports.

import json
import requests
from requests.auth import HTTPBasicAuth
from datetime import datetime
from datetime import timedelta
import logging
import sys


class almOperations:
    almUrl = ""
    userName = ""
    pword = ""

    def __init__(self, almUrl, userName, pword):
        self.logger = logging.getLogger('rr.sf.almoperation')
        self.almUrl = almUrl
        self.userName = userName
        self.pword = pword
        self.almSess = requests.session()
        self.logger.debug('Instance of almOperations created!')

    # Input Arguments: Object (almOperations)
    # Output Arguments: Object (almOperations)
    # Function: Initiate a connection to alm and login. Update the incoming object with the session information.
    def almLogin(self):
        almConn = requests.session()
        almResp = almConn.post(self.almUrl + '/authentication-point/authenticate', auth=HTTPBasicAuth(self.userName, self.pword))
        if almResp.status_code == 200:
            self.almSess = almConn
            self.logger.info('Successfully logged in to ALM.')
            self.logger.debug('Session stored in object instance.')
        else:
            self.logger.error('ALM login failed, check credentials for user - ' + self.userName)
            sys.exit(1)
        return self

    # Input Arguments: Object (almOperations)
    # Output Arguments: Object (almOperations)
    # Function: Check whether the session is active.
    def almSession(self):
        almResp = self.almSess.post(self.almUrl + '/rest/site-session')
        if almResp.status_code == 201:
            self.logger.info('ALM Session successfully verified.')
        else:
            self.logger.error('ALM Session expired.')
            self.logger.error('ALM Logging in again as ' + self.userName)
            self.almLogin()
        return self

    # Input Arguments: Object (almOperations)
    # Output Arguments: Object (almOperations)
    # Function: Fetches the project list of ALM. For future use.
    def almFetchProjects(self):
        almConn = self.almSess.get(self.almUrl + '/rest/domains/JCP/projects', headers={'Accept': 'application/json'})
        if almConn.status_code == 200:
            self.logger.debug('Fetched ALM projects successfully.')
        else:
            self.logger.debug('ALM projects were not fetched successfully. Request returned a status '
                              + str(almConn.status_code))
        return self

    # Input Arguments: Object (almOperations), almProject='POS'
    # Output Arguments: Object (almOperations)
    # Function: Fetches all the execution runs of a project. For future use.
    def almFetchRuns(self, almProject='POS'):
        almConn = self.almSess.get(self.almUrl + '/rest/domains/JCP/projects/' + almProject + '/runs',
                                   headers={'Accept': 'application/json'})
        if almConn.status_code == 200:
            self.logger.debug('Test Runs under the project ' + almProject + ' successfully retrieved.')
        else:
            self.logger.debug('Test Runs under the project ' + almProject + ' was not fetched. '
                                                                            'The request failed with status code ' +
                              str(almConn.status_code))
        return self

    # Input Arguments: Object (almOperations), almRunId, almProject
    # Output Arguments: reportContent
    # Function: Fetches html results of the specified run Id from the specified alm project.
    def almFetchReport(self, almRunId, almProject='POS'):
        almConn = self.almSession()
        self.logger.debug('Session verified Successfully before fetching html report.')
        almResponse = almConn.almSess.get(self.almUrl + '/rest/domains/JCP/projects/' +
                                          almProject + '/runs/' + almRunId + '/attachments',
                                          headers={'Accept': 'application/json'})
        reportContent = ''
        if almResponse.status_code == 200:
            self.logger.debug('Request to the attachments of run Id ' + almRunId + ' is successful.')
            parsedResponse = json.loads(almResponse.text)
            self.logger.debug('Parsed the json(Run details) successfully.')
            reportName = parsedResponse["entities"][1]["Fields"][7]["values"][0]["value"]
            if "html" not in reportName:
                reportName = ''
                self.logger.error('Report not present in the run Id ' + almRunId)
            else:
                self.logger.debug('Fetched the name of the attachment ' + reportName)
            reportContent = almConn.almSess.get(self.almUrl + '/rest/domains/JCP/projects/' + almProject + '/runs/'
                                                + almRunId + '/attachments/' + reportName,
                                                headers={'Accept': 'application/octet-stream'})
            if reportContent.status_code == 200:
                self.logger.info('Contents of the html report successfully read.')
            else:
                self.logger.error('Reading the html report failed with status ' + str(reportContent.status_code))
                exit(1)
        return reportContent

    # Input Arguments: Object (almOperations), testName, status, almProject
    # Output Arguments: list containing totalCount of tests found and the test Id
    # Function: Fetches totalCount of tests found and the test Id based on the testName, status and project.
    def almFetchTestId(self, testName, status='Ready', almProject='POS'):
        almConn = self.almSession()
        self.logger.debug('Successfully verified session before fetching test id of test ' + testName)
        almResponse = almConn.almSess.get(self.almUrl + '/rest/domains/JCP/projects/' +
                                          almProject + '/tests?query={name[' + testName + '];status[' +
                                          status + ']}&fields=id',
                                          headers={'Accept': 'application/json'})
        testId = ''
        totalCount = ''
        if almResponse.status_code == 200:
            parsedResponse = json.loads(almResponse.text)
            testId = parsedResponse["entities"][0]["Fields"][0]["values"][0]["value"]
            totalCount = parsedResponse["TotalResults"]
            self.logger.debug('Fetched the test id of testName ' + testName)
        else:
            self.logger.error('Test id of ' + testName + ' was not fetched. The request failed with status '
                              + str(almResponse.status_code))
        return [totalCount, testId]

    # Input Arguments: Object (almOperations), testId, status, almProject, host
    # Output Arguments: runId
    # Function: Fetches latest run id of a particular test that was executed and passed.
    def almFetchLatestRunIdByHost(self, testId, host, iteration, almProject='POS'):
        almConn = self.almSession()
        self.logger.debug('Successfully verified session before fetching latest run id of test id ' + testId)
        almResponse = almConn.almSess.get(self.almUrl + '/rest/domains/JCP/projects/' +
                                          almProject + '/runs?query={host[' +
                                          host + '];test-id[' + testId + ']}&' +
                                          'fields=id,attachment,owner,execution-date,execution-time'
                                          '&order-by={execution-date[DESC];execution-time[DESC]}',
                                          headers={'Accept': 'application/json'})

        testRuns = {}

        if almResponse.status_code == 200:
            parsedResponse = json.loads(almResponse.text)
            totalCount = len(parsedResponse["entities"])
            i = 0
            while i < int(totalCount):
                fetchDateInEntity = parsedResponse["entities"][i]["Fields"][1]["values"][0]["value"]
                fetchTimeInEntity = parsedResponse["entities"][i]["Fields"][4]["values"][0]["value"]
                fetchRunId = parsedResponse["entities"][i]["Fields"][0]["values"][0]["value"]
                testRuns[fetchRunId] = [fetchDateInEntity, fetchTimeInEntity]
                i = i + 1

            self.logger.debug('Successfully fetched all the test runs of test id ' + testId)
        else:
            self.logger.error('Unable to fetch test runs of test id ' + testId
                              + '. The request failed with status ' + str(almResponse.status_code))


        return self.fetchLatestFromDictionary(testRuns, iteration)

    # Input Arguments: Object (almOperations), testruns
    # Output Arguments: runId
    # Function: Scans through the several runs and finds the latest based on current date and time.
    def fetchLatestFromDictionary(self, testRuns, iter=1):
        todaysDate = datetime.today()
        self.logger.debug('Todays date is ' + str(todaysDate))
        fivedaysbefore = todaysDate + timedelta(days=-5)
        self.logger.debug('Date 30 days ago is ' + str(fivedaysbefore))
        temp = todaysDate - fivedaysbefore
        if iter == 1:
            runId = ''
            self.logger.debug('Start fetching the latest run id from the list of test runs.')
            for key in testRuns.keys():
                diffDate = todaysDate - datetime.strptime(testRuns[key][0] + ' ' + testRuns[key][1],
                                                          '%Y-%m-%d %H:%M:%S')
                if temp > diffDate:
                    temp = diffDate
                    runId = key
            self.logger.info('Latest test run is fetched and the run Id is ' + runId)
            return runId
        else:
            latestruns = {}
            templist = []
            self.logger.debug('Start fetching the latest ' + str(iter) + ' runs')
            for key in testRuns.keys():
                diffDate = todaysDate - datetime.strptime(testRuns[key][0] + ' ' + testRuns[key][1],
                                                          '%Y-%m-%d %H:%M:%S')
                latestruns[diffDate] = key
            for key in sorted(latestruns):
                templist.append(latestruns[key])
            rund = templist[0:iter]
            self.logger.info('Latest ' + str(iter) + ' runs of the test is fetched and the list is ' + str(rund))
            return rund

    # Input Arguments: runId
    # Output Arguments: testDetailList - Consists of runId, test name and status of the test
    # Function: To identify the status of the test run.
    def fetchStatusNameByRunId(self, runId, project='POS'):
        resp = self.almSess.get(self.almUrl + '/rest/domains/JCP/projects/' + project + '/runs?query={id[' + runId +
                                ']}&fields=test-id,status', headers={'Accept': 'application/json'})
        testdetaillist = []
        if resp.ok:
            self.logger.debug("Successfully fetched test id from run id provided.")
            parsedresp = json.loads(resp.text)
            status = parsedresp["entities"][0]["Fields"][1]["values"][0]["value"]
            testId = parsedresp["entities"][0]["Fields"][2]["values"][0]["value"]
            testName = self.fetchNameBytTestId(testId)
            testdetaillist = [runId, testId, testName, status]
        else:
            self.logger.debug("The details of the run id could not be captured, please check the run id " + runId)

        return testdetaillist

    # Input Arguments: testId
    # Output Arguments: testName
    # Function: To identify the status of the test run.
    def fetchNameBytTestId(self, testId, project='POS'):
        resp = self.almSess.get(self.almUrl + '/rest/domains/JCP/projects/' + project + '/tests?query={id[' +
                                testId + ']}&fields=name', headers={'Accept': 'application/json'})
        testName=''
        if resp.ok:
            self.logger.debug("Successfully fetched the test details")
            parsedResp = json.loads(resp.text)
            testName = parsedResp["entities"][0]["Fields"][1]["values"][0]["value"]
        else:
            self.logger.debug("Unable to fetch the test name with the test id provided. Please check test Id " + testId)
        return testName

