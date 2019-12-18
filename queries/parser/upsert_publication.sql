-- :name upsert_publication :insert
INSERT INTO publication (publication_id, producer_id, canonical_url, title, publication_text, urls)
VALUES
(:publication_id, :producer_id, :canonical_url, :title, :publication_text, :urls)
ON DUPLICATE KEY UPDATE
canonical_url = :canonical_url, title = :title, publication_text = :publication_text, urls = :urls
