from pymongo import MongoClient
import pymongo
import requests
import uuid
import numpy as np
import os, sys, json, shutil, time
from multiprocessing import Pool
from PIL import Image
from io import BytesIO

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
inventory_images_path = ROOT_DIR+"/source/inventory"

from ml_src.classifiers import get_pretrained_model, createAttributeModel, AttributeFCN, test_models
from ml_src.classifiers import getImageResult, evaluateModel, predict_attributes, create_all_attribute_models
from ml_src.utils import is_gpu_available
from ml_src.helper import getAttributes, getWeights, getAttributeDims,loadLabelValues
from ml_src.helper import getProbabilityValue,divideArray,replaceWithDefaults, getWeightsType

label_values = loadLabelValues()

client = MongoClient("mongodb://adminUser:password@35.200.171.190:27017/product_data")
DB_NAME = "product_data_b2b"
use_gpu = is_gpu_available()
pretrained_conv_model, _, _ = get_pretrained_model("vgg16", pop_last_pool_layer=True, use_gpu=use_gpu)
all_attribute_models = {}

def getInventoryProductlines(inventory_id):
    having_product_lines_data = []
    product_lines = ["women_tops"]
    for product_line in product_lines:
        print(product_line)
        collection = client[DB_NAME][product_line]
        product_count = collection.find({"inventory_id":inventory_id}).count()
        print(product_count)
        if product_count>0:
            having_product_lines_data.append(product_line)
    return having_product_lines_data

def getImageFromURL(url_and_name):
    url = url_and_name[0]
    image_file_path = url_and_name[1]

    print("Downloading image from url: ", url)

    if not os.path.isfile(image_file_path):
        try:
            response = requests.get(url)
            img = Image.open(BytesIO(response.content))
            rgb_im = img.convert('RGB')
            rgb_im.save(image_file_path)
        except:
            print("Error in saving image")

def downloadImages(data, image_folder_path):
    if not os.path.exists(image_folder_path):
        try:
            os.makedirs(image_folder_path)
        except OSError as exc: # Guard against race condition
            if exc.errno != errno.EEXIST:
                raise
    db_to_image_map = {}
    image_urls_and_names = []
    for source in data:
        db_id = source["_id"]
        url = source['style_images']['default']['imageURL']
        extn = os.path.splitext(url)[1]
        extn = extn.strip()
        extn = extn.lower()
        extn = extn.split('?')[0]
        if extn!='':
            image_name = str(uuid.uuid4())+extn
        else:
            image_name = str(uuid.uuid4())+'.jpg'

        image_path = image_folder_path+"/"+image_name
        db_to_image_map[image_path] = db_id
        # try:
        #     if not os.path.exists(image_path):
        #         with open(image_path, "wb") as fh:
        #             fh.write(requests.get(url).content)
        # except:
        #     print("Error in downloading image")
        image_urls_and_names.append([url, image_path])
    pool = Pool()
    pool.map(getImageFromURL, image_urls_and_names)
    pool.close()
    pool.join()
    return db_to_image_map

def getImageAttributesTags(attribute_model, product_line, attribute, docs, inventory_id=None, company_name='general'):
    image_folder_path = None
    print(inventory_id)
    collection = client[DB_NAME][product_line]
    if inventory_id!=None:
        image_folder_path = inventory_images_path+"/"+str(inventory_id)
    else:
        image_folder_path = inventory_images_path+"/tmp"
    for data in docs:
        try:
            shutil.rmtree(image_folder_path, ignore_errors=False, onerror=None)
        except:
            print("Error while deleting folder")
        db_to_image_map = downloadImages(data, image_folder_path)
        evaluation = evaluateModel(attribute_model, pretrained_conv_model, images_folder=image_folder_path, batch_size=32,num_workers=4,use_gpu=use_gpu,flatten_pretrained_out=False)
        
        db_identifiers = [db_to_image_map[img_path] for img_path in list(evaluation["input_files"])]
        attribute_values = [label_values["idx_to_names"][product_line][attribute][num] for num in list(evaluation["y_pred"])]
        confidences = [abs(round(val, 2)) for val in list(evaluation["y_pred_proba"])]

        bulkop = collection.initialize_ordered_bulk_op()
        bulk_status = False
        for i in range(len(db_identifiers)):
            db_id = db_identifiers[i]
            attribute_value = attribute_values[i]
            pred_probability = confidences[i]
            new_attribute_value = getProbabilityValue(product_line, attribute, attribute_value, pred_probability, company_name)
            if new_attribute_value!="":
                bulk_status = True
                update_query = {"$set":{"product_filter."+attribute:new_attribute_value,"missing_attributes."+attribute:True}}
                bulkop.find({'_id': db_id}).update_one(update_query)
        if bulk_status:
            print("Updating the {} collection".format(product_line))
            result = bulkop.execute()

