from flask import Flask, json, request, Response
from InstagramScraper import InstagramScraper
from includes.models import Profile
from includes.DB import DB
from config import *
import logging, json
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


@api.route('/api/v1/scrape/find/profile', methods=['GET'])
def find_profile():

    if "name" in request.args:
        field = "username"
    elif "web" in request.args:
        field = "web"
    elif "url" in request.args:
        field = "url"
    else:
        return {"status": "error", "message": "Please provide one of these parameters: name, web, url"}, 400
    
    db = DB(host=DB_HOST, username=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
    db.cur.execute(f"SELECT username from profile where {field} like '%{request.args[field.replace('user', '')]}%';")
    results = db.cur.fetchall()
    if results:
        return {"username": results[0][0]}
    return {"message": "No profile matched."}, 404
    
@api.route('/api/v1/scrape/get/posts', methods=['GET'])
def get_posts():
    if "id" not in request.args:
        return {"success": False, "errors": ["missing id argument"]}
        
    if "offset" not in request.args:
        return {"success": False, "errors": ["missing offset argument"]}
        
    db = DB(host=DB_HOST, username=DB_USER, password=DB_PASSWORD, db_name=DB_NAME)
    rows = db.queryArray("SELECT * from post where username=%s order by id limit %d, 500",( request.args['id'], int( request.args['offset'] ), ))
    
    for rowNbr, row in enumerate(rows):
        row['images'] = [];
        row['videos'] = [];
        
        if row['media_paths']:
            print(row['media_paths'])
            for media in json.loads(row['media_paths']):
                print(media)
                
        rows[rowNbr] = row
    
    return Response(json.dumps(rows,default=str),  mimetype='application/json')
    

if __name__ == "__main__":
    api.run(host='0.0.0.0', port=3050)