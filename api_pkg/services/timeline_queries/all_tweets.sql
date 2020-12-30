-- :name all_tweets :many
SELECT username, content_text, timestamp FROM tweets, users
WHERE tweets.author_id = users.id
ORDER BY tweets.timestamp DESC
LIMIT 25;
