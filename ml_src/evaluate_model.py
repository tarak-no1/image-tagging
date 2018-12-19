from pymongo import MongoClient
import pymongo
import requests
import numpy as np
import os, sys, json, shutil
from os import listdir
from os.path import isfile, join

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
inventory_images_path = ROOT_DIR+"/source/inventory"

from classifiers import get_pretrained_model, createAttributeModel, AttributeFCN, evaluateModel,create_all_attribute_models,predict_attributes
from helper import getAttributes, getWeights, getAttributeDims,loadLabelValues

from utils import is_gpu_available
label_values = loadLabelValues()

use_gpu = is_gpu_available()

image_folder_path = inventory_images_path+'/tmp'

pretrained_conv_model, _, _ = get_pretrained_model("vgg16", pop_last_pool_layer=True, use_gpu=use_gpu)

#model = createAttributeModel(AttributeFCN, 512, "tops_length", 3, ROOT_DIR+"/source/fashion_weights/tops_length", use_gpu)

#evaluation = evaluateModel(model, pretrained_conv_model, images_folder=image_folder_path, batch_size=32,num_workers=4,use_gpu=use_gpu,flatten_pretrained_out=False)
#print(evaluation)


product_line = "women_tshirts"
attributes = getAttributes(product_line)
target_dims = getAttributeDims(attributes)
weights_root = {}
for attr in attributes:
    weights_root[attr] = getWeights(product_line, attr)

all_attribute_models = create_all_attribute_models(AttributeFCN, 512,pretrained_conv_model, target_dims, weights_root, batch_size=32, num_workers=4, num_epochs=10, use_gpu=use_gpu)

onlyfiles = [f for f in listdir(image_folder_path) if isfile(join(image_folder_path, f))]
for img in onlyfiles:
    print(img)
    result = predict_attributes(image_folder_path+"/"+img, pretrained_conv_model, all_attribute_models, attribute_idx_map=label_values["idx_to_names"], 
                       flatten_pretrained_out=False, use_gpu=use_gpu)
    print(result)
