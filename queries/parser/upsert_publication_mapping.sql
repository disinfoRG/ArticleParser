-- :name upsert_publication_mapping :insert
INSERT INTO publication_mapping
  (article_id, snapshot_at, publication_id, info)
VALUES
  (:article_id, :snapshot_at, :publication_id, :info)
ON DUPLICATE KEY UPDATE
  article_id = :article_id, snapshot_at = :snapshot_at, publication_id = :publication_id, info = :info
