PROJECT_PATH=$(dirname $(cd $(dirname $0) && pwd))

cd ${PROJECT_PATH}

LOG_PATH=${PROJECT_PATH}"/logs/main.log"

python3 -u ${PROJECT_PATH}/scripts/main.py $* 2>> ${LOG_PATH}