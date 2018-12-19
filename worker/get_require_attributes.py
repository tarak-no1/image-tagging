import requests, json, sys, os
import pandas as pd

sys.path.insert(0, '/home/ubuntu/attribute-tagging/')
from ml_src.tag_products1 import getAttributesForImages

df = pd.read_csv('voonik_url_women_tops.csv')
row = 1
image_links = []
csv_data = {}
print("Total Elements : ", len(df))
require_attributes = []
while row<len(df):
	_id = df.ix[row, 0]
	url = df.ix[row, 1]
	attribute = df.ix[row, 2]
	value = df.ix[row, 3]
	if attribute not in require_attributes:
		require_attributes.append(attribute)
	csv_data[url] = {
		"id": _id,
		"url_list": url,
		"attribute": attribute,
		"value": value
	}
	image_links.append(url)
	row += 1
parameters = {
	"product_line": "women_tops",
	"image_links" : image_links
}
columns = ['id', "url_list", 'attribute', 'value', 'predicted_value'],
print("before request")
tagging_result = getAttributesForImages("women_tops", image_links, 'general', require_attributes)
print("after request")
tagging_result = json.load(tagging_result)
try:
	with open('JSONData.json', 'w') as f:
		json.dump(tagging_result, f, indent=2)
except Exception as e:
	print(e)

csvData = []
for image, attribute_data in tagging_result.items():
	attribute = csv_data[image]['attribute']
	if attribute=='sleeve':
		attribute = 'sleeve_length'
	attribute = attribute.split('_').join(' ')
	try:
		csv_data[image]["predicted_value"] = attribute_data[attribute]
	except Exception as e:
		print("Error : ", e)
	csvData.append(csv_data[image])
df = pd.DataFrame(csvData, columns=columns)
df.to_csv('voonik_output.csv')