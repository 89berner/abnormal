find tmp/ -name "*.*" -print0 | xargs -0 rm
time python abnormal.py --url $1 --proxies=$2 --threads=10 -lDEBUG -s=1 -c=1 -n=1
