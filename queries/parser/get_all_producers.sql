-- :name get_all_producers :many
SELECT * FROM producer
LIMIT :limit
OFFSET :offset
