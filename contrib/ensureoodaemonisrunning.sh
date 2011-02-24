#! /bin/bash

PORT=8100

if nc -z localhost $PORT; then
 echo "OO is already answering on port $PORT";
else
 echo "Starting OO on port $PORT";
 soffice -headless -accept="socket,port=$PORT;urp;"
fi

