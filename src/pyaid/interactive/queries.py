# queries.py
# (C)2010-2012
# Scott Ernst

from __future__ import print_function
from __future__ import absolute_import

import sys

from pyaid.reflection.Reflection import Reflection

if sys.version > '3':
    raw_input = input

#___________________________________________________________________________________________________ queryForInteger
def queryForInteger(question, minimum=None, maximum=None):
    while 1:
        sys.stdout.write(question + " ")
        i = raw_input()
        if i.isdigit():
            if (minimum is None or i >= minimum) and (maximum is None or i <= maximum):
                result = queryYesNo("Confirm your input of: " + str(i), None)
                if result == "yes":
                    return i
            else:
                sys.stdout.write("Value must be an integer.\n")
        else:
            sys.stdout.write("Value must be an integer.\n")
        print("\n")

#___________________________________________________________________________________________________ queryGeneralValue
def queryGeneralValue(question, default =None, allowEmpty =False):
    if default is None:
        default = ''

    while 1:
        sys.stdout.write(question + "[" + default + "]? ")
        result = raw_input().strip()
        if result is None or len(result) < 1:
            if len(default) < 1 and not allowEmpty:
                sys.stdout.write("A valid input is required.\n")
            else:
                check = queryYesNo("Confirm your input of: " + str(default), "yes")
                if check == "yes":
                    return default
        else:
            check = queryYesNo("Confirm your input of: " + result, "yes")
            if check == "yes":
                return result
        print("\n")

#___________________________________________________________________________________________________ queryFromList
def queryFromLargeList(question, choices, data =None, pageSize =30, default =None):
    if pageSize < 4:
        pageSize = 4

    index    = 0
    active   = True

    moreChoice  = 'More Results'
    prevChoice  = 'Previous Results'
    pageData    = None
    pageHistory = []

    dumb        = '%JK@LA!~KSL#_%*JGJ%K#%K%H#K@D))GHEDNAkdfhoawiofnalkawdhiwl3927109347---==+'
    dataChoice  = dumb

    while active:
        hasDefaultChoices = None

        if index == 0:
            end = index + pageSize - 1

            pageChoices = choices[index:end]
            if end < len(choices) - 1:
                pageChoices += [moreChoice]
                hasDefaultChoices = [len(pageChoices) - 1]

            if data:
                pageData = data[index:end] + [None]

        elif index + pageSize - 1 >= len(choices):
            end               = len(choices)
            pageChoices       = choices[index:end] + [prevChoice]
            hasDefaultChoices = [len(pageChoices) - 1]
            if data:
                pageData = data[index:end] + [None]
        else:
            end               = index + pageSize - 2
            pageChoices       = choices[index:end] + [prevChoice, moreChoice]
            hasDefaultChoices = [len(pageChoices) - 2, len(pageChoices) - 1]
            if data:
                pageData = data[index:end] + [None, None]

        pageHistory.append(index)
        if pageData:
            choice, dataChoice = queryFromList(question, pageChoices, pageData, index + 1,
                                               skipConfirmIndexes=hasDefaultChoices,
                                               default=default)
        else:
            choice = queryFromList(question, pageChoices, pageData, index + 1,
                                   skipConfirmIndexes=hasDefaultChoices, default=default)

        if choice == prevChoice:
            pageHistory.pop()
            index = pageHistory[-1]
        elif choice == moreChoice:
            index = min(len(choices) - 1, end)
        else:
            active = False

    if dataChoice != dumb:
        return choice, dataChoice
    else:
        return choice

#___________________________________________________________________________________________________ queryFromList
def queryFromList(question, choices, data=None, indexOffset=1, confirm =True,
                  skipConfirmIndexes =None, default =None):
    index = indexOffset

    defaultData = default if (default and data and default in data) else None

    if defaultData:
        defaultChoice = choices[data.index(defaultData)]
    else:
        defaultChoice = default if (default and default in choices) else None

    if defaultChoice and data and not defaultData:
        defaultData = data[choices.index(defaultChoice)]

    print('Choose from the following list:')
    for item in choices:
        print('\t' + str(index) + ': ' + item)
        index += 1

    while 1:
        if default:
            sys.stdout.write('%s [%s] ' % (question, str(default)))
        else:
            sys.stdout.write(question + " ")
        result = raw_input()
        try:
            if not result and defaultChoice:
                if confirm:
                    res = queryYesNo('Confirm selection of ' + str(defaultChoice), 'yes')
                else:
                    res = 'yes'

                if res == 'yes':
                    if data is None:
                        return defaultChoice
                    else:
                        return defaultChoice, defaultData
            else:
                choiceIndex = int(result) - indexOffset
                if choiceIndex <= len(choices):
                    if skipConfirmIndexes is None or not choiceIndex in skipConfirmIndexes:
                        res = queryYesNo("Confirm your selection of: " + result + " - " \
                                            + str(choices[choiceIndex]), None)
                    else:
                        res = 'yes'

                    if res == "yes":
                        if data is None:
                            return choices[choiceIndex]
                        else:
                            return choices[choiceIndex], data[choiceIndex]
                else:
                    sys.stdout.write("Please respond with a valid number.\n")
        except ValueError:
            sys.stdout.write("Entry appears invalid. Please try again.\n")
        print("\n")

