# Please run this script from the directory with the Procfile
foreman start --formation gateway=1,users=3,timelines=3,dms=3 -p 5000
