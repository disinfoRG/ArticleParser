from dotenv import load_dotenv

load_dotenv()
import os
import re
import pymysql
from pathlib import Path

url_pat = re.compile("^mysql.*://(.*?):(.*?)@(.*?)/(.*)$")
m = url_pat.match(os.getenv("DB_URL"))
db_user, db_pass, db_host, db_name = m.groups()

conn = pymysql.connect(host=db_host, user=db_user, passwd=db_pass, db=db_name)
try:
    with Path("snapshots.csv").open("w") as output:
        output.write("site_id,aritcle_id,url,filename\n")
        with conn.cursor() as cur:
            cur.execute("SELECT site_id FROM Site")
            sites = [str(row[0]) for row in cur.fetchall()]

            for site_id in sites:
                cur.execute(
                    f"""
                    SELECT
                      A1.site_id, A1.article_id, A1.url, A2.raw_data
                    FROM
                      Article AS A1
                      INNER JOIN ArticleSnapshot AS A2
                      ON A1.article_id = A2.article_id
                    WHERE A1.site_id = {site_id}
                    LIMIT 1
                    """
                )
                row = cur.fetchone()
                if row is None:
                    print(f"not found for site {site_id}")
                    continue
                filename = "snapshot%06d.html" % int(site_id)
                output.write(
                    f"{str(row[0])},{str(row[1])},{str(row[2])},{filename}" + "\n"
                )
                with Path(filename).open("w") as f:
                    f.write(str(row[3]))
                print(f"got site {site_id}")
finally:
    conn.close()
