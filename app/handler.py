import os
import uuid
import json, time
from glob import glob
import numpy as np
import requests
import pandas as pd

import tornado.web
from tornado import concurrent
from tornado import gen
from concurrent.futures import ThreadPoolExecutor
from functools import singledispatch

from app.base_handler import BaseApiHandler
from app.settings import MAX_MODEL_THREAD_POOL
from ml_src.tag_products import tagAttributes, getAttributesForImages
from db_config.mysqlQueries import sqlQuery
from worker.make_csv import makeCsv

__UPLOADS__ = "/home/ubuntu/attribute-tagging/upload/"

class IndexHandler(tornado.web.RequestHandler):
    """APP is live"""
    def get(self):
        """Return Index Page"""
        self.render("templates/index.html")

    def head(self):
        """Verify that App is live"""
        self.finish()

    def post(self):
        inventory_id = self.get_argument('inventory_id', '1')
        print("Inventory Id : ", inventory_id)
        tagAttributes(int(inventory_id))
        return self.render("templates/index.html")
class GetAttributes(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        print("In get attributes get")
        """Return Index Page"""
        return self.write({})

    def head(self):
        """Verify that App is live"""
        self.finish()
    def post(self):
        print("In get attributes post")
        print(self.request.body)
        data = tornado.escape.json_decode(self.request.body)
        product_line = data["product_line"]
        image_links = data["image_links"]
        try:
            company_name = data["company_name"]
        except:
            company_name = "general"
        print(product_line)
        print(image_links)
        
        result = getAttributesForImages(product_line, image_links, company_name)
        return self.write(result)
    def options(self):
        # no body
        self.set_status(204)
        self.finish()

class Upload(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def post(self):
        fileinfo = self.request.files['file'][0]
        fname = fileinfo['filename']
        print("filename : ",fname)
        extn = os.path.splitext(fname)[1]
        extn = extn.lower()
        cname = str(uuid.uuid4())
        if extn==".jpg" or extn=='.jpeg' or extn=='.csv' or extn=='.png':
            fh = open(__UPLOADS__ + cname+extn, 'wb')
            fh.write(fileinfo['body'])
            if extn=='.csv':
                makeCsv(__UPLOADS__ + cname, fileinfo)
                return self.write({"status":True, "type":"csv", "message":"https://imagetag.in/upload-dir/"+cname+"_output"+extn})
            else:
                return self.write({"status":True, "type":"jpg", "message":"https://imagetag.in/upload-dir/"+cname+extn})
        else:
            return self.write({"status":False, "type":"error", "message" : "Invalid file format"})
    def options(self):
        # no body
        self.set_status(204)
        self.finish()
class ContactUsHandler(tornado.web.RequestHandler):
    def set_default_headers(self):
        print("setting headers!!!")
        self.set_header("Access-Control-Allow-Origin", "*")
        self.set_header("Access-Control-Allow-Headers", "x-requested-with")
        self.set_header('Access-Control-Allow-Methods', 'POST, GET, OPTIONS')

    def get(self):
        print("In get attributes get")
        """Return Index Page"""
        return self.write({})

    def head(self):
        """Verify that App is live"""
        self.finish()
    def post(self):
        print("In get attributes post")
        data = tornado.escape.json_decode(self.request.body)
        print(data)
        username = data["username"]
        email = data["email"]
        message = data["message"]
        millis = int(round(time.time() * 1000))
        query = "insert into `contact_us`(`name`, `email`, `message`, `timestamp`)values('%s', '%s', '%s','%s')"% (username, email, message, str(millis))
        print(query)
        sqlQuery("image_tagging", query)
        return self.write({"status":True})
    def options(self):
        # no body
        self.set_status(204)
        self.finish()
