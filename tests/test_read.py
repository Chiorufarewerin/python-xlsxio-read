import os
import pytest
import xlsxio
import datetime
from . import test_read_data


TYPES = (int, str, str, datetime.datetime, int, float, datetime.datetime, bool)
MAIN_DIR = os.path.dirname(os.path.abspath(__name__))
CURRENT_DIR = os.path.join(MAIN_DIR, 'tests')
XLSX_DIR = os.path.join(CURRENT_DIR, 'xlsx')
XLSX_TEST_FILE_PATH = os.path.join(XLSX_DIR, 'test_file_base.xlsx')


def test_get_xlsxioread_version_string():
    assert xlsxio.get_xlsxioread_version_string() == '0.2.30'


class TestReadXlsx:
    def get_reader(self) -> xlsxio.XlsxioReader:
        return xlsxio.XlsxioReader(XLSX_TEST_FILE_PATH)

    def base_read(self, reader: xlsxio.XlsxioReader):
        for sheet_name in reader.get_sheet_names():
            with reader.get_sheet(sheet_name) as sheet:
                assert sheet_name in test_read_data.TEST_READ_DATA_STRINGS
                assert sheet.read_data() == test_read_data.TEST_READ_DATA_STRINGS[sheet_name]
            with reader.get_sheet(sheet_name, default_type=bytes) as sheet:
                assert sheet_name in test_read_data.TEST_READ_DATA_BYTES
                assert sheet.read_data() == test_read_data.TEST_READ_DATA_BYTES[sheet_name]
            with reader.get_sheet(sheet_name, types=TYPES) as sheet:
                assert sheet_name in test_read_data.TEST_READ_DATA_TYPES
                assert sheet.read_data() == test_read_data.TEST_READ_DATA_TYPES[sheet_name]

    def test_read_from_filename(self):
        reader = xlsxio.XlsxioReader(XLSX_TEST_FILE_PATH)
        self.base_read(reader)

    def test_read_from_bytes(self):
        with open(XLSX_TEST_FILE_PATH, 'rb') as f:
            reader = xlsxio.XlsxioReader(f.read())
        self.base_read(reader)

    def test_read_from_file(self):
        f = open(XLSX_TEST_FILE_PATH, 'rb')
        reader = xlsxio.XlsxioReader(f)
        self.base_read(reader)
        f.close()

    def test_read_from_filename_not_existing(self):
        with pytest.raises(FileNotFoundError) as ex:
            xlsxio.XlsxioReader('notfound.xlsx')
        assert str(ex.value) == 'No such file: notfound.xlsx'

    def test_read_from_incorrect_bytes(self):
        with pytest.raises(ValueError) as ex:
            xlsxio.XlsxioReader(b'')
        assert str(ex.value) == 'Incorrect value of xlsx file data'

    def test_read_from_incorrect_file(self):
        filename = os.path.join(CURRENT_DIR, '__init__.py')  # just any not xlsx file
        f = open(filename, 'rb')
        with pytest.raises(ValueError) as ex:
            xlsxio.XlsxioReader(f)
        assert str(ex.value) == 'Incorrect value of xlsx file data'

    def test_read_from_closed_file(self):
        f = open(XLSX_TEST_FILE_PATH, 'rb')
        f.close()
        with pytest.raises(ValueError) as ex:
            xlsxio.XlsxioReader(f)
        assert str(ex.value) == 'I/O operation on closed file'

    def test_read_incorrect_type(self):
        with pytest.raises(TypeError) as ex:
            xlsxio.XlsxioReader(123)
        assert str(ex.value) == 'Expected string, bytes or file object, not "int"'

    def test_get_sheet_names(self):
        with self.get_reader() as reader:
            assert reader.get_sheet_names() == ('Sheet1', 'Привет', 'test_empty')

    def test_get_sheet_names_reader_closed(self):
        with self.get_reader() as reader:
            pass
        with pytest.raises(RuntimeError) as ex:
            reader.get_sheet_names()
        assert str(ex.value) == 'Reader is closed or not opened'

    def test_sheet_incorrect_flags_value(self):
        with self.get_reader() as reader:
            with pytest.raises(ValueError) as ex:
                reader.get_sheet(flags=8)
        assert str(ex.value) == 'Incorrect flags value'

    def test_sheet_incorrect_default_type_value(self):
        with self.get_reader() as reader:
            with pytest.raises(ValueError) as ex:
                reader.get_sheet(default_type=list)
        assert str(ex.value) == 'Incorrect default_type value'

    def test_sheet_incorrect_sheetname_value(self):
        with self.get_reader() as reader:
            with pytest.raises(TypeError) as ex:
                reader.get_sheet(123)
        assert str(ex.value) == 'Value sheetname must be str or None'

    def test_sheet_sheetname_not_found(self):
        with self.get_reader() as reader:
            with pytest.raises(ValueError) as ex:
                reader.get_sheet('test')
        assert str(ex.value) == 'No such sheet: test'

    def test_sheet_icorrect_types(self):
        with self.get_reader() as reader:
            with pytest.raises(ValueError) as ex:
                reader.get_sheet(types=[type])
        assert str(ex.value) == 'Incorrect types value'
