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

# This log to excel converter is built by me during my bachelor thesis
# at university of Bonn. If you use it as a whole or part, I would appreciate
# if you acknowledge my work by mention it. This code is published under MIT license.
# shayan.shahpasand@uni-bonn.de


import os
import glob
import pandas as pd
import re

extract_information = ["file name", "Model", "Data Path", "#entity", "#relation", "#train",
                       "#valid", "opt", "#test", "batch size", "learning rate", "gamma",
                       "hidden dimension", "negative sample size", "adversarial_temperature",
                       "loss", "MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]

special_information = ["MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]

dirname = os.path.dirname(__file__)
dataset = "wn18rr"
relPathToLogs = "../Results/raw_results/hpc/" + dataset + "-new-grid-shayan"

# pathToLogs = os.path.join(dirname, relPathToLogs, '*.log')

pathToExcel = os.path.join(dirname, "results-new-grid-" + dataset + "-shayan.xlsx")


def saveResultAsExcel(dataFrame):
    dataFrame.to_excel(pathToExcel, index=False)


def appendRow(keyValue):
    completeRow = dict.fromkeys(extract_information)
    for key in completeRow:
        if key in keyValue.keys():
            completeRow[key] = keyValue[key]
        else:
            completeRow[key] = ""

    newRow = pd.DataFrame([completeRow.values()], columns=completeRow.keys())
    currentSheet = pd.read_excel(pathToExcel, sheet_name=0)
    updatedSheet = currentSheet.append(newRow, ignore_index=True)
    return updatedSheet


def updateExcelFile(filename):
    # for filename in glob.glob(os.path.join(pathToLogs)):
    with open(os.path.join(filename), 'r') as logFile:
        keyValue = {"file name": os.path.basename(logFile.name)}
        logFile = logFile.readlines()
        skip_second_gamma = False
        for line in logFile:
            for phrase in extract_information:
                if phrase in line:
                    if phrase in special_information:
                        if phrase == 'HITS@1' and "HITS@10" in line:
                            continue
                        else:
                            value = re.search(r": \d*\.?\d+", line)
                        if value is not None:
                            keyValue[phrase] = value.group()[2:]
                    else:
                        # REMOVE NEXT LINE  IF WHEN YOU GET RID OF SECOND GAMMA IN LOGS
                        if phrase == 'gamma' and skip_second_gamma is False:
                            skip_second_gamma = True
                            value = re.search(rf"{phrase}: ?.*", line)
                        elif phrase != 'gamma':
                            value = re.search(rf"{phrase}: ?.*", line)
                        if value is not None:
                            keyValue[phrase] = value.group()[phrase.__len__() + 2:]

    updatedDataFreame = appendRow(keyValue)
    saveResultAsExcel(updatedDataFreame)


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


# remove duplicate log files
for root, dirs, files in os.walk(relPathToLogs):
    for file in files:
        logCounts = len(glob.glob1(root, "*.log"))
        if logCounts > 1:
            log_with_results = ""
            # find the largest file loop
            max_size = 0
            #  find the log file with results and save the name
            for logFile in os.listdir(root):
                logFilePath = os.path.join(root, logFile)
                if logFile.endswith(".log") and check_for_results(logFilePath):
                    log_with_results = os.path.basename(logFilePath)
                    break

            #  Remove every log file without results if we have found one log file with result
            if log_with_results != "":
                for logFile in os.listdir(root):
                    logFilePath = os.path.join(root, logFile)
                    if logFile.endswith(".log") and os.path.basename(logFilePath) != log_with_results:
                        os.remove(logFilePath)

            #  keep the largest log file if no log file were found with results
            else:
                for logFile in os.listdir(root):
                    #  find the largest file
                    if logFile.endswith(".log") and os.stat(os.path.join(root, logFile)).st_size > max_size:
                        max_size = os.stat(os.path.join(root, logFile)).st_size
                        continue
                    #  remove the file if there is already another file exist with the same size
                    if logFile.endswith(".log") and os.stat(os.path.join(root, logFile)).st_size == max_size:
                        os.remove(os.path.join(root, logFile))
                #  remove every log file smaller than max size
                for logFile in os.listdir(root):
                    if logFile.endswith(".log") and os.stat(os.path.join(root, logFile)).st_size < max_size:
                        os.remove(os.path.join(root, logFile))

# extract data
for root, dirs, files in os.walk(relPathToLogs):
    for file in files:
        if file.endswith(".log"):
            log_fileName = os.path.join(root, file)
            updateExcelFile(log_fileName)
