from scrape_tools.beautifulsoup_tools import BeautifulSoupHtmlParser
from utility.string_utilities import get_element_split_by, get_element_replaced_with # type: ignore 
from typing import List, Dict, Union, Any, Optional

def run_getattr_for_list(beautiful_soup_parser:BeautifulSoupHtmlParser, function_name: str, input_list: List[Any], function_arguments: Optional[Dict[str,str]]=None):
    final_result: List[Any] = list()
    if function_arguments is None:
        function_arguments = dict()
    for input_data in input_list:
        final_result.append(getattr(beautiful_soup_parser, function_name)(input_html=input_data, **function_arguments))
    return final_result

def run_global_func_for_list(function_name: str, input_list: List[Any], function_arguments: Optional[Dict[str,str]]=None):
    final_result: List[Any] = list()
    if function_arguments is None:
        function_arguments = dict()
    for input_data in input_list:
        final_result.append(globals()[function_name](input_data, **function_arguments))
    return final_result

def message_parser(beautiful_soup_parser:BeautifulSoupHtmlParser, title_for_result: str, incoming_message:List[Dict[str, str]]) -> Dict[str, Any]:
    result_from_command: Union[str, List[Any]] = str()
    for single_command_line in incoming_message:
        function_name = single_command_line.pop("function_name")
        if hasattr(beautiful_soup_parser, function_name):
            if isinstance(result_from_command, str):
                result_from_command = getattr(beautiful_soup_parser, function_name)(**single_command_line)
            elif isinstance(result_from_command, list): # type: ignore 
                result_from_command = run_getattr_for_list(beautiful_soup_parser=beautiful_soup_parser,
                                                           function_name=function_name, 
                                                           input_list=result_from_command, 
                                                           function_arguments=single_command_line
                                                           )
        #  Not the sharpest tool in the shed
        elif function_name in globals():
            if isinstance(result_from_command, list):
                result_from_command = run_global_func_for_list(function_name=function_name, 
                                                               input_list=result_from_command, 
                                                               function_arguments=single_command_line
                                                               )
    return {title_for_result: result_from_command}