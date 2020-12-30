echo "Note: This file was meant for personal use. Please modify path to use." 
cd ~/Applications/dynamodb_local_latest/
java -Djava.library.path=./DynamoDBLocal_lib -jar DynamoDBLocal.jar -sharedDb

# Handy queries
#aws dynamodb list-tables --endpoint-url http://localhost:8000