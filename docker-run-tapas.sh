#!/bin/sh

PATH_TAPAS=$PWD
#gnome-terminal -e ./changeBwd.sh
docker run -it -v $PATH_TAPAS:/tapas/ --rm full_upgraded /bin/bash -c "cd /tapas && /tapas/run_tapas.sh ${1}"
