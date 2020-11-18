-- :name add_follower :affected
INSERT INTO follows (user_id, following_id) VALUES (
	(SELECT id FROM users WHERE username = :user_name), 
	(SELECT id FROM users WHERE username = :followed_name))