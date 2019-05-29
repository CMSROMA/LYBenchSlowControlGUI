#!/bin/sh

PARSED_OPTIONS=$(getopt -n "$0"  -o o:d: --long "output:,days:"  -- "$@")
#Bad arguments, something has gone wrong with the getopt command.
if [ $? -ne 0 ];
then
    echo "Usage: $0 -o outputDir -d days"
  exit 1
fi

eval set -- "$PARSED_OPTIONS"

outDir="/tmp"
days=7

while true;
do
  case "$1" in
  
    -o|--output)
      if [ -n "$2" ];
      then
	  outDir=$2
      fi
      shift 2;;

    -d|--days)
      if [ -n "$2" ];
      then
	  days=$2
      fi
      shift 2;;
 
    --)
      shift
      break;;
  esac
done

DATE=`date +%Y_%m_%d`
filename="LYBenchTempData_"${DATE}".root"
python2 ~/DAQ/LYBenchSlowControlGUI/temperatureDataToRoot.py -d ${days} -o ${outDir}/${filename}
