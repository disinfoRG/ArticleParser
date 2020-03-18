-- :name get_article_snapshots_by_site :many
SELECT
  A1.article_id, A1.snapshot_at
FROM ArticleSnapshot AS A1
JOIN Article AS A2 ON A1.article_id = A2.article_id
WHERE A2.site_id = :site_id
LIMIT :limit
OFFSET :offset
