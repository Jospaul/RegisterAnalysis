#!/usr/bin/env python
# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
# Module handles all the parsing of the html file and collecting the transaction information from the report.

from bs4 import BeautifulSoup
import logging

class processHtml:
    extractedHtml = ""

    def __init__(self, extractedHtml):
        self.extractedHtml = extractedHtml
        self.logger = logging.getLogger('rr.sf.processhtml')

    # Input Arguments: Object (processHtml)
    # Output Arguments: parsedHtml
    # Function: Reads the string data and parses it as a html
    def parseHtml(self):
        parsedHtml = BeautifulSoup(self.extractedHtml.text, "html.parser")
        if not parsedHtml:
            self.logger.error('Unable to parse html received. Please check report format.')
        else:
            self.logger.debug('Successfully parsed the html report.')
        return parsedHtml

    # Input Arguments: Object (processHtml), listWithTag
    # Output Arguments: listNoTag
    # Function: Fetches the string between the tags of given html line.
    def listWithNoTag(self, listWithTag):
        listNoTag = []
        for transaction in listWithTag:
            listNoTag.append(transaction.string)
        self.logger.debug('Successfully extracted the transaction response time values from '
                          'their respective html tags.')
        return listNoTag

    # Input Arguments: Object (processHtml)
    # Output Arguments: trList
    # Function: Fetches the transaction names from the html report.
    def transactionList(self):
        parsedHtml = processHtml.parseHtml(self)
        nameList = []
        for n in parsedHtml.findAll('td'):
            nameList.append(n.get('name'))
        trList = list(set(nameList))
        trList.remove(None)
        trList.remove("TotalSec")
        trList.remove("GrandTotalSec")
        trList.append('POSLaunch')
        self.logger.debug('Successfully fetched the transactions present in the html report.')
        return trList

    # Input Arguments: Object (processHtml), transactionName
    # Output Arguments: list
    # Function: Fetches the response times corresponding to each transactions and returns them in a list.
    def responseTimeListByTransaction(self, transactionName):
        transactionList = processHtml.parseHtml(self).select('td[name=' + transactionName + ']')
        responseTimeList = []
        for member in transactionList:
            responseTimeList.append(processHtml.responseTimePerEntry(self, member))
        self.logger.debug('Successfully fetched the response times and mapped them to their '
                          'corresponding transaction names.')
        return processHtml.secondStringToNumbers(self, responseTimeList)

    # Input Arguments: Object (processHtml), transactionEntry
    # Output Arguments: string
    # Function: Finds the response time of a particular transaction based on the name and returns the value
    def responseTimePerEntry(self, transactionEntry):
        return transactionEntry.find_all('b')[0].string

    # Input Arguments: Object (processHtml), listOfSecondsString
    # Output Arguments: list
    # Function: Takes the list of response times from the html report and then convert them to a list of float numbers
    def secondStringToNumbers(self, listOfSecondsString):
        listOfSecondNum = []
        for val in listOfSecondsString:
            newVal = val.replace("s", "")
            listOfSecondNum.append(float(newVal))
        self.logger.debug('Successfully converted the response times in string format to float.')
        return listOfSecondNum
