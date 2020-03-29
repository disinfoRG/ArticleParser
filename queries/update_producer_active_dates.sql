-- :name update_producer_active_dates :affected
UPDATE producer
SET
  first_seen_at = LEAST(COALESCE(first_seen_at, :published_at), :published_at),
  last_updated_at = GREATEST(COALESCE(last_updated_at, :published_at), :published_at)
WHERE producer_id = :producer_id
