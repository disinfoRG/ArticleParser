-- :name get_all_article_snapshots :many
SELECT *, Article.site_id AS site_id FROM ArticleSnapshot
JOIN Article ON ArticleSnapshot.article_id = Article.article_id
LIMIT :limit
OFFSET :offset
