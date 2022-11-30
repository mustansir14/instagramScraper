from flask import Flask, json, request, Response
from InstagramScraper import InstagramScraper
from includes.models import Profile
from includes.DB import DB
from ast import literal_eval
from config import *
import logging, json, re, validators
logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %H:%M:%S', level=logging.INFO)

api = Flask(__name__)

@api.route('/api/v1/scrape/profile', methods=['GET'])
def grab_company():

    if "id" not in request.args:
        return {"status": "error", "message": "missing id argument"}
    
    try:
        scraper = InstagramScraper()
        profile = scraper.scrape_profile(request.args["id"])
        for i in range(len(profile.posts)):
            profile.posts[i] = vars(profile.posts[i])
        return {"status": "success", "profile": vars(profile)}
    except Exception as e:
        logging.error(str(e))
        return {"status": "error", "message": str(e)}, 300

@api.route('/api/v1/scrape/post', methods=['GET'])
def grab_post():

    if "id" not in request.args:
        return {"status": "error", "message": "missing id argument"}
    
    try:
        scraper = InstagramScraper()
        post = scraper.scrape_post(request.args["id"])
        return {"status": "success", "post": vars(post)}
    except Exception as e:
        logging.error(str(e))
        return {"status": "error", "message": str(e)}, 300

@api.route('/api/v1/scrape/reels/<username>', methods=['GET'])
def grab_reels(username):

    try:
        scraper = InstagramScraper()
        profile = scraper.scrape_profile(username, get_only_reels=True)
        for i in range(len(profile.posts)):
            profile.posts[i] = vars(profile.posts[i])
        return {"Status": "success", "reels": profile.posts}
    except Exception as e:
        logging.error(str(e))
        return {"status": "error", "message": str(e)}, 300


@api.route('/v1/find/profile', methods=['GET'])
def find_profile():

    if not "url" in request.args:
        return {"success": False, "errors": ["Please provide url"]}

    url = request.args['url']

    if not validators.url(url):
        return {"success": False, "errors": ["Url not valid"]}

    url = re.sub('\?*$', "", url)
    url = url.strip("?/ \t\r\n")
    url = url.split('/')
    url = url[-1]
        
    db = DB(host=DB_HOST, username=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
    db.cur.execute(f"SELECT username from profile where username = '{url}';")
    results = db.cur.fetchall()
    if results:
        return { "success": True, "data": results[0][0]}

    return { "success": False, "errors": [f"No profile id match: {url}"]}
    
@api.route('/v1/get/posts', methods=['GET'])
def get_posts():
    if "id" not in request.args:
        return {"success": False, "errors": ["missing id argument"]}
        
    if "offset" not in request.args:
        return {"success": False, "errors": ["missing offset argument"]}

    limit = 100
        
    db = DB(host=DB_HOST, username=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
    rows = db.queryArray("SELECT * from post where username=%s order by id limit %d, %d",( request.args['id'], int( request.args['offset'] ),limit, ))
    
    for rowNbr, row in enumerate(rows):
        row['images'] = [];
        row['videos'] = [];
        
        if row['media_paths']:
            for media in literal_eval(row['media_paths']):
                parts = media.split('/')
                if media.find( "/video/" ) != -1:
                    row['videos'].append( parts[-1] )
                else:
                    row['images'].append( parts[-1] )
                    
        rows[rowNbr] = row
    
    return Response(json.dumps({'success': True, 'data': rows},default=str),  mimetype='application/json')
    

if __name__ == "__main__":
    api.run(host='0.0.0.0', port=3050)