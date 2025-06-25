import logging
from pathlib import Path

##### insert logging style customization here

def activate() -> None:
    logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

def log_file_handeling(path:str,is_dir:bool) -> None:
    # This function was initially built to be flexible to user needs
    # the user could pass either a single file or a directory of files.
    dobject = {True:'directory',False:'file'}
    logging.info(f'Opening {dobject[is_dir]} from path {path}')

def caught_file_ext() -> None:
    logging.warning(f'Path leads to a file and not a directory! Adjusting variable is_dir to False...')
    logging.info(f'Proceeding with AnnData assembly...')

def bad_file(pathway) -> None:
    logging.warning(f"The provided pathway: {pathway} doesn't exist!!!")

def opening_file(component_name:str,file_name:str=None,file_list:list=None) -> None:
    if file_list:
        extracted_names = [f.name for f in file_list]
        file_name = ','.join(extracted_names)
    logging.info(f'Opening {file_name} for {component_name}')

def assign_adata(component_name:str):
    logging.info(f'Assigning {component_name} for AnnData Object')

def save_to_disk(var:str, fname:str):
    logging.info(f'Saving {var} to {fname}')

def success():
    logging.info('Operation was successful')

def error(issue, issue_name, issue_handaling=None):
    logging.error(f"There was an issue with {issue}, a {issue_name} was returned!")
    if issue_handaling:
        logging.info(issue_handaling)