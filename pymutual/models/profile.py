import json


class Profile:
    def __init__(self, name, age, gender, mutual_id, distance_mi, location, photo_urls, position, school, height, mission,
                 hometown, fb_id, dating_interest, liked_user, prompt_id=None, bio=None, tags=None, common_friend_count=None,
                 common_likes_count=None, liked_by_user=False):
        self.name = name
        self.age = age
        self.gender = gender
        self.id = mutual_id
        self.prompt_id = prompt_id
        self.bio = bio
        self.common_friends = common_friend_count
        self.common_likes = common_likes_count
        self.distance_mi = distance_mi
        self.location = location
        self.photo_urls = photo_urls
        self.position = position
        self.school = school
        self.height = height
        self.mission = mission
        self.hometown = hometown
        self.fb_id = fb_id
        self.dating_interest = dating_interest
        self.liked_user = liked_user
        self.tags = tags

        self.liked = liked_by_user
        self.photo_ids = []

    def to_json(self):
        return json.dumps(self, default=lambda o: o.__dict__, indent=4)

    def serialize(self):
        return {
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'mutual_id': self.id,
            'prompt_id': self.prompt_id,
            'bio': self.bio,
            'common_friends': self.common_friends,
            'common_likes': self.common_likes,
            'distance_mi': self.distance_mi,
            'location': self.location,
            'photo_urls': self.photo_urls,
            'position': self.position,
            'school': self.school,
            'height': self.height,
            'mission': self.mission,
            'hometown': self.hometown,
            'fb_id': self.fb_id,
            'dating_interest': self.dating_interest,
            'liked_user': self.liked_user,
            'tags': self.tags,
            'liked_by_user': self.liked,
            'photo_ids': self.photo_ids
        }
