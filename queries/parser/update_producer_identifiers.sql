-- :name update_producer_identifiers :affected
UPDATE producer
SET identifiers = :identifiers
WHERE producer_id = :producer_id

