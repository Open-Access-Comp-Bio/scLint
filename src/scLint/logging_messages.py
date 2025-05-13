import logging

##### insert logging style customization here

def log_file_handeling(path:str,is_dir:bool) -> None:
    dobject = {True:'directory',False:'file'}
    logging.info(f'Opening {dobject} from path {path}')

def caught_file_ext() -> None:
    logging.warning(f'Path leads to a file and not a directory! Adjusting variable is_dir to False...')
    logging.info(f'Proceeding with AnnData assembly...')