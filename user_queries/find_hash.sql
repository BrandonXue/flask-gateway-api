-- :name find_hash :scalar
SELECT COALESCE(pw_hash, 0) FROM users
WHERE username = :user_name;