def tagAttributes(inventory_id):
    product_lines = getInventoryProductlines(inventory_id)
    
    for product_line in product_lines:
        collection = client[DB_NAME][product_line]
        mongo_query_count = 0
        #attributes = getAttributes(product_line)
        attributes = ["tops_length"]
        target_dims = getAttributeDims(product_line, attributes)
        for attr in attributes:
            query = {"inventory_id":inventory_id}
            query["missing_attributes."+attr] = False
            print(query)
            product_count = collection.find(query).count()
            print("product count : "+str(product_count))
            if product_count>0:
                weights_root = getWeights(product_line, attr)
                model = createAttributeModel(AttributeFCN, 512, attr, target_dims[attr], weights_root, use_gpu)
                docs = list(collection.find(query))
                print("Docs Length : {}".format(len(docs)))
                splited_docs = divideArray(docs, 32)
                print("Splitted into :{} arrays".format(len(splited_docs)))
                getImageAttributesTags(model, product_line, attr, splited_docs, inventory_id,company_name='general')


def getAttributesForImages(product_line, image_links, company_name='general'):
    collection = client[DB_NAME][product_line]
    if product_line not in all_attribute_models:
        all_attribute_models[product_line] = {}
    attributes = getAttributes(product_line)
    target_dims = getAttributeDims(product_line, attributes)
    weight_type = getWeightsType(product_line)
    weights_root = {}
    for attr in attributes:
        weight_path = getWeights(product_line, attr)
        if os.path.exists(weight_path) and attr not in all_attribute_models[product_line]:
            weights_root[attr] = weight_path
    response_obj = {}
    if len(weights_root.keys())>0:
        require_models = create_all_attribute_models(AttributeFCN, 512,pretrained_conv_model, target_dims, weights_root, batch_size=32, num_workers=4, num_epochs=10, use_gpu=use_gpu)
        all_attribute_models[product_line].update(require_models)

    attribute_models = {}
    for attr in attributes:
        attribute_models[attr] = all_attribute_models[product_line][attr]
    #print(attribute_models)
    image_data = []
    for img_link in image_links:
        image_data.append({"_id":img_link, "style_images":{"default":{"imageURL":img_link}}})

    image_folder_path = inventory_images_path+"/"+str(int(round(time.time() * 1000)))
    image_data = downloadImages(image_data, image_folder_path)
    #print(image_data)
    headers = {'content-type': 'application/json'}

    for image_path, idx in image_data.items():
        response_obj[idx] = {}
        try:
            parameters = {"product_line":product_line,"weights_type":weight_type,"image_links":[idx]}
            color_detector = requests.post("https://imagetag.in/color-extractor", data=json.dumps(parameters), headers=headers)
            colour_attribute_data = json.loads(color_detector.text)
            print("Color Data : ",colour_attribute_data)
            response_obj[idx] = {"colour":colour_attribute_data[idx]}
        except:
            print("Error in colour api")
        try:
            result = test_models(attribute_models, pretrained_conv_model, image_path, attribute_idx_map=label_values["idx_to_names"][product_line])
        except:
            print(idx, image_path)
            result = {}

        for attribute, res_data in result.items():

            attribute_value = res_data["pred_class"]
            pred_probability = res_data["pred_prob"]
            status = False
            new_attribute_value = getProbabilityValue(product_line, attribute, attribute_value, pred_probability, company_name)
            if new_attribute_value!=attribute_value:
                status = True
            
            result[attribute] = {
                "attribute_value" : new_attribute_value,
                "status" : status,
                "pred_probability" : round(pred_probability,6)
            }
        result = replaceWithDefaults(product_line, result)
        main_result = {}
        for attribute, res_data in result.items():
            cleaned_attribute = attribute.replace('_', ' ')
            if attribute == 'sleeve':
                cleaned_attribute = 'sleeve length'
            main_result[cleaned_attribute] = res_data
        response_obj[idx].update(main_result)
    try:
        shutil.rmtree(image_folder_path, ignore_errors=False, onerror=None)
    except:
        print("Error while deleting folder")
    return json.dumps(response_obj)