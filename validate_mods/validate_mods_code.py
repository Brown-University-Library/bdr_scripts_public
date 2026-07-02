"""
Validates MODS XML against the schema in the root MODS element.
"""

import argparse
import os
from io import BytesIO
from pathlib import Path

import httpx
from dotenv import load_dotenv
from lxml import etree

## the dotenv-directory is in the "stuff" directory.
DOTENV_PATH: Path = Path(__file__).resolve().parents[2] / 'dot_env_files' / 'validate_mods.env'

## load variables from script-specific dotenv file
load_dotenv(DOTENV_PATH)


SCHEMA_REQUEST_TIMEOUT: float = float(os.getenv('VM__SCHEMA_REQUEST_TIMEOUT', '30'))


def parse_xml(xml_file_path: Path) -> etree._ElementTree | None:
    """
    Parses an XML file.

    Called by: validate_mods_xml()
    """
    parser = etree.XMLParser()
    xml_doc = None
    try:
        with xml_file_path.open('rb') as xml_file:
            xml_doc = etree.parse(xml_file, parser)
    except (etree.XMLSyntaxError, OSError) as err:
        print(f'Error reading XML file: {err}')
    return xml_doc


def get_schema_url(xml_doc: etree._ElementTree) -> str | None:
    """
    Gets the schema URL or path from XML schema-location metadata.

    Called by: validate_mods_xml()
    """
    schema_location = xml_doc.getroot().attrib.get('{http://www.w3.org/2001/XMLSchema-instance}schemaLocation')
    schema_url = None
    if not schema_location:
        print('No schema location found in XML.')
    else:
        schema_location_parts = schema_location.split()
        if len(schema_location_parts) < 2:
            print('Schema location does not include a schema URL.')
        else:
            schema_url = schema_location_parts[1]
    return schema_url


def load_schema(schema_url: str) -> etree.XMLSchema | None:
    """
    Loads an XML schema from a URL or local file path.

    Called by: validate_mods_xml()
    """
    parser = etree.XMLParser()
    xml_schema = None
    try:
        if schema_url.startswith(('http://', 'https://')):
            response = httpx.get(schema_url, timeout=SCHEMA_REQUEST_TIMEOUT)
            response.raise_for_status()
            schema_doc = etree.parse(BytesIO(response.content), parser)
        else:
            with Path(schema_url).open('rb') as schema_file:
                schema_doc = etree.parse(schema_file, parser)
        xml_schema = etree.XMLSchema(schema_doc)
    except (etree.XMLSyntaxError, OSError, httpx.HTTPError) as err:
        print(f'Error loading schema: {err}')
    return xml_schema


def validate_with_schema(xml_doc: etree._ElementTree, xml_schema: etree.XMLSchema) -> bool:
    """
    Validates an XML document against an XML schema.

    Called by: validate_mods_xml()
    """
    valid = xml_schema.validate(xml_doc)
    if valid:
        print('The XML is valid according to the schema.')
    else:
        print('The XML is invalid according to the schema.')
        for error in xml_schema.error_log:
            print(error.message)
    return valid


def validate_mods_xml(xml_file_path: str) -> bool:
    """
    Validates a MODS XML file against its embedded schema.

    Called by: main()
    """
    valid = False
    xml_doc = parse_xml(Path(xml_file_path))
    if xml_doc is not None:
        schema_url = get_schema_url(xml_doc)
        if schema_url:
            xml_schema = load_schema(schema_url)
            if xml_schema is not None:
                valid = validate_with_schema(xml_doc, xml_schema)
    return valid


def main() -> None:
    """
    Parses CLI args and validates a MODS XML file.

    Called by: command line
    """
    parser = argparse.ArgumentParser(description='Validate a MODS XML file against its embedded schema.')
    parser.add_argument('--mods-path', required=True, help='Path to the MODS XML file to validate.')
    args = parser.parse_args()
    validate_mods_xml(args.mods_path)


if __name__ == '__main__':
    main()
