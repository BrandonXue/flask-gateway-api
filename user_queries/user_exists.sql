-- :name user_exists :scalar
SELECT COUNT(id) FROM users
WHERE username = :user_name;