"""
Usage:
    uv run -m unittest ./test_validate_mods_code.py
"""

import importlib.util
import tempfile
import textwrap
import unittest
from pathlib import Path

CURRENT_DIR = Path(__file__).resolve().parent
VALIDATE_MODS_CODE_PATH = CURRENT_DIR / 'validate_mods_code.py'
spec = importlib.util.spec_from_file_location('validate_mods_code', VALIDATE_MODS_CODE_PATH)
if spec is None or spec.loader is None:
    raise ImportError(f'Could not load {VALIDATE_MODS_CODE_PATH}')
validate_mods_code = importlib.util.module_from_spec(spec)
spec.loader.exec_module(validate_mods_code)


class ValidateModsXmlTest(unittest.TestCase):
    def test_validate_mods_xml_returns_true_for_valid_xml_with_local_schema(self) -> None:
        """
        Checks that validation succeeds for XML that references a valid local schema.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            schema_path = temp_path / 'mods.xsd'
            xml_path = temp_path / 'valid_mods.xml'

            schema_path.write_text(
                textwrap.dedent(
                    """
                    <xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema"
                        targetNamespace="http://www.loc.gov/mods/v3"
                        xmlns="http://www.loc.gov/mods/v3"
                        elementFormDefault="qualified">
                      <xs:element name="mods" type="xs:string" />
                    </xs:schema>
                    """
                ).strip(),
                encoding='utf-8',
            )
            xml_path.write_text(
                textwrap.dedent(
                    f"""
                    <mods:mods xmlns:mods="http://www.loc.gov/mods/v3"
                        xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
                        xsi:schemaLocation="http://www.loc.gov/mods/v3 {schema_path}">
                        valid content
                    </mods:mods>
                    """
                ).strip(),
                encoding='utf-8',
            )

            result = validate_mods_code.validate_mods_xml(str(xml_path))

        self.assertTrue(result)

    def test_validate_mods_xml_returns_false_without_schema_location(self) -> None:
        """
        Checks that validation fails when the XML omits schema location metadata.
        """
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            xml_path = temp_path / 'missing_schema_location.xml'
            xml_path.write_text(
                textwrap.dedent(
                    """
                    <mods:mods xmlns:mods="http://www.loc.gov/mods/v3">
                        missing schema location
                    </mods:mods>
                    """
                ).strip(),
                encoding='utf-8',
            )

            result = validate_mods_code.validate_mods_xml(str(xml_path))

        self.assertFalse(result)


if __name__ == '__main__':
    unittest.main()
