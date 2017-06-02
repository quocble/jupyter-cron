import re
import time
import daemon
import glob
import schedule
import pathlib
import os
import argparse
import inspect
from types import FunctionType
import logging

logger = logging.getLogger('jupyter-cron')
ch = logging.StreamHandler()
ch.setLevel(logging.DEBUG)
logger.addHandler(ch)
logging.getLogger().setLevel(logging.DEBUG)

formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

parser = argparse.ArgumentParser(description="Scans for file to run on a schedule based on its name")
parser.add_argument("glob", type=str, help="specify glob to search eg. test/**/*.ipynb")
parser.add_argument("-d", "--daemonize", help="daemonize the process", action="store_true")
parser.add_argument("-l", "--log", type=str, help="specify log file")

args = parser.parse_args()

patternEveryN = re.compile('(.*) \(every (.*) at (.*)\)', re.IGNORECASE)
patternTime = re.compile("(0?[1-9]|1[012])(.[0-5]\d)?[APap][mM]")

supported_exts = ['.py','.ipynb']
every_X = ['day', 'monday', 'tuesday', 'wednesday','thursday', 'friday','saturday','sunday']

if args.log:
    fh = logging.FileHandler(args.log)
    fh.setLevel(logging.DEBUG)
    fh.setFormatter(formatter)
    logger.addHandler(fh)
    logger.info("set log file to " +  args.log)

def job(filename):
    # check if file exist, if not remove from schedule
    path = pathlib.Path(filename)

    if path.is_file():
        logger.info ("Running file " + filename + " with ext " + path.suffix)
        if path.suffix == '.ipynb':
            os.system("jupyter nbconvert --ExecutePreprocessor.timeout=300 --execute \"" + filename + "\"")
        if path.suffix == '.py':
            os.system("python \"" + filename + "\" > \"" + filename + ".output.txt\"")
    else:
        logger.warn("File does not exist " + filename)
        return schedule.CancelJob


def build_schedule():
    for filename in glob.iglob(args.glob, recursive=True):
        #print (filename)
        match = patternEveryN.match(filename)
        if match == None:
            logger.info ("format does not match " + filename)
            continue

        timeMatch = patternTime.match(match.group(3))
        if timeMatch == None:
            logger.info ("time is not correct format " +  filename)
            continue

        #print (match.group(1,2,3))
        t = None
        logger.info (filename + " matches for schedule")

        if timeMatch.group(2) == None:
            t = time.strptime(match.group(3).upper(), "%I%p")
        else:
            t = time.strptime(match.group(3).upper(), "%I.%M%p")
        time_str = str(t.tm_hour) + ":" + str(t.tm_min)

        tagHash = match.group(1) + match.group(2) + match.group(3)
        path = pathlib.Path(filename)

        found = []
        found[:] = (job for job in schedule.jobs if tagHash in job.tags)

        # new job - insert / same job will be discarded
        if len(found) == 0 and path.suffix in supported_exts:
            x = match.group(2).lower()
            if x in every_X:
                every = schedule.every()
                getattr(every, x).at(time_str).do(job, filename).tag(tagHash)
            else:
                logger.warn(match.group(2) + " is not valid")

    logger.info ("current schedule")
    for j in schedule.jobs:
        logger.info (j)


schedule.every(5).minutes.do(build_schedule)
build_schedule()

def run_loop():
    while True:
        schedule.run_pending()
        time.sleep(1)

if __name__ == "__main__":
    if args.daemonize:
        with daemon.DaemonContext():
            run_loop()
    else:
        run_loop()
