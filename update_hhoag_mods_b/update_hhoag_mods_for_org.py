"""
Example usage:
    $ python ./update_hhoag_mods.py --org_list "fooA,fooB" --mods_dir "bar" --tracker_dir "baz" 

Note that one of the functions has a doctest. All doctests can be run with the following command:
`python -m doctest ./update_hhoag_mods_b/update_hhoag_mods_for_org.py -v`

"""

import argparse, json, logging, os, pathlib, pprint, sys, time


## setup logging ----------------------------------------------------
lglvl: str = os.environ.get( 'HHDICT__LOGLEVEL', 'DEBUG' )
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[lglvl],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )


## helpers start ----------------------------------------------------


def validate_arg_paths( mods_directory_path: pathlib.Path, tracker_directory_path: pathlib.Path ) -> None:
    """ Validates argument paths.
        Called by dundermain. """
    if not mods_directory_path.exists():
        print( f'Error: The path {mods_directory_path} does not exist.', file=sys.stderr )
        sys.exit(1)
    if not tracker_directory_path.is_dir():
        print( f'Error: The path {tracker_directory_path} is not a directory.', file=sys.stderr )
        sys.exit(1)
    return


def get_org_tracker_filepath( org: str, tracker_directory_path: pathlib.Path ) -> pathlib.Path:
    """ Gets the org's tracker file path.
        Called by manage_org_mods_update(). 
    Doctest:
    >>> get_org_tracker_filepath( 'HH123456', pathlib.Path('/path/to/foo') )    
    PosixPath('/path/to/foo/HH12/3456/HH123456__whole_org_updated.json')
    """
    part_a, part_b = org[:4], org[4:8]
    org_tracker_filepath = tracker_directory_path / part_a / part_b / f'{org}__whole_org_updated.json'  # pathlib way of joining paths
    log.debug(f'org_tracker_filepath, ``{org_tracker_filepath}``')
    return org_tracker_filepath


def check_org_in_tracker( org_tracker_filepath: pathlib.Path ) -> bool:
    """ Checks if org is already in tracker file.
        Called by manage_org_mods_update(). """
    return_val = False
    if org_tracker_filepath.exists():
        return_val = True
    log.debug( f'return_val `{return_val}`' )
    return return_val


def get_filepath_data( org: str, mods_directory_path: pathlib.Path ) -> dict:
    """ Gets org data.
        Called by manage_org_mods_update(). """
    org_data = {}
    mods_paths = list( mods_directory_path.rglob('*mods.xml') )
    org_data = {}
    for mods_filepath in mods_paths:
        if org in mods_filepath.name:
            item_dict = { 'path:': str(mods_filepath) }
            hh_id: str = parse_id( mods_filepath )
            org_data[ hh_id ] = item_dict
    log.debug( f'org_data, partial, ``{pprint.pformat(org_data)[0:1000]}...``' )
    return org_data


def parse_id( mods_file: pathlib.Path ) -> str:
    """ Returns hall-hoag-id from mods-filepath.
        Called by make_id_dict() 
    >>> mods_filepath = pathlib.Path( '/path/to/HH123456.mods.xml' )  # org
    >>> parse_id( mods_filepath )
    'HH123456'
    >>> mods_filepath = pathlib.Path( '/path/to/HH123456_0001.mods.xml' )  # item
    >>> parse_id( mods_filepath )
    'HH123456_0001'
    """
    filename_a: str = mods_file.stem  # removes .xml but still contains .mods
    filename_b: str = filename_a.split('.')[0]  # removes .mods    
    return filename_b

## helpers end ------------------------------------------------------


## manager ----------------------------------------------------------
def manage_org_mods_update( orgs_list: list, mods_directory_path: pathlib.Path, tracker_directory_path: pathlib.Path ) -> None:
    """ Manager function
        Called by dundermain. """
    for org in orgs_list:
        org_tracker_filepath: pathlib.Path = get_org_tracker_filepath( org, tracker_directory_path )
        org_already_processed: bool = check_org_in_tracker( org_tracker_filepath )
        if org_already_processed:
            continue
        org_data: dict = get_filepath_data( org, mods_directory_path )  # value-dict contains path info at this point

    return


## dunndermain ------------------------------------------------------
if __name__ == '__main__':
    """ Receives and validates dir-path, then calls manager function. """
    assert pathlib.Path.cwd().name == 'bdr_scripts_public', f"Error: wrong directory; cd to the `bdr_sripts_public` directory and try again."
    start_time = time.monotonic()
    ## prep args ----------------------------------------------------
    parser = argparse.ArgumentParser(description='Recursively finds JSON files in specified directory.')
    parser.add_argument( '--org_list', required=True, help='orgs to process; example "HH123456" or "HH123456,HH654321"' )
    parser.add_argument( '--mods_dir', required=True, help='path to directory containing pre-made org-mods and item-mods files' )
    parser.add_argument( '--tracker_dir', required=True, help='path to directory containing the tracker files' )
    args = parser.parse_args()
    ## grab args ----------------------------------------------------
    orgs_list = [ ', '.join( args.org_list.split(',') ) ]
    mods_directory_path = pathlib.Path(args.mods_dir)
    tracker_directory_path = pathlib.Path(args.tracker_dir)
    ## validate path-------------------------------------------------
    validate_arg_paths( mods_directory_path, tracker_directory_path )
    ## get to work --------------------------------------------------
    manage_org_mods_update( orgs_list, mods_directory_path, tracker_directory_path )
    elapsed_time = time.monotonic() - start_time
    log.info( f'elapsed time, ``{elapsed_time:.2f}`` seconds' )
