class Profile:

    def __init__(self):

        self.username = None
        self.description = None
        self.no_of_posts = None
        self.no_of_followers = None
        self.no_of_following = None
        self.web = None
        self.category = None
        self.status = None
        self.log = None
        self.posts = []

    def __str__(self):

        return_string = ""
        if self.username:
            return_string += "Username: " + self.username + "\n"
        if self.description:
            return_string += "Description: " + self.description + "\n"
        if self.category:
            return_string += "Category: " + self.category + "\n"
        if self.no_of_posts:
            return_string += "Posts: " + str(self.no_of_posts) + "\n"
        if self.no_of_followers:
            return_string += "Followers: " + str(self.no_of_followers) + "\n"
        if self.no_of_following:
            return_string += "Following: " + str(self.no_of_following) + "\n"

        return return_string

class Post:

    def __init__(self) -> None:
        
        self.id = None
        self.username = None
        self.date_posted = None
        self.caption = None
        self.no_of_likes = None
        self.is_video = None
        self.media_paths = []
        self.status = None
        self.log = None

    def __str__(self) -> str:
        
        return_string = ""
        if self.id:
            return_string += "ID: " + str(self.id) + "\n"
        if self.username:
            return_string += "Username: " + self.username + "\n"
        if self.date_posted:
            return_string += "Date Posted: " + str(self.date_posted) + "\n"
        if self.caption:
            return_string += "Caption: " + self.caption + "\n"
        if self.no_of_likes:
            return_string += "Likes: " + str(self.no_of_likes) + "\n"
        if self.is_video is not None:
            return_string += "Is Video: " + str(self.is_video) + "\n"
        if self.media_paths:
            return_string += "Media Path: " + str(self.media_paths) + "\n"

        return return_string
