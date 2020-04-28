-- :name get_drive_by_name :one
SELECT
  drive_id, name, data
FROM
  drive
WHERE
  name = :name

-- :name update_drive_producer_dir_id :affected
UPDATE
  drive
SET
  data = JSON_SET(
    JSON_SET(data, CONCAT("$.dirs.producers.", :producer_id), :dir_id),
    CONCAT("$.files.producers.", :producer_id),
    JSON_OBJECT()
  )
WHERE
  name = :name

-- :name update_drive_file_id :affected
UPDATE
  drive
SET
  data = JSON_SET(data, CONCAT("$.files.producers.", :producer_id, ".", :filename), :file_id)
WHERE
  name = :name
