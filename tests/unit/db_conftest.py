from datetime import date, datetime
from decimal import Decimal
from json import dumps as jdumps
from typing import Any, Callable, Dict, List

from httpx import URL, Request, Response, codes
from pytest import fixture

from firebolt.async_db.cursor import JSON_OUTPUT_FORMAT, ColType, Column
from firebolt.common.settings import Settings
from firebolt.db import ARRAY, DATETIME64, DECIMAL

QUERY_ROW_COUNT: int = 10


@fixture
def query_description() -> List[Column]:
    return [
        Column("uint8", "UInt8", None, None, None, None, None),
        Column("uint16", "UInt16", None, None, None, None, None),
        Column("uint32", "UInt32", None, None, None, None, None),
        Column("int32", "Int32", None, None, None, None, None),
        Column("uint64", "UInt64", None, None, None, None, None),
        Column("int64", "Int64", None, None, None, None, None),
        Column("float32", "Float32", None, None, None, None, None),
        Column("float64", "Float64", None, None, None, None, None),
        Column("string", "String", None, None, None, None, None),
        Column("date", "Date", None, None, None, None, None),
        Column("date32", "Date32", None, None, None, None, None),
        Column("datetime", "DateTime", None, None, None, None, None),
        Column("datetime64", "DateTime64(4)", None, None, None, None, None),
        Column("bool", "UInt8", None, None, None, None, None),
        Column("array", "Array(UInt8)", None, None, None, None, None),
        Column("decimal", "Decimal(12, 34)", None, None, None, None, None),
    ]


@fixture
def python_query_description() -> List[Column]:
    return [
        Column("uint8", int, None, None, None, None, None),
        Column("uint16", int, None, None, None, None, None),
        Column("uint32", int, None, None, None, None, None),
        Column("int32", int, None, None, None, None, None),
        Column("uint64", int, None, None, None, None, None),
        Column("int64", int, None, None, None, None, None),
        Column("float32", float, None, None, None, None, None),
        Column("float64", float, None, None, None, None, None),
        Column("string", str, None, None, None, None, None),
        Column("date", date, None, None, None, None, None),
        Column("date32", date, None, None, None, None, None),
        Column("datetime", datetime, None, None, None, None, None),
        Column("datetime64", DATETIME64(4), None, None, None, None, None),
        Column("bool", int, None, None, None, None, None),
        Column("array", ARRAY(int), None, None, None, None, None),
        Column("decimal", DECIMAL(12, 34), None, None, None, None, None),
    ]


@fixture
def query_data() -> List[List[ColType]]:
    return [
        [
            i,
            256,
            70000,
            -32768,
            922337203685477580,
            -922337203685477580,
            1,
            "1.0387398573",
            "some text",
            "2019-07-31",
            "1860-01-31",
            "2019-07-31 01:01:01",
            "2020-07-31 01:01:01.1234",
            1,
            [1, 2, 3, 4],
            "123456789.123456789123456789123456789",
        ]
        for i in range(QUERY_ROW_COUNT)
    ]


@fixture
def python_query_data() -> List[List[ColType]]:
    return [
        [
            i,
            256,
            70000,
            -32768,
            922337203685477580,
            -922337203685477580,
            1,
            1.0387398573,
            "some text",
            date(2019, 7, 31),
            date(1860, 1, 31),
            datetime(2019, 7, 31, 1, 1, 1),
            datetime(2020, 7, 31, 1, 1, 1, 123400),
            1,
            [1, 2, 3, 4],
            Decimal("123456789.123456789123456789123456789"),
        ]
        for i in range(QUERY_ROW_COUNT)
    ]


@fixture
def server_side_async_id_callback(server_side_async_id) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {"query_id": server_side_async_id}
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def server_side_async_missing_id_callback(server_side_async_id) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {"no_id": server_side_async_id}
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def server_side_async_id() -> str:
    return "1a3f53d"


@fixture
def server_side_async_cancel_callback(server_side_async_id) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {
            "meta": [
                {"name": "host", "type": "String"},
                {"name": "port", "type": "UInt16"},
                {"name": "status", "type": "Int64"},
                {"name": "error", "type": "String"},
                {"name": "num_hosts_remaining", "type": "UInt64"},
                {"name": "num_hosts_active", "type": "UInt64"},
            ],
            "data": [["node1.node.consul", 9000, 0, "", 0, 0]],
            "rows": 1,
            "statistics": {
                "elapsed": 0.116907717,
                "rows_read": 1,
                "bytes_read": 61,
                "time_before_execution": 0.012180623,
                "time_to_execute": 0.104614307,
                "scanned_bytes_cache": 0,
                "scanned_bytes_storage": 0,
            },
        }
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def server_side_async_cancel_callback_error(server_side_async_id) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        return Response(status_code=codes.BAD_REQUEST, json={})

    return do_query


