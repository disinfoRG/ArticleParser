-- :name create_publication :insert
INSERT INTO publication (publication_id, producer_id, canonical_url, title, publication_text, urls)
VALUES
(:publication_id, :producer_id, :canonical_url, :title, :publication_text, :urls)
