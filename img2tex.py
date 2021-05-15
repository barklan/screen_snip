import os
import requests
from bs4 import BeautifulSoup
import re


path_img = "boom4.png"


class ScribbleMyScience:
    url = "https://scribblemyscience.com/result"

    @classmethod
    def img2tex(self, path_img: str) -> str:
        with open(path_img, "rb") as img:
            name_img = os.path.basename(path_img)
            files = {"file": (name_img, img, "multipart/form-data", {"Expires": "0"})}
            with requests.Session() as s:
                r = s.post(self.url, files=files)
                soup = BeautifulSoup(r.content, "html.parser")
        string_of_interest = str(soup.find_all("div", class_="text-result")[0])
        contains_tex = re.search(r"<p>\\\(", string_of_interest)
        print(contains_tex)
        if contains_tex:
            result = re.split(r"(<p>\\\(|\\\)</p>)", string_of_interest)[2]
        else:
            result = None
        return result