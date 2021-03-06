mkdir -p logs
#cmd="cd `pwd`; echo \`pwd\` >&2; python crawl_kbb.py"
cmd="#!/bin/bash
cd /afs/cs.wisc.edu/u/s/a/saikat/public/html/Fall14/CS784/CS784-Data_Integration; 
echo \`pwd\` >&2;
python crawl_kbb.py;
"
echo $1
sleep_time=1000000
if [ "$1" = "kill" ];
then
    echo "Killing all"
    cmd="
#!/bin/bash
kill -9 \`ps -ef | grep crawl_kbb.py | grep -v 'grep' | awk '{print \$2}'\`
"
    sleep_time=100000
fi

echo $cmd
for X in 01 02 03 04 05 06 07 08 09 10 11 12 13 14 15 16 17 18 19 20 21 22 23 24 25 26 27 28 29 30 31 32 33 34 35 36 37 38 39 40
do
    Y=adelie-$X
    Z=galapagos-$X
    M=macaroni-$X
    ssh $USER@$Y 'bash -s' "$cmd" > logs/remote_log_$Y.txt &
    usleep $sleep_time
    ssh $USER@$Z 'bash -s' "$cmd" > logs/remote_log_$Z.txt &
    usleep $sleep_time
    ssh $USER@$M 'bash -s' "$cmd" > logs/remote_log_$M.txt &
    usleep $sleep_time
done

