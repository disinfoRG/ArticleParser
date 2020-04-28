-- :name get_scraper_by_name :one
SELECT
  scraper_id, scraper_name, data
FROM
  scraper
WHERE
  scraper_name = :scraper_name
