from scrape_tools.beautifulsoup_tools import BeautifulSoupHtmlParser
from scrape_tools.scrape_message_parser import message_parser
from utility.read_write_utilities import PandasAndParquet


from typing import List, Dict, Any

incoming_data_1: List[Dict[str, str]] = [{"function_name":"get_data_from_tag_or_class", "tag_name": "a", "class_name": "lnk2"},
                 {"function_name": "get_text_from_single_tag"},
                 {"function_name": "get_element_split_by", "element": "1", "split_by": ","}
                 ]

incoming_data_2: List[Dict[str, str]] = [{"function_name":"get_data_from_tag_or_class", "tag_name": "div", "class_name": "price"},
                 {"function_name": "get_text_from_single_tag"},
                 {"function_name": "get_element_replaced_with", "old_string": " EUR ", "new_string": ""}
                 ]

bsp = BeautifulSoupHtmlParser()
bsp.get_html(url="https://www.imot.bg/pcgi/imot.cgi?act=3&slink=97mydj&f1=1")

data_to_be_stored: Dict[str, Any] = dict()

data_to_be_stored.update(message_parser(beautiful_soup_parser=bsp, title_for_result= "Locations", incoming_message=incoming_data_1))
data_to_be_stored.update(message_parser(beautiful_soup_parser=bsp, title_for_result= "Price", incoming_message=incoming_data_2))

# print(data_to_be_stored["Price"])


ExportToParquet = PandasAndParquet()
ExportToParquet.append_column_to_dataframe(column_name="Price", column_data=data_to_be_stored["Price"])
ExportToParquet.append_column_to_dataframe(column_name="Locations", column_data=data_to_be_stored["Locations"])

ExportToParquet.save_dataframe_as_parquet(path_to_save_folder="./", just_filename="test_parquet")
read_dataframe = PandasAndParquet()
read_dataframe.read_parquet_as_dataframe(path_to_file_folder="./", just_filename="test_parquet")
read_dataframe.get_data_head()

my_data_frame = read_dataframe.get_data_as_dataframe()
