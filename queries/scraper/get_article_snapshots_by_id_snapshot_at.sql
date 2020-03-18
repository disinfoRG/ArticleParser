-- :name get_article_snapshots_by_id_snapshot_at :one
SELECT
  *,
  Article.site_id AS site_id,
  Article.first_snapshot_at AS first_seen_at,
  Article.last_snapshot_at AS last_updated_at,
  Article.article_type AS article_type
FROM ArticleSnapshot
JOIN Article ON ArticleSnapshot.article_id = Article.article_id
WHERE Article.article_id = :article_id AND snapshot_at = :snapshot_at
