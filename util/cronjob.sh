echo $PWD
echo $PWD

cd /home/centos/pymessage

echo "KILLING SERVER PROCESS"
kill $(ps aux | grep '[p]ython3 server.py' | awk '{print $2}')

sleep 5

sudo lsof -t -i tcp:55555 | xargs kill -9

echo "pulling..."
git pull

echo "SERVER RESTART..."
python3 $PWD/server.py &


