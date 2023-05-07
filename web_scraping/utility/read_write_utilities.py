import pandas as pd
import pyarrow as pa
from pathlib import Path

from typing import List, Any

class PandasAndParquet:
    def __init__(self) -> None:
        self.__data_frame:pd.DataFrame = pd.DataFrame()
        
    
    def append_column_to_dataframe(self, column_name:str, column_data: List[Any]) -> None:
        name_and_data_for_df = {column_name: column_data}
        self.__data_frame = self.__data_frame.assign(**name_and_data_for_df) #type: ignore
    
    def save_dataframe_as_parquet(self, path_to_save_folder:str, just_filename:str) -> None:
        """  
        Used to save current dataframe to a parquet file.

        Kwargs:
        ------
                path_to_save_folder : str
                    Path using FORWARD slashes '/'
                just_filename : str
                    parquet filename without .parquet
        """

        parquet_save_dir =  Path(path_to_save_folder) / just_filename
        self.__data_frame.to_parquet(parquet_save_dir)

    def read_parquet_as_dataframe(self, path_to_file_folder:str, just_filename:str) -> None:
        parquet_read_dir =  Path(path_to_file_folder) / just_filename
        self.__data_frame = pd.read_parquet(parquet_read_dir)
    
    def get_data_as_dataframe(self) -> pd.DataFrame:
        return self.__data_frame

    def get_data_head(self):
        print(self.__data_frame.head())