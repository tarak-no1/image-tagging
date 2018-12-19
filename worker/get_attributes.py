from pymongo import MongoClient
import pymongo
from elasticsearch import Elasticsearch, TransportError
import os, sys, json, shutil, time
sys.path.insert(0, '/home/ubuntu/attribute-tagging/')
from ml_src.tag_products1 import getAttributesForImages
from ml_src.helper import divideArray

es = Elasticsearch(['http://35.200.199.189/elasticsearch'], http_auth=('user', 'fLxscDBh5zdZ'),port=80)
client = MongoClient("mongodb://adminUser:password@35.200.171.190:27017/product_data")

DB_NAME = 'product_data'
def tagAttributes(product_line, image_links, require_attributes):
	print("In Tag Attributes function")
	collection = client[DB_NAME][product_line]
	print(len(image_links))
	image_attribute_data = json.loads(getAttributesForImages(product_line, image_links, require_attributes=require_attributes))
	print("Length :",len(image_attribute_data.keys()))

	bulkop = collection.initialize_ordered_bulk_op()
	query_count = 0
	for img_path, attr_data in image_attribute_data.items():
		try:
			for attr, attr_value_data in attr_data.items():
				if(attr=='professional_look'):
					professional_look = attr_value_data["attribute_value"]
					confidance = attr_value_data["pred_probability"]
					if professional_look=='yes':
						query_count += 1
						print("updated")
						bulkop.find({'style_images.default.imageURL': img_path,"new_updated_benefit":{"$nin":["professional_look"]}}).update({"$addToSet":{"new_updated_benefit":"professional_look"}, "$set":{"new_updated_benefit_scores.professional_look_score":confidance}})
				else:
					attr_value = attr_value_data["attribute_value"]
					att_confidance = attr_value_data["pred_probability"]
					query_count += 1
					bulkop.find({'style_images.default.imageURL': img_path}).update({"$set":{"product_filter."+attr:attr_value}})
			if query_count>=200:
				query_count = 0
				result = bulkop.execute()
				bulkop = collection.initialize_ordered_bulk_op()
		except Exception as e:
			print(e)
	try:
		if(query_count>0):
			result = bulkop.execute()
	except Exception as e:
		print(e)
	return True

def getAttributes(product_line, require_attributes):
	collection = client[DB_NAME][product_line]
	# prof_query = professional_look_query[product_line]
	# es_result = es.search(index="product_data", doc_type=product_line, body=prof_query)
	# print(es_result["hits"]["total"])
	# hits = es_result["hits"]["hits"]
	# mongo_query = {"$or":[]}
	# for dt in hits:
	# 	mongo_query["$or"].append({"es_mysql_id":int(dt["_id"])})

	# print(len(mongo_query["$or"]))
	# print(mongo_query["$or"][0])
	# products_list = list(collection.find(mongo_query))
	products_list = list(collection.find({}))
	print("Total Products : ",len(products_list))
	image_links = []
	count=0
	for data in products_list:
		count += 1
		try:
			image_path = data["style_images"]["default"]["imageURL"]
			image_links.append(image_path);
			if(len(image_links)>=100):
				new_image_links = image_links;
				image_links = []
				print("Count : ",count)
				status = tagAttributes(product_line, new_image_links, require_attributes)
				print(status)
		except KeyError:
			print("Error : ")

	if len(image_links)>0:
		status = tagAttributes(product_line, image_links, require_attributes)
		print(status)
		image_links = []

if __name__ == "__main__":
	print(sys.argv)
	# if len(sys.argv) != 2:
	# 	print("Usage: python get_attributes.py women_dresses")
	# 	sys.exit(1)
	product_line = 'women_tops'
	require_attributes = ["professional_look"]
	getAttributes(product_line, require_attributes)


