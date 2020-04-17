-- :name insert_publication_mapping :insert
INSERT INTO publication_mapping
  (article_id, snapshot_at, publication_id, version, info)
VALUES
  (:article_id, :snapshot_at, :publication_id, :version, :info)

-- :name update_publication_mapping :affected
UPDATE publication_mapping
SET
  publication_id = :publication_id,
  version = :version,
  info = :info
WHERE
  article_id = :article_id
  AND snapshot_at = :snapshot_at

