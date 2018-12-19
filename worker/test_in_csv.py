import json, sys
import pandas as pd
import csv
sys.path.insert(0, '/home/ubuntu/attribute-tagging/')
from ml_src.tag_products1 import getAttributesForImages


def makeCsv(csv_file_name):
    columns = ["product_line","image_link"]
    csv_data = {}
    required_data = []
    print(csv_file_name)
    reader = pd.read_csv(csv_file_name+".csv")
    row = 1
    while row<len(reader):
        try:
            company_name = reader.ix[row, 0].strip()
            product_line = reader.ix[row, 1].strip()
            image_link = reader.ix[row, 2].strip().replace('"', '')
            if company_name not in csv_data:
                csv_data[company_name] = {}
            if product_line not in csv_data[company_name]:
                csv_data[company_name][product_line] = []
            if image_link not in csv_data[company_name][product_line]:
                csv_data[company_name][product_line].append(image_link)
        except Exception as e:
            print("ignored", e)
        row += 1
    for company_name, products_data in csv_data.items():
        for product_line, image_links in products_data.items():
            requred_attributes = ['sub_category']
            image_attribute_data = getAttributesForImages(product_line, image_links, company_name,requred_attributes)
            for link, att_data in json.loads(image_attribute_data).items():
                obj = {"company_name":company_name,"product_line":product_line,"image_link":link}
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
    df.to_csv(csv_file_name+"_output.csv")
    print("file created")
makeCsv("/home/ubuntu/attribute-tagging/worker/test")