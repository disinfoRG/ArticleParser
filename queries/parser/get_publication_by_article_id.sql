-- :name get_publication_by_article_id :many
SELECT *
FROM publication_mapping as PM
  INNER JOIN publication as P
  ON PM.publication_id = P.publication_id AND PM.version = P.version
WHERE PM.article_id = :article_id
ORDER BY P.version ASC
