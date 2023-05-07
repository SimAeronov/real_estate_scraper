from typing import Union

def get_element_split_by(input_string:str, element:Union[str, int], split_by:str) -> str:
    return input_string.split(split_by)[int(element)]

def get_element_replaced_with(input_string:str, old_string:str, new_string:str) -> str:
    return input_string.replace(old_string, new_string)