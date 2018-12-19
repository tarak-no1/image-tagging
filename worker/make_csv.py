import json, sys
import pandas as pd
import csv
sys.path.insert(0, '/home/ubuntu/attribute-tagging/')
from ml_src.tag_products import getAttributesForImages

def makeCsv(csv_file_name, fileinfo):
    columns = ["company_name","product_line","image_link", "colour", "hexa_code"]
    csv_data = {}
    required_data = []
    reader = fileinfo["body"].decode("utf-8")
    reader = reader.strip().split("\n")
    print("Csv Length : ", len(reader))
    reader = [i.strip().split(",") for i in reader]
    for data in reader:
        try:
            company_name = data[0].strip()
            product_line = data[1].strip()
            image_link = data[2].strip().replace('"', '')
            if company_name not in csv_data:
                csv_data[company_name] = {}
            if product_line not in csv_data[company_name]:
                csv_data[company_name][product_line] = []
            if image_link not in csv_data[company_name][product_line]:
                csv_data[company_name][product_line].append(image_link)
        except:
            print("ignored")
    for company_name, products_data in csv_data.items():
        for product_line, image_links in products_data.items():
            image_attribute_data = getAttributesForImages(product_line, image_links, company_name)
            for link, att_data in json.loads(image_attribute_data).items():
                obj = {"company_name":company_name,"product_line":product_line,"image_link":link}
                for attribute, data in att_data.items():
                    if attribute!="colour":
                        att_value = attribute+"_value"
                        att_confidance = attribute+"_confidance"
                        if att_value not in columns:
                            columns.append(att_value)

                        if att_confidance not in columns:
                            columns.append(att_confidance)
                        obj[attribute+"_value"] = data["attribute_value"]
                        obj[attribute+"_confidance"] = data["pred_probability"]
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
#makeCsv("/home/ubuntu/attribute-tagging/worker/test_urls.csv")