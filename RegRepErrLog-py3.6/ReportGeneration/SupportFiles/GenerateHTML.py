#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# The module handles generating the output as an HTML and sending to integrations.

import datetime
import requests
import ReportGeneration.SupportFiles.config as cnf
import logging


logger = logging.getLogger('rr.sf.generatehtml')


# Input Arguments: tranName, count, average, percentile, sla=2
# Output Arguments: row
# Function: It accepts the transaction name, count, average response time, 95th percentile response times and sla
#           (default value is 2) and generates a row for the html table after it makes an assessment whether the
#           the average or the 95th percentile response times are greater than the SLA or not.
def createRow(tranName, count, average, percentile, sla=2):
    row = ''
    if cnf.teamsResult.lower() == "long":
        if average > sla:  # abs(average-sla)/sla > 0.3 and average > sla:
            row = "<tr><td>" + tranName + "</td><td>" + str(sla) + "</td><td>" + count +\
                  "</td><td bgcolor=#FF0000>" + str(average) + "</td><td>" + str(percentile) + "</td></tr>"
            if percentile > sla:  # abs(percentile-sla)/sla > 0.3 and percentile > sla:
                row = "<tr><td>" + tranName + "</td><td>" + str(sla) + "</td><td>" + count + \
                      "</td><td bgcolor=#FF0000>" + str(average) + "</td><td bgcolor=#FF0000>" + str(percentile) + "</td></tr>"
        elif percentile > sla:  # abs(percentile-sla)/sla > 0.3 and percentile > sla:
            row = "<tr><td>" + tranName + "</td><td>" + str(sla) + "</td><td>" + count + \
                  "</td><td>" + str(average) + "</td><td bgcolor=#FF0000>" + str(percentile) + "</td></tr>"
        else:
            row = "<tr><td>" + tranName + "</td><td>" + str(sla) + "</td><td>" + count + \
                  "</td><td>" + str(average) + "</td><td>" + str(percentile) + "</td></tr>"
    elif cnf.teamsResult.lower() == "short":
        if average > sla:  # abs(average-sla)/sla > 0.3 and average > sla:
            row = "<tr><td>" + tranName + "</td><td>" + str(sla) + "</td><td>" + count +\
                  "</td><td bgcolor=#FF0000>" + str(average) + "</td><td>" + str(percentile) + "</td></tr>"
            if percentile > sla:  # abs(percentile-sla)/sla > 0.3 and percentile > sla:
                row = "<tr><td>" + tranName + "</td><td>" + str(sla) + "</td><td>" + count + \
                      "</td><td bgcolor=#FF0000>" + str(average) + "</td><td bgcolor=#FF0000>" + str(percentile) + "</td></tr>"
        elif percentile > sla:  # abs(percentile-sla)/sla > 0.3 and percentile > sla:
            row = "<tr><td>" + tranName + "</td><td>" + str(sla) + "</td><td>" + count + \
                  "</td><td>" + str(average) + "</td><td bgcolor=#FF0000>" + str(percentile) + "</td></tr>"

    logger.debug('Row created for transaction ' + tranName + ': ' + row)
    return row


# Input Arguments: rawResults
# Output Arguments: html
# Function: Takes the final result in the dictionary format and generates the html table.
def createHTML(rawResults):
    html = "<html><table style=\\\"width:50%\\\"><tr><th>Transaction Name</th>" +\
           "<th>SLA (sec)</th><th>Count</th><th>Average Response Time (Sec)</th>" +\
           "<th>95th Percentile (Sec)</th></tr>"
    for key in rawResults:
        html = html + createRow(key, str(rawResults[key][0]), rawResults[key][1], rawResults[key][2],
                                cnf.transactions.get(key, 2))

    html = html + "</table></html>"
    logger.debug('HTML table for the test result generated: ' + html)
    return html

# Input Arguments: runStatus
# Output Arguments: html
# Function: Takes the contents of the run status and generate an html to print the status of test.
def createStatusHtml(runStat):
    html = "<html><table style=\\\"width:50%\\\"><tr><th>Run ID</th>" +\
           "<th>Test Name</th><th>Status</th></tr>"
    for key in runStat:
        if runStat[key][1] == 'Passed':
            html = html + "<tr><td>" + str(key) + "</td><td>" + str(runStat[key][0]) + "</td><td bgcolor=#7CFC00>" \
                   + str(runStat[key][1]) + "</td></tr>"
        else:
            html = html + "<tr><td>" + str(key) + "</td><td>" + str(runStat[key][0]) + "</td><td bgcolor=#FF0000>" \
                   + str(runStat[key][1]) + "</td></tr>"

    html = html + "</table></html>"
    logger.debug('HTML table for the run status generated: ' + html)
    return html


# Input Arguments: rawResults
# Output Arguments: None
# Function: Takes the final result in the dictionary format and sends the processed html to specified teams channel
#           from configuration
def postTeams(rawResults, host, runStatus):
    html = createHTML(rawResults)
    teamsLink = cnf.teamsUrl
    logger.debug("Teams Url to send information is " + teamsLink)
    resultstopost = {"title": host + ": POS Results " + str(datetime.date.today()),
                     "text": html}
    try:
        sess = requests.session()
        if cnf.teamsResult.lower() == "long":
            html = createStatusHtml(runStatus)
            statustopost = {"title": host + ": POS Results " + str(datetime.date.today()),
                            "text": html}
            resp = sess.post(teamsLink, data=str(resultstopost), headers={'Content-type': 'text/json'})
            if resp.status_code == 200:
                logger.info('Successfully posted results to teams.')
            else:
                logger.error('Unable to post results to team. Please check the url to teams channel in configuration file.')
            resp = sess.post(teamsLink, data=str(statustopost), headers={'Content-type': 'text/json'})
            if resp.ok:
                logger.info('Successfully posted status to teams.')
            else:
                logger.error('Unable to post status to team. Please check the url to teams channel in configuration file.')
        elif cnf.teamsResult.lower() == "short":
            resp = sess.post(teamsLink, data=str(resultstopost), headers={'Content-type': 'text/json'})
            if resp.status_code == 200:
                logger.info('Successfully posted results to teams.')
            else:
                logger.error(
                    'Unable to post results to team. Please check the url to teams channel in configuration file.')

    except IOError:
        logger.error('Unable to connect to teams channel.')


