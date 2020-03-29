-- :name get_all_publications :many
SELECT * FROM publication
LIMIT :limit
OFFSET :offset
