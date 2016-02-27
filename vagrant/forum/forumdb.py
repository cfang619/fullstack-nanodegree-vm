#
# Database access functions for the web forum.
# 

import time
import psycopg2
import bleach

## Database connection
DB = []

## Get posts from database.
def GetAllPosts():
    '''Get all the posts from the database, sorted with the newest first.

    Returns:
      A list of dictionaries, where each dictionary has a 'content' key
      pointing to the post content, and 'time' key pointing to the time
      it was posted.
    '''
    ## old code for ref
    #posts = [{'content': str(row[1]), 'time': str(row[0])} for row in DB]

    ## open connnection with psql db and retrieve cursor
    conn = psycopg2.connect("dbname=forum")
    curs = conn.cursor();
    ## insert new  content into specified table/column
    table = "posts"
    content_col = "content"
    time_col = "time"
    SQL = "SELECT %s,%s FROM %s ORDER BY %s DESC" % (content_col, time_col, table, time_col)
    curs.execute(SQL);
    db_data = curs.fetchall()

    ## convert into array of hashes
    posts = [{'content': str(bleach.clean(str(row[0]))), 'time': str(row[1])} for row in db_data]
    
    conn.close()

    return posts

## Add a post to the database.
def AddPost(content):
    '''Add a new post to the database.

    Args:
      content: The text content of the new post.
    '''

    ## open connnection with psql db and retrieve cursor
    conn = psycopg2.connect("dbname=forum")
    curs = conn.cursor();
    ## insert new  content into specified table/column
    table = 'posts'
    col = 'content'
    SQL = 'INSERT INTO %s (%s) values (%s)' % (table, col, "%s")
    curs.execute(SQL, (bleach.clean(content),));
    
    ## commit change to db
    conn.commit()
    conn.close()
    #t = time.strftime('%c', time.localtime())
    #DB.append((t, content))
