-- :name get_publications_by_parser_version :many
SELECT * FROM publication_mapping
WHERE
  JSON_EXTRACT(info, "$.parser.version") < :version
  -- XXX old version string
  OR JSON_EXTRACT(info, "$.parser.version") = "0.9.0"
LIMIT :limit
OFFSET :offset
