-- :name user_tweets :many
SELECT username, content_text, timestamp FROM tweets, users
WHERE author_id = :author_id AND users.id = :author_id
ORDER BY tweets.timestamp DESC
LIMIT 25;
