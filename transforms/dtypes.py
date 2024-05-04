from tclogger import logger


class DataTyper:
    """
    DTYPES maps dtype from python to postgresql
    - https://www.postgresql.org/docs/current/datatype.html#DATATYPE-TABLE
    """

    DTYPES = {
        int: "int8",
        float: "float8",
        str: "text",
        bool: "bool",
        dict: "json",
    }

    def py_val_to_sql_dtype(self, val):
        py_dtype = type(val)
        sql_dtype = DataTyper.DTYPES.get(py_dtype, None)

        logger.note(f"val: {val}, sql_dtype: {sql_dtype}")

        if py_dtype == list:
            if len(val) == 0:
                raise ValueError(f"Invalid type: Empty list")
            if type(val[0]) == list:
                raise ValueError(f"Invalid type: Nested list")
            item = val[0]
            item_sql_dtype = self.py_val_to_sql_dtype(item)
            return f"{item_sql_dtype}[]"
        elif py_dtype in DataTyper.DTYPES.keys():
            return sql_dtype
        elif sql_dtype is None:
            raise ValueError(f"Invalid type: {val}")
        else:
            raise ValueError(f"Invalid type: {val}")


if __name__ == "__main__":
    data_typer = DataTyper()
    variables = [
        1,
        1.0,
        "string",
        True,
        {"key": "value"},
        [1, 2, 3],
        [1.0, 2.0, 3.0],
        ["a", "b", "c"],
        [True, False, True],
        [{"key1": "value1"}, {"key2": "value2"}, {"key3": "value3"}],
    ]
    for var in variables:
        sql_dtype = data_typer.py_val_to_sql_dtype(var)
        print(f"{str(var):>8} => {sql_dtype}")

    # python -m transforms.dtypes
