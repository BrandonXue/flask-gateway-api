-- :name email_exists :scalar
SELECT COUNT(id) FROM users
WHERE email = :user_email;