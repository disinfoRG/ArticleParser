-- :name get_all_sites :many
SELECT * FROM Site
LIMIT :limit
OFFSET :offset
