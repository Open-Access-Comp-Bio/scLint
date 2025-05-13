import file_ext
from pathlib import Path

FILE_EXT = file_ext.extensions

def create_PATH(path:str)->dict:
    path_object = Path(path)
    path_entries = [entry for entry in path_object.iterdir() if entry.is_file()]
    path_dict = {'dir':path_object, 'files':path_entries}
    return path_dict

def id_files(path_dict:dict)->dict:
    """
    This function takes in a dictionary and sorts the file paths
    from the input dictionary on what their corresponding AnnData
    entry points are
    """
    # TODO consider using default dict and regex
    # to simplify and scale file identification
    # biggest weak point is obs potentially
    # an assumption is made that all the files in
    # obs will be mergable with each other.
    identified_files = {}
    identified_files['obs'] = []
    for file_path in path_dict['files']:
        full_path = path_dict['dir'] + file_path
        if "_spliced_counts" in full_path:
            identified_files["spliced"] = full_path
        elif "_unspliced_counts" in full_path:
            identified_files["unspliced"] = full_path
        elif "_counts" and not "_spliced_counts" and not "_unspliced_counts":
            identified_files['X'] = full_path
        elif "_metadata" in full_path:
            identified_files['metadata'] = full_path
        elif "names" in full_path:
            identified_files['var'] = full_path
        else:
            identified_files['obs'].append(full_path)
    return identified_files