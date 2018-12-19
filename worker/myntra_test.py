import json, sys
import pandas as pd
import csv
from pymongo import MongoClient
client = MongoClient("mongodb://adminUser:password@35.200.171.190:27017/product_data")
sys.path.insert(0, '/home/ubuntu/attribute-tagging/')
from ml_src.tag_products1 import getAttributesForImages, bulkImageAttributeTagging
DB_NAME = "myntra_test_dataset"

def generateCsv(product_line):
    columns = ["product_line","image_link"]
    csv_data = {}
    cropped_to_main_map = {}
    required_data = []
    collection = client[DB_NAME][product_line]

    product_line_data = list(collection.find({}))
    print("Total Products :", len(product_line_data))
    for data in product_line_data:
        try:
            company_name = "myntra"
            image_link = data["style_images"]["cropped"]["imageURL"]
            main_image_url = data["style_images"]["default"]["imageURL"]

            cropped_to_main_map[image_link] = main_image_url

            if company_name not in csv_data:
                csv_data[company_name] = {}
            if product_line not in csv_data[company_name]:
                csv_data[company_name][product_line] = []
            if image_link not in csv_data[company_name][product_line]:
                csv_data[company_name][product_line].append(image_link)
        except Exception as e:
            print("ignored", e)
            
    for company_name, products_data in csv_data.items():
        for product_line, image_links in products_data.items():
            requred_attributes = ['sub_category']
            image_attribute_data = getAttributesForImages(product_line, image_links, company_name,requred_attributes)
            for link, att_data in json.loads(image_attribute_data).items():
                obj = {"company_name":company_name,"product_line":product_line,"image_link":cropped_to_main_map[link]}
                for attribute, data in att_data.items():
                    if attribute!="colour":
                        att_value = attribute+"_value"
                        att_confidance = attribute+"_confidance"
                        if att_value not in columns:
                            columns.append(att_value)

                        # if att_confidance not in columns:
                        #     columns.append(att_confidance)
                        obj[attribute+"_value"] = data["attribute_value"]
                        #obj[attribute+"_confidance"] = data["pred_probability"]
                    else:
                        obj["colour"] = []
                        obj["hexa_code"] = []
                        try:
                            for col_data in data["attribute_value"]:
                                obj["colour"].append(col_data["colour"])
                                obj["hexa_code"].append(col_data["hexa_code"])
                        except:
                            print('error')
                required_data.append(obj)
        
    df = pd.DataFrame(required_data, columns = columns)
    df.to_csv("myntra_test_output.csv")
    print("file created")

if __name__ == "__main__":
    print(sys.argv)
    if len(sys.argv) != 2:
      print("Usage: python myntra_test.py women_tshirts")
      sys.exit(1)
    product_line = sys.argv[1]
    generateCsv(product_line)