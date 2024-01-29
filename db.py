import pymongo
import datetime
import json

with open("config.json","r") as c:
    params = json.load(c)['params']

if params["local_server"] == True:
    client = pymongo.MongoClient(params["local_uri"])
else:
    client = pymongo.MongoClient(params["prod_uri"])


db = client['flask']
collectionp = db['posts']
collectionc = db['contacts']

class Posts:

    def __init__(self):
        pass

    def insertDocument(self, title, tagline, slug, content, img_file):
        self.count = collectionp.count_documents({}) + 1
        self.date = datetime.datetime.now()
        collectionp.insert_one({"_id":self.count,"title":title, "tagline":tagline, "slug":slug, "content":content, "img_file":img_file, "date":self.date})

    def getPost(self, slug):
        post = collectionp.find_one({"slug":slug})
        return post
    
    def updatePostById(self, sno, title, tagline, slug, content, img_file):
        self.date = datetime.datetime.now()
        prev = {"_id":int(sno)}
        next = {"$set":{"title":title, "tagline":tagline, "slug":slug, "content":content, "img_file":img_file, "date":self.date}}
        collectionp.update_one(prev, next)

    def getPostById(self, id):
        post = collectionp.find_one({"_id":int(id)})
        return post
        
    
    def getAllPost(self):
        return collectionp.find({})
    
    def deletePost(self, sno):
        collectionp.delete_one({"_id":int(sno)})


class Contacts:

    def __init__(self):
        pass

    def insertDocument(self, name, email, number, mes):
        self.count = collectionc.count_documents({}) + 1
        self.date = datetime.datetime.now()
        collectionc.insert_one({"_id":self.count,"name":name, "email":email, "phone_no":number,"message":mes, "date":self.date})

