import requests

diffbot_endpoint = "https://api.diffbot.com/v3/article"
diffbot_token = "ea4e23212c0c97084981e4024d95eaaa"


def get_text_from_diffbot(url):
    resp = requests.get(
        diffbot_endpoint,
        params={"token": diffbot_token, "url": url, "paging": "false"},
        timeout=60,
    )
    assert resp.status_code == 200
    return resp.json()["objects"][0]["text"]
