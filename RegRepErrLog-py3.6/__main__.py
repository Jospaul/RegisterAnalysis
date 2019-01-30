# Author: Jospaul Mahajan Prakash
# Company: Infosys Limited
#
# The application helps in compiling the html reports generated by the POS performance test cases in to a tabular
# format that maps the transactions and captures the average response time, 95th percentile response time and the
# transaction count.
#
# The final table can currently be output in 2 ways -
#   * as a csv file to the folder location specified
#   * directly to a teams channel
#
# The application does SLA analysis if it is output to teams.
# Further integrations to Jira and others are planned in future.

from ReportGeneration.POSResults import createPosResult
import ReportGeneration.SupportFiles.logconfig as lcf
import ReportGeneration.SupportFiles.config as cnf
import logging

if __name__ == "__main__":
    cnf.fetchfromconfig()
    lcf.enablelog()
    logger = logging.getLogger('rr.main')
    logger.info('Start Report Generation.')
    createPosResult()
