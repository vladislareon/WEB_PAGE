import webpagelib

FORBIDDEN_TAGS = ("script", "style", "iframe", "svg")
tittle_classifier = webpagelib.element_features.FitsXpathMask("/html/head/title")


def check_forbidden_tags_in(xpath):
    return any(tag in xpath for tag in FORBIDDEN_TAGS)


def element_is_suitable(elem):
    if not elem.text:
        return False
    # we need only tittle element in <head> tag
    if tittle_classifier(elem):
        return True
    if not ("body" in elem.xpath):
        return False
    if check_forbidden_tags_in(elem.xpath):
        return False
    if len(elem.text.strip() + elem.tail.strip()) <= 3:
        return False
    return True