#___________________________________________________________________________________________________ queryByReflection
def queryByReflection(question, reflectionSource, default =None):
    choices, data            = Reflection.getReflectionNameValueLists(reflectionSource)
    choiceResult, dataResult = queryFromLargeList(question, choices, data, default=default)
    return dataResult

#___________________________________________________________________________________________________ queryYesNoQuit
def queryYesNo(question, default="yes"):
    valid = {"yes":"yes",   "y":"yes",    "ye":"yes",
             "no":"no",     "n":"no"}
    if default is None:
        prompt = " [y/n] [] "
    elif default == "yes":
        prompt = " [y/n] [y]"
    elif default == "no":
        prompt = " [y/n] [n]"
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        result = raw_input().lower()
        if default is not None and result == '' or result is None:
            return default
        elif result in valid.keys():
            return valid[result]
        else:
            sys.stdout.write("Please respond with 'yes' or 'no'.\n")
        print("\n")

#___________________________________________________________________________________________________ queryContinueSkipQuit
def queryContinueSkipQuit(question, default="continue"):
    valid = {"continue":"continue",   "c":"continue",    "co":"continue", "con":"continue",
             "cont":"continue", "conti":"continue", "contin":"continue", "continu":"continue",
             "skip":"skip",     "s":"skip", "sk":"skip", "ski":"skip",
             "quit":"quit", "qui":"quit", "qu":"quit", "q":"quit"}

    prompt = " [continue(c)/skip(s)/quit(q)] [**]:"
    if default is None:
        prompt = prompt.replace("**", "")
    elif default == "continue":
        prompt = prompt.replace("**", "c")
    elif default == "skip":
        prompt = prompt.replace("**", "s")
    elif default == "quit":
        prompt = prompt.replace("**", "q")
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        result = raw_input().lower()
        if default is not None and result == '':
            return default
        elif result in valid.keys():
            return valid[result]
        else:
            sys.stdout.write("Please respond with 'continue', 'skip' or 'quit'.\n")
        print("\n")

#___________________________________________________________________________________________________ queryYesNoQuit
def queryYesNoQuit(question, default="yes"):
    valid = {"yes":"yes",   "y":"yes",    "ye":"yes",
             "no":"no",     "n":"no",
             "quit":"quit", "qui":"quit", "qu":"quit", "q":"quit"}
    if default is None:
        prompt = " [y/n/q] [] "
    elif default == "yes":
        prompt = " [y/n/q] [y]"
    elif default == "no":
        prompt = " [y/n/q] [n]"
    elif default == "quit":
        prompt = " [y/n/q] [q]"
    else:
        raise ValueError("invalid default answer: '%s'" % default)

    while 1:
        sys.stdout.write(question + prompt)
        result = raw_input().lower()
        if default is not None and result == '':
            return default
        elif result in valid.keys():
            return valid[result]
        else:
            sys.stdout.write("Please respond with 'yes', 'no' or 'quit'.\n")
        print("\n")

#___________________________________________________________________________________________________ queryMasterOrSlave
def queryMasterOrSlave(question):
    valid = {"master":"master", "m":"master", "ma":"master", "mas":"master", "mast":"master",
             "maste":"master",
             "slave":"slave", "s":"slave", "sl":"slave", "sla":"slave", "slav":"slave",
             "quit":"quit", "qui":"quit", "qu":"quit", "q":"quit"}

    while 1:
        sys.stdout.write(question + " [master/slave/quit]: ")
        result = raw_input().lower()
        if result in valid.keys():
            return valid[result]
        else:
            sys.stdout.write("Please respond with 'master', 'slave' or 'quit'.\n")
        print("\n")
