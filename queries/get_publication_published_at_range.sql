-- :name get_publication_published_at_range :one
SELECT
  MIN(published_at) as start, MAX(published_at) as end
FROM publication
WHERE

-- :name get_publication_published_at_range_by_producer :one
SELECT
  MIN(published_at) as start, MAX(published_at) as end
FROM publication
WHERE
  producer_id = :producer_id
