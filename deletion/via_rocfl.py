"""
(Under development; doesn't work yet)

This script demonstrates deletion of items from OCFL storage.

Usage:
    uv run ./via_rocfl.py --pids "bdr:12345,bdr:67890"
"""

import argparse, logging, os, pathlib

from dotenv import load_dotenv

## load envars
DOT_ENV_PATH = pathlib.Path( __file__ ).resolve().parents[2] / 'dot_env_files' / 'deletion.env'
load_dotenv( DOT_ENV_PATH )
STORAGE_ROOT_PATH = pathlib.Path( os.environ['STORAGE_ROOT_PATH'] )

## setup logging
lglvl: str = os.environ.get( 'LOGLEVEL', 'DEBUG' )
lglvldct = {
    'DEBUG': logging.DEBUG,
    'INFO': logging.INFO }
logging.basicConfig(
    level=lglvldct[lglvl],  # assigns the level-object to the level-key loaded from the envar
    format='[%(asctime)s] %(levelname)s [%(module)s-%(funcName)s()::%(lineno)d] %(message)s',
    datefmt='%d/%b/%Y %H:%M:%S' )
log = logging.getLogger( __name__ )


## manager function
def delete_items( pids ):
    for pid in pids:
        log.debug( f'deleting pid, ``{pid}``' )
        try:
            pass
            ## cd to repo root
            os.chdir( STORAGE_ROOT_PATH.resolve() )  # `str(pathlib-obj)` also works, but resolve() guarantees an absolute path
            ## assemble command
            rocfl_cmd = [
                
            ]
            ## run command
        except Exception as e:
            msg = f'problem deleting pid, ``{pid}``; exception, ``{e}``'
            log.exception( msg )

        ## cd to repo root


if __name__ == '__main__':
    ## set up argparser ---------------------------------------------
    log.debug( '\n\nstarting processing' )
    parser = argparse.ArgumentParser(description='Deletes OCFL pid.')
    parser.add_argument('--pids', required=True, help='comma-separated list of pids to delete')
    args = parser.parse_args()
    log.debug( f'args: {args}' )
    ## get PIDS -----------------------------------------------------
    submitted_pids = args.pids.split(',')
    assert type( submitted_pids ) == list
    pids = [ pd.strip() for pd in submitted_pids ]  # removes any whitespace before or after the pid
    log.debug( f'cleaned pids, ``{pids}``' )
    ## call manager function ----------------------------------------
    delete_items( pids )
    ## end ----------------------------------------------------------
    log.debug( 'done processing' )