# professional_look_query = {
# 	"women_tops":{
# 		"size":5000,
# 		"_source":["_id"],
# 	    "query": {
# 	      "bool": {
# 	        "must": {
# 	          "bool": {
# 	            "must": [
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.sleeve": "long sleeve"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.sleeve": "three-quarter sleeve"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.sleeve": "short sleeve"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "a-line"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "shirt style"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "single-breasted"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "wrap"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "peplum"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "fit and flared"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "double-breasted"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "tunic"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "stitched"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.tops_type": "regular"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "bow neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "band collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "shirt collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "lapel collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "peter pan collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "keyhole neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "round neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "boat neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "mandarin collar"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "solid"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "checked"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "striped"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "self design"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "black"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "burgundy"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "coffee"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "blue"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "brown"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "charcoal"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "grey"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "khaki"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "navy blue"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "white"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "wine"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "dark-green"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "neutral"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "nude"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "olive"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "coffee brown"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "off white"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "mustard"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "rust"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "cream"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "dark grey"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "rose"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "stone"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "teal"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "mushroom brown"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "ivory"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "beige"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "violet indigo"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              }
# 	            ],
# 	            "must_not": [
# 	              {
# 	                "bool": {
# 	                  "must": [
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.neck": [
# 	                          "v-neck"
# 	                        ]
# 	                      }
# 	                    },
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.sleeve": [
# 	                          "short sleeve"
# 	                        ]
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "must": [
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.sleeve": [
# 	                          "no sleeves"
# 	                        ]
# 	                      }
# 	                    },
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.neck": [
# 	                          "v-neck"
# 	                        ]
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "embellishments"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "faded"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "dyed"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "embroidered"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "tie-up neck"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.tops_length": "crop"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "brasso"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "mesh"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "shimmer"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "satin"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "brocade"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "dobby"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "faux fur"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "rubber"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "scuba"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "leather"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "organza"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "polyurethane"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "sequin"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "georgette"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "hooded"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "convertible"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "off shoulder"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "racer back"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "shawl collar"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "double collar"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "one shoulder"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric_type": "denim"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "cotton blend"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "jersey"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "pure cotton"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.dress_length": "maxi"
# 	                }
# 	              }
# 	            ]
# 	          }
# 	        }
# 	      }
# 	    }
# 	},
# 	"women_dresses":{
# 		"size":3000,
# 		"_source":["_id"],
# 	    "query": {
# 	      "bool": {
# 	        "must": {
# 	          "bool": {
# 	            "must": [
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.sleeve": "long sleeve"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.sleeve": "three-quarter sleeve"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.sleeve": "short sleeve"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "bow neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "band collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "shirt collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "lapel collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "peter pan collar"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "keyhole neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "round neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "boat neck"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.neck": "mandarin collar"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "solid"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "checked"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "striped"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.pattern": "self design"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "black"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "burgundy"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "coffee"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "blue"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "brown"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "charcoal"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "grey"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "khaki"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "navy blue"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "white"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "wine"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "dark-green"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "neutral"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "nude"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "olive"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "coffee brown"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "off white"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "mustard"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "rust"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "cream"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "dark grey"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "rose"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "stone"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "teal"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "mushroom brown"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "ivory"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "beige"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.colour": "violet indigo"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "should": [
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "a-line"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "wrap"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "straight regular"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "peplum"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "tunic"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "basic"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "shirt"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "shift"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "bodycon"
# 	                      }
# 	                    },
# 	                    {
# 	                      "match": {
# 	                        "product_filter.dress_shape": "jacket style"
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              }
# 	            ],
# 	            "must_not": [
# 	              {
# 	                "bool": {
# 	                  "must": [
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.neck": [
# 	                          "v-neck"
# 	                        ]
# 	                      }
# 	                    },
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.sleeve": [
# 	                          "short sleeve"
# 	                        ]
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "bool": {
# 	                  "must": [
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.sleeve": [
# 	                          "no sleeves"
# 	                        ]
# 	                      }
# 	                    },
# 	                    {
# 	                      "terms": {
# 	                        "product_filter.neck": [
# 	                          "v-neck"
# 	                        ]
# 	                      }
# 	                    }
# 	                  ]
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "embellishments"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "faded"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "dyed"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.pattern": "embroidered"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "tie-up neck"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.tops_length": "crop"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "brasso"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "mesh"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "shimmer"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "satin"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "brocade"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "dobby"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "faux fur"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "rubber"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "scuba"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "leather"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "organza"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "polyurethane"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "sequin"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "georgette"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "hooded"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "convertible"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "off shoulder"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "racer back"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "shawl collar"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "double collar"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.neck": "one shoulder"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric_type": "denim"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "cotton blend"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "jersey"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.fabric": "pure cotton"
# 	                }
# 	              },
# 	              {
# 	                "match": {
# 	                  "product_filter.dress_length": "maxi"
# 	                }
# 	              }
# 	            ]
# 	          }
# 	        }
# 	      }
# 	    }
#     }
# }