#!/bin/bash

#bwd from 3Mbps to 9Mbps
V=(250 375 500 625 750 875 1000 1125)
i=(1 2 6 3 0 2 7 5 4 6 2 1 0 0 1 6 3 2 5 7 5)

#delete any previous constraint
sudo ./wan_emulation.sh tc_del_egress docker0

cont=0
while [ 1 ]
do  
    kb=${V[i[cont]]}
    sudo ./wan_emulation.sh tc_egress 50 docker0 ${kb}
    sleep 5
    sudo ./wan_emulation.sh tc_del_egress docker0
    ((cont++))
done
