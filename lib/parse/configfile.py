#!/usr/bin/env python

"""
Copyright (c) 2006-2023 sqlmap developers (https://sqlmap.org/)
See the file 'LICENSE' for copying permission
"""

from lib.core.common import checkFile
from lib.core.common import getSafeExString
from lib.core.common import openFile
from lib.core.common import unArrayizeValue
from lib.core.common import UnicodeRawConfigParser
from lib.core.convert import getUnicode
from lib.core.data import cmdLineOptions
from lib.core.data import conf
from lib.core.data import logger
from lib.core.enums import OPTION_TYPE
from lib.core.exception import SqlmapMissingMandatoryOptionException
from lib.core.exception import SqlmapSyntaxException
from lib.core.optiondict import optDict

config = None

def configFileProxy(section, option, datatype):
    """
    Parse configuration file and save settings into the configuration
    advanced dictionary.
    """

    if config.has_option(section, option):
        try:
            if datatype == OPTION_TYPE.BOOLEAN:
                value = config.getboolean(section, option) if config.get(section, option) else False
            elif datatype == OPTION_TYPE.INTEGER:
                value = config.getint(section, option) if config.get(section, option) else 0
            elif datatype == OPTION_TYPE.FLOAT:
                value = config.getfloat(section, option) if config.get(section, option) else 0.0
            else:
                value = config.get(section, option)
        except ValueError as ex:
            errMsg = "error occurred while processing the option "
            errMsg += f"'{option}' in provided configuration file ('{getUnicode(ex)}')"
            raise SqlmapSyntaxException(errMsg)

        conf[option] = value if value else None
    else:
        debugMsg = f"missing requested option '{option}' (section "
        debugMsg += f"'{section}') into the configuration file, "
        debugMsg += "ignoring. Skipping to next."
        logger.debug(debugMsg)

def configFileParser(configFile):
    """
    Parse configuration file and save settings into the configuration
    advanced dictionary.
    """

    global config

    debugMsg = "parsing configuration file"
    logger.debug(debugMsg)

    checkFile(configFile)
    configFP = openFile(configFile, "rb")

    try:
        config = UnicodeRawConfigParser()
        config.readfp(configFP)
    except Exception as ex:
        errMsg = f"you have provided an invalid and/or unreadable configuration file ('{getSafeExString(ex)}')"
        raise SqlmapSyntaxException(errMsg)

    if not config.has_section("Target"):
        errMsg = "missing a mandatory section 'Target' in the configuration file"
        raise SqlmapMissingMandatoryOptionException(errMsg)

    mandatory = any(
        config.has_option("Target", option)
        and config.get("Target", option)
        or cmdLineOptions.get(option)
        for option in (
            "direct",
            "url",
            "logFile",
            "bulkFile",
            "googleDork",
            "requestFile",
            "wizard",
        )
    )
    if not mandatory:
        errMsg = (
            "missing a mandatory option in the configuration file "
            + "(direct, url, logFile, bulkFile, googleDork, requestFile or wizard)"
        )
        raise SqlmapMissingMandatoryOptionException(errMsg)

    for family, optionData in optDict.items():
        for option, datatype in optionData.items():
            datatype = unArrayizeValue(datatype)
            configFileProxy(family, option, datatype)
