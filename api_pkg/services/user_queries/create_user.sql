-- :name create_user :insert
INSERT INTO users (username, email, pw_hash)
	VALUES (:user_name, :user_email, :pw_hash);