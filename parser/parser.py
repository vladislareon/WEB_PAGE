import webpagelib

from ..utils import get_logger
from .blocks_matcher import StringProcess
from .checkers import element_is_suitable

logger = get_logger(__name__)


def get_arbitary_parent(elem: webpagelib.Element, depth: int = 1):
    current = elem.to_dict()
    for _ in range(depth - 1):
        current = current.get("parent")
        if current is None:
            return
    return current.get("tag")


def fill_properties_from_WPD(element: webpagelib.Element, properties):
    properties["text"] = (element.text + element.tail).strip()
    properties["xpath"] = element.xpath
    properties["class"] = element.attributes.get("class", "").split()
    properties["p_tag"] = get_arbitary_parent(element, 1)
    properties["pp_tag"] = get_arbitary_parent(element, 2)
    properties["ppp_tag"] = get_arbitary_parent(element, 3)

    properties["location"] = {}
    properties["location"]["x"] = int(element.display["x"])
    properties["location"]["y"] = int(element.display["y"])
    properties["size"] = {}
    properties["size"]["width"] = int(element.display["w"])
    properties["size"]["height"] = int(element.display["h"])

    properties["font-color"] = element.styles.get("color")
    properties["bg-color"] = element.styles.get("background-color")
    properties["font-size"] = element.styles.get("font-size")
    properties["hasImg"] = element.tag == "img" and "src" in element.attributes

    properties["label"] = 0


def extract_data_from_WPD(wpd: webpagelib.WebPageDump):
    metadata = {}
    image_size = (0, 0)
    try:
        w = wpd.root_element.display["w"]
        h = wpd.root_element.display["h"]

        image_size = (w, h)
        isVisible = webpagelib.element_features.IsVisible(image_size[0], image_size[1])

        for elem in wpd.root_element:
            if element_is_suitable(elem):
                textLength = len(elem.text.strip())
                tailLength = len(elem.tail.strip())
                properties = dict()

                # TODO refactor the following code

                if (elem.tag == "img" or textLength > 0) and isVisible(elem):
                    properties = metadata.setdefault(elem.xpath, {})
                    fill_properties_from_WPD(elem, properties)
                    properties.setdefault("length", textLength)

                if tailLength > 0 and isVisible(elem.parent):
                    properties = metadata.setdefault(elem.parent.xpath, {})
                    fill_properties_from_WPD(elem.parent, properties)
                    properties.setdefault("length", len(elem.parent.text.strip()))
                    properties["length"] += textLength + tailLength
                    properties["text"] += (elem.text + elem.tail).strip()
    except Exception as ex:
        logger.error(ex)
    return image_size, metadata


def parse(wpd, url):
    features = {
        "Blocks": {},
        "Text": "",
        "MatchingBlocks": [],
        "Grid": [],
        "Image": {},
        "URL": url,
    }
    image_size, features["Blocks"] = extract_data_from_WPD(wpd)
    features["Image"]["width"], features["Image"]["height"] = image_size
    return features


def get_matching_blocks(blocks, text):
    str_pr = StringProcess(blocks, text, split_len=10 ** 10)
    skipped, inds, xpathes = str_pr.do_all()
    return xpathes
