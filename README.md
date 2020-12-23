## Introduction
A Flask gateway API featuring three microservices: users, timelines, and direct messages (DMs). This was created for a web back-end development class.


## Features

#### Basic Features
- A basic gateway API that connects to three microservices and distributes load to them in a round-robin fashion.
- Each service has a variety of operations with RESTful design (hopefully).
- Removal of services from the pool if any of them encounter an internal server error.
- Basic auth required before accedding all endpoints aside from creating an account and authentication.

#### Examples
The following examples are for the DMs service (uses DynamoDB):
- showcasing sendDirectMessageTo():
    - http -a user2:password POST http://localhost:5000/api/v1/dms to='user1' message='Have a nice day' quickreply="['No']"
- showcasing replyToDirectMessage():
    - http -a user1:password POST http://localhost:5000/api/v1/dms/2020-11-27T12:56:13.848139user2/replies message='No, thank you!'
- showcasing listDirectMessagesFor():
    - http -a user1:password GET http://localhost:5000/api/v1/dms
    - http -a user1:password GET http://localhost:5000/api/v1/dms timestamp='2020-11-27T12:55'
- showcasing listRepliesTo():
    - http -a user1:password GET http://localhost:5000/api/v1/dms/2020-11-27T09:54:59.540514user2/replies


## Running the API

#### Requirements
Tools:
- python 3
- foreman
- httpie
- dynamodb local
- AWS cli

Python modules:
- boto3
- botocore
- flask
- flask_api
- flask_basic_auth
- pugsql
- requests
- werkzeug.security

#### Usage
1. Start up dynamodb local by navigating to the directory it is located in, and running:
    - `java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb`
    - This can be done in one step with `zsh ./dynamo.sh` although you may need to modify the script depending on your platform.
  
2. Navigate to the project repository with another terminal emulator window.

3. Initialize the test databases.
    - The users and timelines test databases can be initialized through the `init` custom flask command of the users_api or the timelines_api flask apps.
    - The DMs database can be initalized through the `init` custom flask command of the direct_messsages_api flask app.
    - All databases will be automatically populated with test data.
    - This can be done in one step with `zsh ./init.sh`, although you may need to modify the script depending on your platform.
  
4. Using foreman, run:
    - `foreman start --formation gateway=1,users=3,timelines=3,directmessages=3 -p 5000`
    - This will start three instances of each microservice. The port must be configured to 5000 for development, because of the way config is set.
    - This can be done in one step with `zsh ./start.sh` although you may need to modify the script depending on your platform.

5. Begin making HTTP Requests to the API.


## Collaborators
- Brandon Xue
- Jacob Rapmund (Only for the users and timelines microservices. Jacob has his own version of everything else.)
