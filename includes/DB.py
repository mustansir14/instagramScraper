import mariadb
from includes.models import *
from datetime import datetime
import logging

class DB:

    def __init__(self, host, username, password, db_name) -> None:

        self.con = mariadb.connect(host=host, user=username, password=password, db=db_name)
        self.cur = self.con.cursor()

    def insert_or_update_profile(self, profile : Profile):
        
        sql = """INSERT INTO profile (username, description, category, no_of_posts, no_of_followers, 
        no_of_following, date_inserted, date_updated, status, log) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, 
        %s) ON DUPLICATE KEY UPDATE description=%s, category=%s, no_of_posts=%s, no_of_followers=%s, 
        no_of_following=%s, date_updated=%s, status=%s, log=%s;"""
        args = (profile.username, profile.description, profile.category, profile.no_of_posts, 
        profile.no_of_followers, profile.no_of_following, datetime.now(), datetime.now(), profile.status, 
        profile.log, profile.description, profile.category, profile.no_of_posts, profile.no_of_followers, 
        profile.no_of_following, datetime.now(), profile.status, profile.log, )
        try:
            self.cur.execute(sql, args)
            logging.info(f"Profile {profile.username} added/updated to DB.")
            self.con.commit()
        except Exception as e:
            logging.error(f"Error saving profile {profile.username} to DB. {str(e)}")

    def insert_or_update_post(self, post: Post):

        sql = """INSERT INTO post (id, username, date_posted, caption, no_of_likes, is_video, media_paths, 
        date_inserted, date_updated, status, log) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
        %s) ON DUPLICATE KEY UPDATE username=%s, date_posted=%s, caption=%s, no_of_likes=%s, 
        is_video=%s, media_paths=%s, date_updated=%s, status=%s, log=%s;"""
        args = (post.id, post.username, post.date_posted, post.caption, post.no_of_likes, 
        post.is_video, str(post.media_paths), datetime.now(), datetime.now(), post.status, 
        post.log, post.username, post.date_posted, post.caption, post.no_of_likes, 
        post.is_video, str(post.media_paths), datetime.now(), post.status, post.log, )
        try:
            self.cur.execute(sql, args)
            logging.info(f"Post {post.id} for profile: {post.username} added/updated to DB.")
            self.con.commit()
        except Exception as e:
            logging.error(f"Error saving Post {post.id} for profile: {post.username} to DB. {str(e)}")

