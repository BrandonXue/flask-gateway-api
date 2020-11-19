-- :name home_timeline :many
SELECT username, content_text, timestamp FROM tweets, users
WHERE users.id = tweets.author_id AND tweets.author_id IN ( SELECT following_id FROM follows 
						WHERE :author_id = user_id)
ORDER BY tweets.timestamp DESC
LIMIT 25;


