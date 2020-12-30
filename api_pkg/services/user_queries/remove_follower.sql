-- :name remove_follower :affected
DELETE FROM follows
WHERE
	user_id = (SELECT id FROM users WHERE username = :user_name) AND
	following_id = (SELECT id FROM users WHERE username = :followed_name)