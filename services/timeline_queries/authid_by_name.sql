-- :name authid_by_name :one
SELECT id FROM users
WHERE username = :username;
