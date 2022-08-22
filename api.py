from flask import Flask, json, request
from InstagramScraper import InstagramScraper
import logging
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
        return {"status": "error", "message": str(e)}

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
        return {"status": "error", "message": str(e)}


if __name__ == "__main__":
    api.run(host='0.0.0.0', port=80)