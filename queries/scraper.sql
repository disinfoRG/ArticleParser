-- :name get_scraper_by_name :one
SELECT
  scraper_id, scraper_name, db_url_var, site_table_name, article_table_name, snapshot_table_name
FROM
  scraper
WHERE
  scraper_name = :scraper_name
