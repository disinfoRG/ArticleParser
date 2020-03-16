-- :name get_producer_by_id :one
SELECT * FROM producer
WHERE producer_id = :producer_id
