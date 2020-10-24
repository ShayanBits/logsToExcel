# Copyright © 2020 Shayan Shahpasand

# ===============================================================
# ==      ===  ====  =====  =====  ====  =====  =====  =======  =
# =  ====  ==  ====  ====    ====   ==   ====    ====   ======  =
# =  ====  ==  ====  ===  ==  ====  ==  ====  ==  ===    =====  =
# ==  =======  ====  ==  ====  ===  ==  ===  ====  ==  ==  ===  =
# ====  =====        ==  ====  ====    ====  ====  ==  ===  ==  =
# ======  ===  ====  ==        =====  =====        ==  ====  =  =
# =  ====  ==  ====  ==  ====  =====  =====  ====  ==  =====    =
# =  ====  ==  ====  ==  ====  =====  =====  ====  ==  ======   =
# ==      ===  ====  ==  ====  =====  =====  ====  ==  =======  =
# ===============================================================

# This log purefier is written by me during my bachelor thesis
# at university of Bonn. If you use it as a whole or part, I would appreciate
# if you acknowledge my work by mention it. This code is published under MIT license.
# shayan.shahpasand@uni-bonn.de


import os
import glob
import shutil
import pandas as pd
import re

extract_information = ["file name", "Model", "Data Path", "#entity", "#relation", "#train",
                       "#valid", "opt", "#test", "batch size", "learning rate", "gamma",
                       "hidden dimension", "negative sample size", "adversarial_temperature",
                       "loss", "MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]
extract_pattern_information = ["file name", "#entity", "#relation", "#train",
                               "#valid", "#test", "MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]

special_information = ["MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]

output_modes = ["symmetric", "inverse", "implication"]

dirname = os.path.dirname(__file__)
dataset = "fb15k"
relPathToLogs = "../results/" + dataset + "/models/"

logsDirectory = "../results/" + dataset + "/logs/"

# pathToLogs = os.path.join(dirname, relPathToLogs, '*.log')

relPathToExcel = os.path.join(dirname, "results-" + dataset + "-")



def check_for_results(filename):
    with open(os.path.join(filename), 'r') as logFile:
        logFile = logFile.readlines()
        for line in logFile:
            for phrase in extract_information:
                if phrase in line:
                    if phrase in special_information:
                        if phrase == 'HITS@1' and "HITS@10" in line:
                            return True
        return False


def mark_output(logFile):
    for line in logFile:
        for phrase in output_modes:
            if phrase in line:
                return phrase
    return 'default'


def is_pattern_file(filename):
    with open(os.path.join(filename), 'r') as logFile:
        logFile = logFile.readlines()
        for line in logFile:
            for phrase in output_modes:
                if phrase in line:
                    return phrase
        return False


def purify_logfiles():
    for root, dirs, files in os.walk(relPathToLogs):
        for file in files:
            logCounts = len(glob.glob1(root, "*.log"))
            if logCounts == 1:
                for logFile in os.listdir(root):
                    logFilePath = os.path.join(root, logFile)
                    if logFile.endswith(".log"):
                        shutil.copy(logFilePath, logsDirectory)
                        break
            elif logCounts > 1:
                log_with_results = ""
                # find the largest file loop
                max_size = 0
                #  find the log file with results and save the name
                for logFile in os.listdir(root):
                    logFilePath = os.path.join(root, logFile)
                    if logFile.endswith(".log") and check_for_results(logFilePath) and not is_pattern_file(logFilePath):
                        log_with_results = os.path.basename(logFilePath)
                        # check if the log is already in the logs directory
                        if os.path.exists(logsDirectory + logFile):
                            shutil.copy(logFilePath, logsDirectory)
                            break

                #  Remove every log file(non pattern ones) without results if we have found one log file with result
                if log_with_results != "":
                    for logFile in os.listdir(root):
                        logFilePath = os.path.join(root, logFile)
                        if logFile.endswith(".log") and \
                                os.path.basename(logFilePath) != log_with_results and not \
                                is_pattern_file(logFilePath):
                            os.remove(logFilePath)
                            break

                #  keep the largest log file if no log file were found with results
                else:
                    for logFile in os.listdir(root):
                        logFilePath = os.path.join(root, logFile)
                        #  find the largest file
                        if logFile.endswith(".log") and os.stat(logFilePath).st_size > max_size and not \
                                is_pattern_file(logFilePath):
                            max_size = os.stat(logFilePath).st_size
                            # check if the log is already in the logs directory
                            if os.path.exists(logsDirectory + logFile):
                                shutil.copy(logFilePath, logsDirectory)
                                continue
                        #  remove duplicate files
                        if logFile.endswith(".log") and os.stat(logFilePath).st_size == max_size:
                            os.remove(logFilePath)
                    #  remove every log file smaller than max size which
                    #  doesnt contain results and are not pattern based
                    # TODO: remove all pattern files except the largest one for each pattern
                    for logFile in os.listdir(root):
                        logFilePath = os.path.join(root, logFile)
                        if logFile.endswith(".log") and os.stat(logFilePath).st_size < max_size and not \
                                is_pattern_file(logFilePath):
                            os.remove(logFilePath)

purify_logfiles()