import requests
from bs4 import BeautifulSoup
from bs4.element import Tag
from typing import Optional, List, Union

class BeautifulSoupHtmlParser:

    def __init__(self) -> None:
        self.__souped_html = BeautifulSoup()

    def get_html(self, url:str) -> None:
        response = requests.get(url=url)
        # response.encoding = 'ISO-8859-1'
        response.encoding = response.apparent_encoding
        self.__souped_html = BeautifulSoup(markup=response.text, features="lxml")

    def get_data_from_tag_or_class(self, **kwargs: str) -> List[Tag]:
        tag_name: Optional[str] = None
        class_name: Optional[str] = None
        for key, value in kwargs.items():
            if key == "tag_name":
                tag_name = value
            elif key == "class_name":
                class_name = value
        return self.__souped_html.find_all(name=tag_name, class_=class_name)

    @classmethod
    def get_text_from_single_tag(cls, input_html: Tag) -> str:
        return input_html.text
    
    @classmethod
    def get_href_from_single_tag(cls, input_html: Tag) -> Union[str, List[str]]:
        return input_html["href"]
    
    @classmethod
    def get_parent_from_single_tag(cls, input_html: Tag) -> Optional[Tag]:
        return input_html.parent
    
    def print_souped(self):
        print(self.__souped_html)
