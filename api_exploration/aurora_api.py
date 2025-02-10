from requests import get
from xml.etree import ElementTree as ET


def get_current_aurora_data():
    response = get(
        "https://aurorawatch-api.lancs.ac.uk/0.2/status/current-status.xml")
    root = ET.fromstring(response.text)
    last_update = root[0][0].text
    current_status = root[1].attrib["status_id"]
    return {"last_updated": last_update, "current_status": current_status}


if __name__ == "__main__":
    print(get_current_aurora_data())
