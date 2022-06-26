def fits_image(block, h, w):
    return (
        0 <= block["location"]["y"]
        and block["location"]["y"] + block["size"]["height"] <= h
        and 0 <= block["location"]["x"]
        and block["location"]["x"] + block["size"]["width"] <= w
    )

def extract_coordinates(w, h, metainfo):
    coordinates_x, coordinates_y = [], []

    for block_path in metainfo:
        block = metainfo[block_path]
        if type(block) == list:
            block = block[0]

        if fits_image(block, h, w):
            coordinates_x.append(block["location"]["x"])
            coordinates_x.append(block["location"]["x"] + block["size"]["width"])
            coordinates_y.append(block["location"]["y"])
            coordinates_y.append(block["location"]["y"] + block["size"]["height"])

    return coordinates_x, coordinates_y


def prepare_grid(image_size, metainfo):
    w = image_size.get("width")
    h = image_size.get("height")

    coordinates_x, coordinates_y = extract_coordinates(w,h, metainfo)
    coordinates_x += [0, w]
    coordinates_y += [0, h]

    coordinates_x = sorted(set(coordinates_x))
    coordinates_y = sorted(set(coordinates_y))

    return coordinates_x, coordinates_y


def prepare_map_irreg_(
    image_size, metainfo, coordinates, prior_map=None, leave_only_max=True
):
    w = image_size.get("width")
    h = image_size.get("height")

    coordinates_x, coordinates_y = coordinates

    inv_x = {x: i for i, x in enumerate(coordinates_x)}
    inv_y = {y: i for i, y in enumerate(coordinates_y)}

    if prior_map is None:
        result = [
            [[] for _ in range(len(coordinates_x) - 1)]
            for _ in range(len(coordinates_y) - 1)
        ]
    else:
        result = prior_map

    for block_path in metainfo:
        block = metainfo[block_path]
        if type(block) == list:
            block = block[0]

        if fits_image(block, h, w):
            min_x = inv_x[block["location"]["x"]]
            max_x = inv_x[block["location"]["x"] + block["size"]["width"]]
            min_y = inv_y[block["location"]["y"]]
            max_y = inv_y[block["location"]["y"] + block["size"]["height"]]

            for y in range(min_y, max_y):
                for x in range(min_x, max_x):
                    result[y][x].append(block)

    return result


def prepare_map_irreg(image_size, metainfo):
    coordinates = prepare_grid(image_size, metainfo)
    return prepare_map_irreg_(image_size, metainfo, coordinates)
