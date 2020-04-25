#!/bin/bash

#bwd from 2Mbps to 1Mbps
V=(63 80)

# Seed random generator
RANDOM=$$$(date +%s)

#delete any previous constraint
sudo ./wan_emulation.sh tc_del_egress docker0


while [ 1 ]
do  
    kb=${V[$RANDOM % ${#V[@]}]}
    sudo ./wan_emulation.sh tc_egress 50 docker0 ${kb}
    sleep 5
    sudo ./wan_emulation.sh tc_del_egress docker0
done
