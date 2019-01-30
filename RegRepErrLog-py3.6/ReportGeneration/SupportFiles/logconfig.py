import logging
import ReportGeneration.SupportFiles.config as cnf
from datetime import datetime

def enablelog():
    logfile = cnf.logLoc
    logger = logging.getLogger('rr')
    if cnf.logLevel.lower() == 'DEBUG'.lower():
        logger.setLevel(logging.DEBUG)
    else:
        logger.setLevel(logging.INFO)
    fh = logging.FileHandler(logfile + '\\regrep' + datetime.today().strftime('%Y_%m_%dT%H%M%S') + '.log')
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    fh.setFormatter(formatter)
    logger.addHandler(fh)
