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
import pandas as pd
import re

extract_information = ["file name", "Model", "Data Path", "#entity", "#relation", "#train",
                       "#valid", "opt", "#test", "batch size", "learning rate", "gamma",
                       "hidden dimension", "negative sample size", "adversarial_temperature",
                       "loss", "MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]
extract_pattern_information = ["file name", "#entity", "#relation", "#train",
                               "#valid", "#test", "MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]

special_information = ["MRR", "MR", "HITS@1", "HITS@3", "HITS@10"]


dirname = os.path.dirname(__file__)
dataset = "wn18rr"
patterns = ["symmetric", "inverse", "implication", "one_to_many"]
# patterns = ["implication", "symmetric", "inverse"]


# patterns = ["symmetric"]


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
        # outputMode = mark_output(logFile)
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
    # return keyValue, outputMode
    return keyValue


def updateExcelFile(keyValue, outputMode):
    updatedDataFrame = appendRow(keyValue, outputMode)
    saveResultAsExcel(updatedDataFrame, outputMode)


# extract data
for pattern in patterns:
    if pattern == "default":
        relPathToLogs = "../results/" + dataset + "/logs/" + pattern
    else:
        relPathToLogs = "../results/" + dataset + "/logs/pattern/" + pattern
    relPathToExcel = os.path.join(dirname + "/../results/" + dataset + "/excel/", "results-" + dataset + "-")
    for root, dirs, files in os.walk(relPathToLogs):
        for file in files:
            # extract key values
            keyValue = get_main_key_values(os.path.join(root, file))
            updatedDataFrame = appendRow(keyValue, pattern)
            saveResultAsExcel(updatedDataFrame, pattern)
