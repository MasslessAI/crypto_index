#!/bin/bash

reportErr() {
    echo "$1"
    exit 3
    }  

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PYTHON='/usr/bin/python3'


if [[ $# -gt 0 ]]
then
    while [[ "$1" != "" ]];
    do
        case $1 in
            -p  )  shift
                    prodDir="$1";;
            -t  )  shift
                    loadFileTemplate="$1";;
            -b  )  shift
                    bufferDays="$1";;
            # -a  )  shift
                    # skip_att="$1";;
            # --report ) normal_run="False"; run_report="True";;
            # --impact ) normal_run="False"; run_impact="True";;            
        esac
    shift
    done
fi

today_date=$(date +%Y%m%d)
start_date=$(date +%Y-%m-%dT00:00:00 -d "$bufferDays days ago")
#start_date='2018-06-15T00:00:00'

runDir=$prodDir/dynamic_$today_date
[[ ! -d $runDir ]] && mkdir -p $runDir
#[[ $? -ne 0 ]] && reportErr "Unable to mkdir $runDir"

inputDir=$runDir/input
[[ ! -d $inputDir ]] && mkdir $inputDir
#[[ $? -ne 0 ]] && reportErr "Unable to mkdir $inputDir"

logDir=$runDir/log
[[ ! -d $logDir ]] && mkdir $logDir
#[[ $? -ne 0 ]] && reportErr "Unable to mkdir $logDir"

loadFile=$inputDir/loadFile_${today_date}.csv
cp $loadFileTemplate $loadFile
sed -i s#"start_yyyymmddThhmmss"#${start_date}#g $loadFile
sed -i s#"end_yyyymmddThhmmss"#""#g $loadFile

apiKeyFile=$prodDir/cfg/API_keys.cfg
[[ ! -f $apiKeyFile ]] && reportErr "$apiKeyFile does not exist!"

echo "`date` [INFO]: $PYTHON $SCRIPT_DIR/LoadSymbolToDB.py $apiKeyFile $loadFile > $logDir/loadSymbolToDB.$today_date.log 2>&1"
$PYTHON $SCRIPT_DIR/LoadSymbolToDB.py $apiKeyFile $loadFile > $logDir/loadSymbolToDB.$today_date.log 2>&1





