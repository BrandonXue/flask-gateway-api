# foreman start -m gateway=1,users=3,timelines=3
gateway: FLASK_APP=gateway flask run -p $PORT
users: FLASK_APP=users_api flask run -p $PORT
timelines: FLASK_APP=timelines_api flask run -p $PORT



# foreman start -m gateway=1,sandman=3,datasette=3
#gateway: FLASK_APP=gateway flask run -p $PORT
#sandman: sandman2ctl -p $PORT sqlite+pysqlite:///../mockroblog/mockroblog.db
#datasette: datasette -p $PORT --reload ../mockroblog/mockroblog.db
