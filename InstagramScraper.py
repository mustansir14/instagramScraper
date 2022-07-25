import os
import requests
import urllib.request
import time
import logging
from includes.models import *
from includes.DB import DB
from config import *
from datetime import datetime
from multiprocessing import Process, Queue
import sys
from sys import platform
import argparse
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)


class InstagramScraper:

    def __init__(self, use_db=True) -> None:

        self.url = "https://i.instagram.com/api/v1/users/web_profile_info"

        self.headers = {
            "authority": "i.instagram.com",
            "accept": "*/*",
            "accept-language": "en-US,en;q=0.9",
            "origin": "https://www.instagram.com",
            "referer": "https://www.instagram.com/",
            "sec-ch-ua": "^\^.Not/A",
            "sec-ch-ua-mobile": "?0",
            "sec-ch-ua-platform": "^\^Windows^^",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/103.0.0.0 Safari/537.36",
            "x-asbd-id": "198387",
            "x-ig-app-id": "936619743392459",
            "x-ig-www-claim": "0"
        }

        self.use_db = use_db
        if use_db:
            self.db = DB(host=DB_HOST, username=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
        
        os.makedirs(FILES_DIR.rstrip("/") + "/post/image", exist_ok=True)
        os.makedirs(FILES_DIR.rstrip("/") + "/post/video", exist_ok=True)

    def scrape_profile(self, profile_url) -> Profile:

        logging.info("Scraping Profile: " + profile_url)
        username = profile_url.strip("/").split("/")[-1]
        querystring = {"username":username}
        profile = Profile()
        profile.username = username
        response = requests.get(self.url, headers=self.headers, params=querystring)
        if response.status_code != 200:
            profile.status = "error"
            profile.log = str(response.status_code) + " Error requesting Instagram API: " + response.text
            logging.error(profile.log)
            return profile
        user_json = response.json()["data"]["user"]
        profile.username = username
        profile.description = user_json["biography"]
        profile.no_of_followers = user_json["edge_followed_by"]["count"]
        profile.no_of_following = user_json["edge_follow"]["count"]
        profile.no_of_posts = user_json["edge_owner_to_timeline_media"]["count"]
        profile.category = user_json["category_name"]
        profile.status = "success"
        if self.use_db:
            self.db.insert_or_update_profile(profile)
        logging.info("Scraping Posts for " + profile_url)
        edges = user_json["edge_felix_video_timeline"]["edges"] + user_json["edge_owner_to_timeline_media"]["edges"]
        ids_done = []
        for edge in edges:
            if edge["node"]["id"] in ids_done:
                continue
            post = self.scrape_post(edge=edge)
            profile.posts.append(post)
            if self.use_db:
                self.db.insert_or_update_post(post)
            ids_done.append(post.id)

        return profile


    def scrape_post(self, id=None, edge=None) -> Post:

        if not id and not edge:
            raise Exception("Either ID or edge is needed.")
        
        if not edge:
            
            self.db.cur.execute("SELECT username from post where id = %s;", (id, ))
            data = self.db.cur.fetchall()
            if data:
                username = data[0][0]
            else:
                raise Exception("Post with ID %s not found in DB. Can't determine username." % id)
            res = requests.get(self.url, headers=self.headers, params={"username":username})
            user_json = res.json()["data"]["user"]
            edges = user_json["edge_felix_video_timeline"]["edges"] + user_json["edge_owner_to_timeline_media"]["edges"]
            edge_found = False
            for edge in edges:
                if edge["node"]["id"] == id:
                    edge_found = True
                    break
            if not edge_found:
                raise Exception("Post with ID %s not found for profile %s. Only latest 12 posts can be fetched so maybe the post is old." % (id, username))

        post = Post()
        node = edge["node"]
        post.id = node["id"]
        post.username = node["owner"]["username"]
        post.caption = node["edge_media_to_caption"]["edges"][0]["node"]["text"]
        post.caption = " ".join(filter(lambda x:x[0]!='#' or x[0] != '@', post.caption.split()))
        post.date_posted = datetime.fromtimestamp(node["taken_at_timestamp"])
        post.no_of_likes = node["edge_liked_by"]["count"]
        post.is_video = False
        if node["__typename"] == "GraphSidecar":
            post_edges = node["edge_sidecar_to_children"]["edges"]
        else:
            post_edges = [edge]
            if node["__typename"] == "GraphVideo":
                post.is_video = True
        for i, post_edge in enumerate(post_edges):
            node = post_edge["node"]
            if node["__typename"] == "GraphVideo":
                if i > 0:
                    post.media_paths.append(FILES_DIR.rstrip("/") + "/post/video/" + str(post.id) + "_" + str(i) + ".mp4")
                else:
                    post.media_paths.append(FILES_DIR.rstrip("/") + "/post/video/" + str(post.id) + ".mp4")
                if not os.path.isfile(post.media_paths[-1]):
                    urllib.request.urlretrieve(node["video_url"], post.media_paths[-1])
            elif node["__typename"] == "GraphImage":
                if i > 0:
                    post.media_paths.append(FILES_DIR.rstrip("/") + "/post/image/" + str(post.id) + "_" + str(i) + ".jpg")
                else:
                    post.media_paths.append(FILES_DIR.rstrip("/") + "/post/image/" + str(post.id) + ".jpg")
                if not os.path.isfile(post.media_paths[-1]):
                    res = requests.get(node["display_url"])
                    with open(post.media_paths[-1], "wb") as f:
                        f.write(res.content)

        post.status = "success"
        return post


    def bulk_scrape(self, urls, num_threads):

        if platform == "linux" or platform == "linux2":
            urls_to_scrape = Queue()
            for url in urls:
                urls_to_scrape.put(url)
            processes = []
            for i in range(num_threads):
                processes.append(Process(target=self.scrape_urls_from_queue, args=(urls_to_scrape, )))
                processes[i].start()

            for i in range(num_threads):
                processes[i].join()
        else:
            for url in urls:
                self.scrape_url(url)
    
    
    def scrape_urls_from_queue(self, q):

        try:
            scraper = InstagramScraper()
            
            while q.qsize():
                company_url = q.get()
                scraper.scrape_profile(company_url)   
        except:
            pass



if __name__ == "__main__":

    parser = argparse.ArgumentParser(description="InstagramScraper CLI to grab company and reviews from URL")
    parser.add_argument("--bulk_scrape_urls_file", nargs='?', type=str, default=False, help="File to read urls for bulk scrape, one url per line.")
    parser.add_argument("--urls", nargs='*', help="url(s) for scraping. Separate by spaces")
    parser.add_argument("--no_of_threads", nargs='?', type=int, default=1, help="No of threads to run. Default 1")
    parser.add_argument("--log_file", nargs='?', type=str, default=None, help="Path for log file. If not given, output will be printed on stdout.")
    parser.add_argument("--grabber-instagram-mustansir", nargs='?', type=bool, default=False, help="Only mark to kill all")
    if len(sys.argv) == 1:
        parser.print_help(sys.stderr)
        sys.exit(1)
    args = parser.parse_args()
    # setup logging based on arguments
    if args.log_file and platform == "linux" or platform == "linux2":
        logging.basicConfig(filename=args.log_file, filemode='a',format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    elif platform == "linux" or platform == "linux2":
        logging.basicConfig(format='%(asctime)s Process ID %(process)d: %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    elif args.log_file:
        logging.basicConfig(filename=args.log_file, filemode='a',format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)
    else:
        logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

    scraper = InstagramScraper()
    if args.bulk_scrape_urls_file:
        scraper.bulk_scrape(num_threads=args.no_of_threads)
    else:
        for url in args.urls:
            profile = scraper.scrape_profile(url)
            logging.info("Profile for %s scraped successfully.\n" % profile.username)
            try:
                print(profile)
            except Exception as e:
                print(e)
            print("\n")
            for i, post in enumerate(profile.posts, start=1):
                print("Post# " + str(i))
                try:
                    print(post)
                except Exception as e:
                    print(e)
                print("\n")


