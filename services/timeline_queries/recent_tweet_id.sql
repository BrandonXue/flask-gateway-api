-- :name recent_tweet_id :one
SELECT MAX(id) AS id FROM tweets
WHERE :author_id = author_id;
