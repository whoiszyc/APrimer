import pytest

import pandas as pd
import pandas.util.testing as tm
from pandas.util.testing import ensure_clean

from pandas.io.excel import ExcelFile

xlrd = pytest.importorskip("xlrd")
xlwt = pytest.importorskip("xlwt")


def test_read_xlrd_book(read_ext, frame):
    df = frame

    engine = "xlrd"
    sheet_name = "SheetA"

    with ensure_clean(read_ext) as pth:
        df.to_excel(pth, sheet_name)
        book = xlrd.open_workbook(pth)

        with ExcelFile(book, engine=engine) as xl:
            result = pd.read_excel(xl, sheet_name, index_col=0)
            tm.assert_frame_equal(df, result)

        result = pd.read_excel(book, sheet_name=sheet_name,
                               engine=engine, index_col=0)
        tm.assert_frame_equal(df, result)
