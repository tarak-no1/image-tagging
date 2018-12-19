import requests, json
import pandas as pd
import csv

csv_file_name = "test_urls.csv"
headers = {'content-type': 'application/json'}
columns = ["image_link","colour","min_pixels", "actual_pixels"]
with open(csv_file_name) as f:
    reader = csv.reader(f, delimiter="\t")
    csvData = []
    for i in reader:
        parameters = {"product_line":"women_tops","weights_type":"topwear","image_links":i}
        
        get_attributes_request = requests.post("http://35.201.175.78/image-tagging/get-attributes", data=json.dumps(parameters), headers=headers)
        color_detector = requests.post("http://35.201.175.78/color-extractor", data=json.dumps(parameters), headers=headers)
        
        image_attribute_data = json.loads(get_attributes_request.text)
        att_keys = image_attribute_data.keys()
        for link, att_data in image_attribute_data.items():
        	for field, data in att_data.items():
	        	att_value = field+"_value"
	        	att_confidance = field+"_confidance"
	        	att_status = field+"_status"
	        	if att_value not in columns:
		        	columns.append(att_value)
		        if att_confidance not in columns:
	        		columns.append(att_confidance)
	        	if att_status not in columns:
	        		columns.append(att_status)
        color_detector_data = json.loads(color_detector.text)
        for link, obj in color_detector_data.items():
        	if link in image_attribute_data:
        		image_attribute_data[link]["colour"] = obj[0]
        for link, att_data in image_attribute_data.items():
        	obj = {"image_link":link}
        	for attribute, data in att_data.items():
        		print(attribute)
        		if attribute!="colour":
	        		obj[attribute+"_value"] = data["attribute_value"]
	        		obj[attribute+"_confidance"] = data["pred_probability"]
	        		obj[attribute+"_status"] = data["status"]
	        	else:
	        		obj["colour"] = data["colour"]
	        		obj["min_pixels"] = data["min_pixels"]
	        		obj["actual_pixels"] = data["actual_pixels"]
	        print(obj)
	        csvData.append(obj)


print(columns)
df = pd.DataFrame(csvData, columns = columns)
df.to_csv('output.csv')