@fixture
def server_side_async_get_status_callback(server_side_async_id) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {
            "engine_name": "engine",
            "query_id": server_side_async_id,
            "status": "ENDED_SUCCESSFULLY",
            "query_start_time": "2020-07-31 01:01:01.1234",
            "query_duration_ms": 0.104614307,
            "original_query": "SELECT 1",
        }
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def server_side_async_get_status_not_yet_availabe_callback(
    server_side_async_id,
) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {
            "engine_name": "",
            "query_id": "",
            "status": "",
            "query_start_time": "",
            "query_duration_ms": "",
            "original_query": "",
        }
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def server_side_async_get_status_error(server_side_async_id) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        return Response(status_code=codes.OK, json="")

    return do_query


@fixture
def server_side_async_missing_query_id_error(server_side_async_id) -> Response:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {
            "engine_name": "engine",
            "query_id": "",
            "status": "ENDED_SUCCESSFULLY",
            "query_start_time": "2020-07-31 01:01:01.1234",
            "query_duration_ms": 0.104614307,
            "original_query": "SELECT 1",
        }
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def query_callback(
    query_description: List[Column], query_data: List[List[ColType]]
) -> Callable:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {
            "meta": [{"name": c.name, "type": c.type_code} for c in query_description],
            "data": query_data,
            "rows": len(query_data),
            "statistics": {
                "elapsed": 0.002983335,
                "time_before_execution": 0.002729331,
                "time_to_execute": 0.000215215,
                "rows_read": 1,
                "bytes_read": 1,
                "scanned_bytes_cache": 0,
                "scanned_bytes_storage": 0,
            },
        }
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def select_one_query_callback(
    query_description: List[Column], query_data: List[List[ColType]]
) -> Callable:
    def do_query(request: Request, **kwargs) -> Response:
        query_response = {
            "meta": [{"name": "select 1", "type": "Int8"}],
            "data": [{"select 1": 1}],
            "rows": 1,
            # Real example of statistics field value, not used by our code
            "statistics": {
                "elapsed": 0.002983335,
                "time_before_execution": 0.002729331,
                "time_to_execute": 0.000215215,
                "rows_read": 1,
                "bytes_read": 1,
                "scanned_bytes_cache": 0,
                "scanned_bytes_storage": 0,
            },
        }
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def query_with_params_callback(
    query_description: List[Column],
    query_data: List[List[ColType]],
    set_params: Dict,
) -> Callable:
    def do_query(request: Request, **kwargs) -> Response:
        set_parameters = request.url.params
        for k, v in set_params.items():
            assert k in set_parameters and set_parameters[k] == encode_param(
                v
            ), "Invalid set parameters passed"
        query_response = {
            "meta": [{"name": c.name, "type": c.type_code} for c in query_description],
            "data": query_data,
            "rows": len(query_data),
            # Real example of statistics field value, not used by our code
            "statistics": {
                "elapsed": 0.002983335,
                "time_before_execution": 0.002729331,
                "time_to_execute": 0.000215215,
                "rows_read": 1,
                "bytes_read": 1,
                "scanned_bytes_cache": 0,
                "scanned_bytes_storage": 0,
            },
        }
        return Response(status_code=codes.OK, json=query_response)

    return do_query


@fixture
def insert_query_callback(
    query_description: List[Column], query_data: List[List[ColType]]
) -> Callable:
    def do_query(request: Request, **kwargs) -> Response:
        return Response(status_code=codes.OK, headers={"content-length": "0"})

    return do_query


def encode_param(p: Any) -> str:
    return jdumps(p).strip('"')


@fixture
def set_params() -> Dict:
    return {"param1": 1, "param2": "2", "param3": 1}


@fixture
def query_url(settings: Settings, db_name: str) -> str:
    return URL(
        f"https://{settings.server}/?database={db_name}"
        f"&output_format={JSON_OUTPUT_FORMAT}"
    )


@fixture
def set_query_url(settings: Settings, db_name: str) -> str:
    return URL(f"https://{settings.server}/?database={db_name}")


@fixture
def query_with_params_url(query_url: str, set_params: str) -> str:
    params_encoded = "&".join([f"{k}={encode_param(v)}" for k, v in set_params.items()])
    query_url = f"{query_url}&{params_encoded}"
