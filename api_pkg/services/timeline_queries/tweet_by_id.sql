-- :name tweet_by_id :one
SELECT username, content_text, timestamp FROM tweets, users
WHERE tweets.id = :id AND author_id = :author_id AND users.id = :author_id;
