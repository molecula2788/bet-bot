#!/bin/bash

MYSQL_ROOT_PASSWORD=REPLACE_WITH_MYSQL_ROOT_PASSWORD
MYSQL_BOT_PASSWORD=REPLACE_WITH_MYSQL_PASSWORD

echo 'Setting up db'

docker run --rm -v $PWD/db-data:/var/lib/mysql \
       -e MYSQL_ROOT_PASSWORD=$MYSQL_ROOT_PASSWORD \
       -e MYSQL_USER=bot \
       -e MYSQL_PASSWORD=$MYSQL_BOT_PASSWORD \
       -e MYSQL_DATABASE=bot \
       -e MYSQL_HOST=db \
       mariadb:10.7 &> log &

pid=$!

while true; do
    n=$(grep 'mariadb.org binary distribution' log | wc -l)

    if [ $n = 2 ]; then
	break
    fi

    sleep 0.5
done

kill -QUIT $pid
wait $pid

echo 'Loading db data'

docker run --name mysql-tmp --rm -v $PWD/db-data:/var/lib/mysql mariadb:10.7 &> log &
pid=$!

while true; do
    n=$(grep 'mariadb.org binary distribution' log | wc -l)

    if [ $n = 1 ]; then
	break
    fi

    sleep 0.5
done

docker exec -i mysql-tmp mysql -u bot -p$MYSQL_BOT_PASSWORD bot < db.sql

docker exec -i mysql-tmp mysql -u bot -p$MYSQL_BOT_PASSWORD bot -e "INSERT INTO bot_config(name, value) values('channel_id','REPLACE_WITH_CHANNEL_ID')"

kill -QUIT $pid
wait $pid
