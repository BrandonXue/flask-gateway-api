# foreman start -m gateway=1,users=3,timelines=3,directmessages=3
gateway: FLASK_APP=gateway flask run -p $PORT
users: FLASK_APP=services/users_api flask run -p $PORT
timelines: FLASK_APP=services/timelines_api flask run -p $PORT
directmessages: FLASK_APP=services/direct_messages_api flask run -p $PORT
