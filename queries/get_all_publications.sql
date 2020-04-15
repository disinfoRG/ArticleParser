-- :name get_all_publications :many
SELECT * FROM publication
LIMIT :limit
OFFSET :offset

-- :name get_all_publications_by_producer :many
SELECT * FROM publication
WHERE producer_id = :producer_id
LIMIT :limit
OFFSET :offset
