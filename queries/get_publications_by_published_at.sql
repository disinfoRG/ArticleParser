-- :name get_publications_by_published_at :many
SELECT * FROM publication
WHERE
  published_at >= :start
  AND published_at < :end
LIMIT :limit
OFFSET :offset

-- :name get_publications_by_producer_published_at :many
SELECT * FROM publication
WHERE
  producer_id = :producer_id
  AND published_at >= :start
  AND published_at < :end
LIMIT :limit
OFFSET :offset
