
ArticleParser
===

ArticleParser is part of [0archive project](https://0archive.tw/).  Its purpose is to

1. pull raw data from several scraper databases,
2. translate raw data into a standardized format and save it to the database of ArticleParser, and then
3. publish the resulting dataset in the database to several places for storage.

An example of upstream scraper is [ZeroScraper](https://github.com/disinfoRG/ZeroScraper/) of 0archive.  Dataset publishing can currently output to local files or Google Drive folders.

There is a diagram of [0archive system architecture](https://g0v.hackmd.io/@chihao/0archive/https%3A%2F%2Fdocs.google.com%2Fpresentation%2Fd%2F1RPRAGsHJWNR87AW_L2v-GHCc4S5eFUPNFwcmCz0_eSw%2Fedit%23slide%3Did.p) to which you can refer.

The code runs on Python 3.7 or above.  The system is tested on MariaDB 10.3.

* [Installation Guide](https://g0v.hackmd.io/OgKshAg-SFau9xm_SuZRew?view)
* [Developer Guide](https://g0v.hackmd.io/7L3brtf3QQWyfYqa_nizFw?view)

