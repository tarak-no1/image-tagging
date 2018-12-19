import json
import os
ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
label_values_file = ROOT_DIR+"/source/label_values.json"
probability_values_file = ROOT_DIR+"/source/probability_values.json"
weights_types_file = ROOT_DIR+"/source/weight_types.json"
def loadLabelValues():  
    with open(label_values_file, 'r') as f:
        label_values = json.load(f)
    return label_values

def loadProbalityValues():
    with open(probability_values_file, 'r') as f:
        probability_values = json.load(f)
    return probability_values

def getAttributes(product_line):
    label_values = loadLabelValues()
    attributes = list(label_values["idx_to_names"][product_line].keys())
    try:
        attributes.remove('professional_look')
    except:
        print('professional_look not present')
    try:
        attributes.remove('sub_category')
    except:
        print('sub_category not present')
    return attributes

def getWeights(product_line, attribute):
    print(product_line, attribute)
    label_values = loadLabelValues()
    weights_path = ROOT_DIR+"/source/fashion_weights/"+label_values["weights"][attribute][product_line]
    return weights_path

def getAttributeDims(product_line, attributes):
    dim_obj = {}
    label_values = loadLabelValues()
    for att in attributes:
        dim_obj[att] = len(label_values["idx_to_names"][product_line][att].keys())
    return dim_obj
def getProbabilityValue(product_line, attribute, attribute_value, predicted_probability, company_name='general'):
    predicted_probability = predicted_probability*100
    try:
        if company_name!='zappos':
            company_name = 'general'
        probability_values = loadProbalityValues()
        if company_name in probability_values:
            if product_line in probability_values[company_name]:
                if attribute in probability_values[company_name][product_line]:
                    if attribute_value in probability_values[company_name][product_line][attribute]:
                        probability_data = probability_values[company_name][product_line][attribute][attribute_value]
                        if predicted_probability<probability_data["probability_cut"]:
                            attribute_value = probability_data["condition"]
    except:
        print("Error in this function")
    return attribute_value

def divideArray(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]
def replaceWithDefaults(product_line, img_data):
    if 'pattern' in img_data and 'pattern_type' in img_data:
        if img_data['pattern']["attribute_value"]!='printed':
            img_data['pattern_type']["attribute_value"] = img_data['pattern']["attribute_value"]
    if 'sleeve' in img_data and 'sleeve_type' in img_data:
        if img_data['sleeve']['attribute_value']=='no sleeves':
            img_data['sleeve_type']["attribute_value"] = "no sleeves"
    if 'pattern' in img_data and 'print_coverage' in img_data:
        if img_data['pattern']["attribute_value"]!='printed' and img_data['pattern']["attribute_value"]!='embroidered' and img_data['pattern']["attribute_value"]!='embellishments':
            img_data['print_coverage']['attribute_value'] = "na"
    return img_data
def getWeightsType(product_line):
    with open(weights_types_file, 'r') as f:
        weight_types = json.load(f)
    if product_line in weight_types:
        return weight_types[product_line]
    return None