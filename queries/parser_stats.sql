-- :name compute_parser_stats :affected
REPLACE
  parser_stats (parser_name, processed_date, producer_id, processed_count)
SELECT
  "publication" AS parser_name,
  DATE_FORMAT(FROM_UNIXTIME(JSON_EXTRACT(PM.info, "$.last_processed_at")), "%Y-%m-%d") AS processed_date,
  P.producer_id AS producer_id,
  COUNT(*) AS processed_count
FROM publication_mapping as PM
  JOIN publication as P
  ON PM.publication_id = P.publication_id AND PM.version = P.version
WHERE JSON_EXTRACT(PM.info, "$.last_processed_at") BETWEEN :start AND :end
GROUP BY processed_date, producer_id
