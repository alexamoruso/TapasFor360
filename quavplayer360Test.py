import glob
import os
import subprocess

prefix          = "/usr"
quavServerAddr  = "10.73.0.27"
#quavServerAddr = "127.0.0.1"
quavServerPort  = 8887

tracesPath      = prefix + "/share/mahimahi/traces/"

# shscript path
shScript        = os.getenv("PWD") + "/docker-run-tapas.sh"

tracesUp        = glob.glob("".join([tracesPath, "/*.up"])) # these two lines return the same results
tracesDown      = glob.glob("".join([tracesPath + "/*.down"])) # these two lines return the same results

#tracesUp       = glob.glob("".join([tracesPath, "/ATT-LTE-driving.up"]))
#tracesDown     = glob.glob("".join([tracesPath + "/ATT-LTE-driving.down"]))

videos          = ["/Elephant/Elephant"]

scalingFactors  = [480]
nViews          = [3]
segSizes        = [1]

# MahiMahi params
fixedDelays     = [0]

#tracesUp       = glob.glob("".join([tracesPath, "/*.up"]))
#tracesDown     = glob.glob("".join([tracesPath + "/*.down"]))
#videos         = [ "/Elephant/Elephant" ]
#scalingFactors = [ 480 ]
#nViews         = [ 3 ]
#segSizes       = [ 1 ]
#fixedDelays    = [ 0 ]

processQueue = {}

# open experimentMetadata file

# open experimentResult file


def run():
    i = 1
    for k in range(1, 10):
        for v in videos:
            for tu in tracesUp:
                for td in tracesDown:
                    for nv in nViews:
                        for sf in scalingFactors:
                            for ss in segSizes:
                                for fd in fixedDelays:
                                    if tu.split('.')[0] == td.split('.')[0]:
                                        # create process
                                        # scaled
                                        #'mm-delay', str(fd), 'mm-link', '--meter-all', str(tu), str(td), '--'
                                        
                                        
                                        p = subprocess.Popen(['mm-delay', str(fd), 'mm-link', '--meter-all', str(tu), str(td), '--', str(shScript),
                                                            "http://{}:{}/dash{}_{}_{}_{}s/new/playlist.m3u8".format(quavServerAddr, quavServerPort, v, nv, sf, ss)])

                                        #"http://{}:{}/dash{}_{}_{}_{}s/0/index_0.m3u8,".format(quavServerAddr, quavServerPort, v, nv, sf, ss)
                                        #"http://{}:{}/dash{}_{}_{}_{}s/1/index_1.m3u8,".format(quavServerAddr, quavServerPort, v, nv, sf, ss)
                                        # "http://{}:{}/dash{}_{}_{}_{}s/2/index_2.m3u8".format(quavServerAddr, quavServerPort, v, nv, sf, ss)])
                                        # full resolution
                                        #p = subprocess.Popen([ 'mm-delay', str(fd), 'mm-link', '--meter-all', str(tu), str(td), '--', 'chromium', '--autoplay-policy=no-user-gesture-required', '--no-default-browser-check', '--user-data-dir=/tmp/nonexistent{}'.format(datetime.datetime.now()), "http://{}:{}/test/index.html?url=http://{}:{}/DEMO{}_{}s/manifest.mpd".format(quavServerAddr, quavServerPort, quavServerAddr, quavServerPort, v, ss, i) ], stdout=subprocess.PIPE)

                                        # add process to processQueue
                                        processQueue[i] = p

                                        # start process
                                        output, errors = p.communicate()
                                        print errors
                                        p.wait()


                                        i = i+1


if __name__ == "__main__":
    from sys import argv
    run()

# close file
