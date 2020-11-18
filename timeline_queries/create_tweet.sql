-- :name create_tweet :insert
INSERT INTO tweets(id, author_id, timestamp, content_text) 
VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = :author_id)+1, :author_id, current_timestamp, :content_text)
