import pandas as pd
import requests
import os
import json
import pprint
import uuid
from multiprocessing import Pool
from shutil import rmtree
from PIL import Image
from io import BytesIO

def download_image(url_and_name):
    url = url_and_name[0]
    image_name = url_and_name[1]

    print("Downloading image from url: ", url)
    image_file_path = os.path.join(images_folder, image_name)

    if not os.path.isfile(image_file_path):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            rgb_im = img.convert('RGB')
            rgb_im.save(image_file_path)
        except:
            print("Error in saving image")
def get_image_data(file_name):
    
    pool = Pool()
    pool.map(download_image, image_urls_and_names)
    client.close()