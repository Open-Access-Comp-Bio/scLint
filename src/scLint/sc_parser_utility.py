import file_ext
from pathlib import Path

FILE_EXT = file_ext.FILE_EXTS

def pool_files(path:str)->dict:
    """
    Input: path to a directory with files
    Output: dict witt with dict name (key)
    with a list of files (values)
    """
    path_object = Path(path)
    path_entries = [entry for entry in path_object.iterdir() if entry.is_file() if entry.name != '.DS_Store']
    path_dict = {'dir':path_object, 'files':path_entries}
    return path_dict

# IT might be better to for go this and have the users input
# all of the files they want to run or create an input template that
# can be read instead. The second step seems like a good idea. maybe
# we can attempt to run the automatted path but if an error occurs we can
# ask for the metadata.
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
        path = str(file_path)
        if "_spliced_counts" in path:
            identified_files["spliced"] = file_path
        elif "_unspliced_counts" in path:
            identified_files["unspliced"] = file_path
        elif "_counts" and not "_spliced_counts" and not "_unspliced_counts":
            identified_files['X'] = file_path
        elif "_metadata" in path:
            identified_files['metadata'] = file_path
        elif "names" in path:
            identified_files['var'] = file_path
        else:
            identified_files['obs'].append(file_path)
    return identified_files

def open_files(identified_files:dict):
    """
    Input: A dict with identified files and their paths
    Output: dict with pandas DataFrames.
    """
    pass