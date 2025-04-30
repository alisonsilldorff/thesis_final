# Princeton University Computer Science Senior Thesis: A Digital Humanities Analysis of the Broadway Musical
This project was completed over the course of my senior year at Princeton University. It is a data analysis of the Broadway Musical, culminating in a 76 page research paper. Using the Selenium library in Python, I scraped data from IBDB, and organized these data into a MySQL database. I also scraped data from TMDB and Letterboxd, also included in my database. Advised by Professor Brian Kernighan.

## Abstract
How can data deepen our understanding of Broadway musicals, their history, their actors, and their writers? This project is a data-driven digital humanities approach to understanding the Broadway musical and its related genres on Broadway. Through data collected from the Internet Broadway Database (IBDB), this project reveals the current limitations of digital theatre records and data, which in turn demonstrate the definitional challenges of this form that make it both difficult to work with and fascinating to parse. The data are analyzed to explore the development of the musical genre, the history of screen musicals, and historical demographic and career information about Broadway musical actors and writers. These analyses employ quantitative reasoning to understand theatre narratives in terms of the writers that defined the genre, examine structural gender inequality in the theatre industry, and support and question historical accounts of the Broadway musical. Furthermore, these analyses emphasize the need for further data-driven theatre research and interdisciplinary approaches to musical theatre scholarship.

## Files
**SENIOR_THESIS_FINAL.pdf** The full written research paper

### Scraping and Cleaning files
**fix_db.py** used to fix closing dates of certain rows  
**generate_ids.py** Using the property and sequence digits that have been generated, get the tag id and make a full ID  
**ibdb_scrape_details.py** scrape IBDB data from a single page for various musical theater metrics  
**ibdb_scrape_urls.py** Scrape URLs from an IBDB search page  
**misc_sql_work.py** workspace for cleaning and organizing MySQL database  
**populate_db.py** Populates the shows portion of the DB  
**scrape_ltbxd.py** scrape all movies from a set of list URLs from Letterboxd  
**scrape_tmdb.py** scrape movies from TMDB  

### Analysis files
**analysis_work_2.ipynb** Preliminary analyses  
**analysis_work_exploration2.ipynb** Uses SQL database to analyze people data (actors and writers)  
**analysis_work_exploration3.ipynb** Uses SQL database to analyze movie musical data  
**sql_analysis_work.ipynb** Uses SQL database to analyze overall metrics  
