import pandas as pd
import numpy as np
from tqdm import tqdm
CHANNELS = 3
k = 20
dx1 = [0, 0, -1, 0]
dy1 = [0, -1, 0, 0]
dx2 = [1, 0, 0, 0]
dy2 = [0, 0, 0, 1]



def extract_channels(blocks):
    if len(blocks) == 0:
        result = [0, 0, 0]
    else:
        block = blocks[0]

        result = [
            block['length'] / 500,
            np.mean(parse_color(block['font-color'])[:3]) / 255,
            #block['width'] * block['height'] / 10000,
            parse_font_size(block['font-size']) / 100
        ]
    
    assert(len(result) == CHANNELS)
    
    return result
def extract_label_cell(blocks, default=None):
    assert(default is not None or len(blocks) > 0)
    
    if len(blocks) > 0:
        block = blocks[0]
        return block['label']
    else:
        return default
def parse_color(color):
    return [float(num) for num in color[(color.find('(') + 1):color.find(')')].split(',')]
def parse_color(color):
    return [float(num) for num in color[(color.find('(') + 1):color.find(')')].split(',')]

def parse_font_size(font_size):
    #print(font_size)
    return float(font_size[:-2])

def parse_text_density(block):
    block_area = block['size']['height'] * block['size']['width']
    return block['length'] / block_area if block_area != 0 else 0

def parse_loc_x_rel(image, block):
    return block['location']['x'] / image.size[0];

def parse_loc_y_rel(image, block):
    return block['location']['y'] / image.size[1];

def extract_features_cell(image, blocks, total_length):
    assert(len(blocks) > 0)



def extract_coordinates(image_size, blocks):
    w, h = image_size
    coordinates_x, coordinates_y = [], []

    for block in blocks:
        if fits_image(block, h, w):
            coordinates_x.append(block['location']['x'])
            coordinates_x.append(block['location']['x'] + block['size']['width'])
            coordinates_y.append(block['location']['y'])
            coordinates_y.append(block['location']['y'] + block['size']['height'])

    coordinates_x += [0, w]
    coordinates_y += [0, h]
            
    coordinates_x = sorted(set(coordinates_x))
    coordinates_y = sorted(set(coordinates_y))
    
    return coordinates_x, coordinates_y

def fits_image(block, h, w):
    return 0 <= block['location']['y'] and \
            block['location']['y'] + block['size']['height'] <= h and \
            0 <= block['location']['x'] and \
            block['location']['x'] + block['size']['width'] <= w



def prepare_map_irreg(image_size, blocks, prior_map=None, label=None):
    w, h = image_size
    coordinates_x, coordinates_y = extract_coordinates(image_size, blocks)

    inv_x = {x: i for i, x in enumerate(coordinates_x)}
    inv_y = {y: i for i, y in enumerate(coordinates_y)}
        
    if prior_map is None:
        result = [[[] for _ in range(len(coordinates_x) - 1)] for _ in range(len(coordinates_y) - 1)]
    else:
        result = prior_map
    
    for block in blocks:
        if label is not None:
            block['label'] = label
            
        if fits_image(block, h, w):
            min_x = inv_x[block['location']['x']]
            max_x = inv_x[block['location']['x'] + block['size']['width']]
            min_y = inv_y[block['location']['y']]
            max_y = inv_y[block['location']['y'] + block['size']['height']]

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    result[y][x].append(block)
                
    return result
def get_nn_dataset(image, metainfo, cell_map, prior_features=None, prior_labels=None,
                       prior_labels_list = None, prior_bbox = None, padded_size=(500, 250)):
    features = prior_features if prior_features is not None else []
    labels   = prior_labels if prior_labels is not None else []
    labels_list   = prior_labels_list if prior_labels_list is not None else []
    bbox = prior_bbox if prior_bbox is not None else []
    
    #output shape: channels, h, w
    compressed_image = np.zeros((max(padded_size[0], len(cell_map)), max(padded_size[1], len(cell_map[0])), CHANNELS))
    compressed_answers = np.zeros((max(padded_size[0], len(cell_map)), max(padded_size[1], len(cell_map[0])), 2))
    xs = []
    ys = []
    lab = []
    boxes = np.array([0, 0, 0, 0])
    for i in range(len(cell_map)):
        for j in range(len(cell_map[0])):
            compressed_image[i][j] = np.array(extract_channels(cell_map[i][j]))     
            compressed_answers[i][j][extract_label_cell(cell_map[i][j], 0)] = 1.0
            if extract_label_cell(cell_map[i][j], 0) == 1:
                xs.append(i)
                ys.append(j)
            lab.append(extract_label_cell(cell_map[i][j], 0))
            #левый угол - начало
            #правый - 
    if len(xs) == 0:
        return features, labels, labels_list, bbox
    features.append(compressed_image.reshape((3, max(padded_size[0], len(cell_map)), max(padded_size[1], len(cell_map[0])))))
    labels.append(compressed_answers)
    labels_list.append([1])
    bbox.append([[np.min(xs), np.min(ys), np.max(xs), np.max(ys)]])
    #bbox.append([[np.min(xs), np.max(ys), np.max(xs), np.min(ys)]])
     [xmin, ymin, xmax, ymax]
    return features, labels, labels_list, bbox


def get_classical_dataset(all_blocks):
    lenght = []
    location_x = []
    location_y = []
    size_1 = []
    size_2 = []
    image = []
    font_size = []
    label = []
    data = pd.DataFrame
    for block in all_blocks:
        lenght.append(block['length'])
        image.append(block['hasImg'])
        location_x.append(block['location']['x'])
        location_y.append(block['location']['y'])
        size_1.append(block['size']['width'])
        size_2.append(block['size']['height'])
        if block['font-size'] == None:
            font_size.append(0)
        else:
            font_size.append(float(block['font-size'][:-2]))
        label.append(block['label'])
    image = np.array(image).astype(int)
    data = pd.DataFrame({'lenght': lenght,
                         'image': image,
                         'location_x': location_x,
                         'location_y': location_y, 'size_1': size_1, 'size_2': size_2, 'font_size': font_size})
    return data, label



def get_all_data(collection, number = None):
    if number == None:
        number = collection.count_documents({})
    i = 0
    X, y = [], [] 
    labels_list, bbox = [], []
    X_classical = pd.DataFrame()
    y_classical = []
    posts = collection.find()
    for i in tqdm(range(number)):
        post = posts[i]
#     for post in tqdm(posts):
        i += 1
        if i >= number:
            break
        matching_blocks_hs = set(post["MatchingBlocks"])
        filtered_blocks = []
        all_blocks = []

#         for block_body in post["Blocks"].values():
#             if block_body["xpath"] in matching_blocks_hs:
#                 filtered_blocks.append(block_body)
        for block_body in post["Blocks"].values():
            all_blocks.append(block_body)
        A, b = get_classical_dataset(all_blocks)
        X_classical = pd.concat([X_classical, A])
        y_classical += b
        image_size = (post["Image"]["width"], post["Image"]["height"])
        cell_map = prepare_map_irreg(image_size, all_blocks)
        if len(cell_map) == 0:
             continue
        cut_size=(512, 256)


        X, y, labels_list, bbox = get_nn_dataset(image_size, all_blocks, cell_map,
                                                 X, y, labels_list, bbox, cut_size)
    return X_classical, y_classical, X, y, labels_list, bbox
