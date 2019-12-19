-- :name upsert_publication :insert
INSERT INTO publication
  (publication_id, producer_id, canonical_url, title, publication_text, first_seen_at, last_updated_at, urls, hashtags, keywords, tags)
VALUES
  (:publication_id, :producer_id, :canonical_url, :title, :publication_text, :first_seen_at, :last_updated_at, :urls, :hashtags, :keywords, :tags)
ON DUPLICATE KEY UPDATE
  canonical_url = :canonical_url, title = :title, publication_text = :publication_text, first_seen_at = :first_seen_at, last_updated_at = :last_updated_at, urls = :urls, hashtags = :hashtags, keywords = :keywords, tags = :tags
