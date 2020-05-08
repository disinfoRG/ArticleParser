-- :name compute_publication_stats :affected
REPLACE
  publication_stats (published_date, producer_id, published_count)
SELECT
  DATE_FORMAT(FROM_UNIXTIME(published_at), "%Y-%m-%d") AS published_date,
  producer_id AS producer_id,
  COUNT(*) AS published_count
FROM publication
WHERE published_at BETWEEN :start AND :end
GROUP BY published_date, producer_id
