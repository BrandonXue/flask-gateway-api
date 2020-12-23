# t = to
# fr = from
# ts = timestamp
# irt = in-reply-to
# msg = message
# qro = quick-reply-options
# mId = messageId

dm_table_schema = {
    'TableName': 'dms',
    'KeySchema': [
        {
            'AttributeName': 't',
            'KeyType': 'HASH'
        },
        {
            'AttributeName': 'mId',
            'KeyType': 'RANGE'
        }
    ],
    'AttributeDefinitions': [
        {
            'AttributeName': 't',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'mId',
            'AttributeType': 'S'
        },
        {
            'AttributeName': 'irt',
            'AttributeType': 'S'
        }
    ],
    'ProvisionedThroughput':{
        'ReadCapacityUnits': 50,
        'WriteCapacityUnits': 40
    },
    'GlobalSecondaryIndexes':[
    {
        'IndexName': 'replies',
        'KeySchema': [
            {
                'AttributeName': 'irt',
                'KeyType': 'HASH'
            },
            {
                'AttributeName': 'mId',
                'KeyType': 'RANGE'
            }
        ],
        'Projection': {
            'ProjectionType': 'ALL'
        },
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 40,
            'WriteCapacityUnits': 30
        }
    },
    {
        'IndexName': 'messageIds',
        'KeySchema': [
            {
                'AttributeName': 'mId',
                'KeyType': 'HASH'
            }
        ],
        'Projection': {
            'ProjectionType': 'INCLUDE',
            'NonKeyAttributes': ['t']
        },
        'ProvisionedThroughput': {
            'ReadCapacityUnits': 10,
            'WriteCapacityUnits': 10
        }
    }]
}