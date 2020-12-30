# foreman start -m gateway=1,users=3,timelines=3,dms=3
gateway: FLASK_APP=api_pkg/gateway flask run -p $PORT
users: FLASK_APP=api_pkg/services/users_api flask run -p $PORT
timelines: FLASK_APP=api_pkg/services/timelines_api flask run -p $PORT
dms: FLASK_APP=api_pkg/services/dms_api flask run -p $PORT