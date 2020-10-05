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
extract_pattern_information = ["file name", "#entity", "#relation", "#train",
                               "#valid", "#test", "MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]

special_information = ["MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]

output_modes = ["symmetric", "inverse", "implication"]

dirname = os.path.dirname(__file__)
dataset = "fb15k"
relPathToLogs = "../Results/raw_results/hpc/" + dataset + "-new-grid" + "/models/RotatE/rotate"

# pathToLogs = os.path.join(dirname, relPathToLogs, '*.log')

relPathToExcel = os.path.join(dirname, "results-" + dataset + "-")


# pathToExcel = os.path.join(dirname, "results-new-grid-" + dataset + "-shayan.xlsx")


def saveResultAsExcel(dataFrame, outputMode):
    exactPathToExcel = os.path.join(relPathToExcel + outputMode + ".xlsx")
    dataFrame.to_excel(exactPathToExcel, index=False)


def appendRow(keyValue, outputMode):
    completeRow = dict.fromkeys(extract_information)
    for key in completeRow:
        if key in keyValue.keys():
            completeRow[key] = keyValue[key]
        else:
            completeRow[key] = ""

    newRow = pd.DataFrame([completeRow.values()], columns=completeRow.keys())
    exactPathToExcel = os.path.join(relPathToExcel + outputMode + ".xlsx")
    currentSheet = pd.read_excel(exactPathToExcel, sheet_name=0)
    updatedSheet = currentSheet.append(newRow, ignore_index=True)
    return updatedSheet


def get_main_key_values(filename):
    with open(os.path.join(filename), 'r') as logFile:
        keyValue = {"file name": os.path.basename(logFile.name)}
        logFile = logFile.readlines()
        outputMode = mark_output(logFile)
        # if its default result, keep key values as is and only update hit@10
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
                        # REMOVE NEXT LINE  WHENEVER YOU GET RID OF SECOND GAMMA IN LOGS
                        if phrase == 'gamma' and skip_second_gamma is False:
                            skip_second_gamma = True
                            value = re.search(rf"{phrase}: ?.*", line)
                        elif phrase != 'gamma':
                            value = re.search(rf"{phrase}: ?.*", line)
                        if value is not None:
                            keyValue[phrase] = value.group()[phrase.__len__() + 2:]
    return keyValue, outputMode


def get_pattern_key_values(filename, keyValue):
    with open(os.path.join(filename), 'r') as logFile:
        keyValue["file name"] = os.path.basename(logFile.name)
        logFile = logFile.readlines()
        outputMode = mark_output(logFile)
        # if its default result, keep key values as is and only update hit@10
        skip_second_gamma = False
        for line in logFile:
            for phrase in extract_pattern_information:
                if phrase in line:
                    if phrase in extract_pattern_information:
                        if phrase == 'HITS@1' and "HITS@10" in line:
                            continue
                        else:
                            value = re.search(r": \d*\.?\d+", line)
                        if value is not None:
                            keyValue[phrase] = value.group()[2:]
                    else:
                        # REMOVE NEXT LINE  WHENEVER YOU GET RID OF SECOND GAMMA IN LOGS
                        if phrase == 'gamma' and skip_second_gamma is False:
                            skip_second_gamma = True
                            value = re.search(rf"{phrase}: ?.*", line)
                        elif phrase != 'gamma':
                            value = re.search(rf"{phrase}: ?.*", line)
                        if value is not None:
                            keyValue[phrase] = value.group()[phrase.__len__() + 2:]
    return keyValue, outputMode


def updateExcelFile(keyValue, outputMode):
    updatedDataFrame = appendRow(keyValue, outputMode)
    saveResultAsExcel(updatedDataFrame, outputMode)


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


def find_the_largest_file(root):
    max_size = 0
    largest_file = ""
    for logFile in os.listdir(root):
        logFilePath = os.path.join(root, logFile)
        #  find the largest file
        if logFile.endswith(".log") and os.stat(logFilePath).st_size > max_size:
            max_size = os.stat(logFilePath).st_size
            largest_file = os.path.basename(logFilePath)
    return largest_file


def purify_logfiles():
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
                        if logFile.endswith(".log") and \
                                os.path.basename(logFilePath) != log_with_results and not \
                                check_for_results(logFilePath):
                            os.remove(logFilePath)

                #  keep the largest log file if no log file were found with results
                else:
                    for logFile in os.listdir(root):
                        logFilePath = os.path.join(root, logFile)
                        #  find the largest file
                        if logFile.endswith(".log") and os.stat(logFilePath).st_size > max_size:
                            max_size = os.stat(logFilePath).st_size
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
                                check_for_results(logFilePath) and not is_pattern_file(logFilePath):
                            os.remove(logFilePath)


# remove duplicate log files
# purify_logfiles()

# extract data
for root, dirs, files in os.walk(relPathToLogs):
    # flag to check if this directory is processed before
    is_checked = False
    for file in files:
        if is_checked:
            continue
        # find the larges file
        logCounts = len(glob.glob1(root, "*.log"))
        if logCounts > 1:
            is_checked = True
            largest_file = find_the_largest_file(os.path.join(root))
            # extract key values
            keyValue, outputMode = get_main_key_values(os.path.join(root, largest_file))
            updatedDataFrame = appendRow(keyValue, outputMode)
            saveResultAsExcel(updatedDataFrame, outputMode)
        # for every other log only use these key values
        for file in files:
            if file.endswith(".log") and not os.path.basename(file) == largest_file:
                log_fileName = os.path.join(root, file)
                keyValue, outputMode = get_pattern_key_values(log_fileName, keyValue)
                updateExcelFile(keyValue, outputMode)
