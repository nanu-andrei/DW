import asyncio
import json
import sys
from datetime import date

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from infrastructure.adapters.cassandra.asset_repository import CassandraAssetRepository
from infrastructure.adapters.cassandra.data_source_repository import CassandraDataSourceRepository
from infrastructure.adapters.cassandra.time_series_repository import CassandraTimeSeriesRepository
from application.use_cases.list_assets import ListAssetsUseCase
from application.use_cases.get_asset_details import GetAssetDetailsUseCase
from application.use_cases.list_data_sources import ListDataSourcesUseCase
from application.use_cases.get_data_source_details import GetDataSourceDetailsUseCase
from application.use_cases.get_time_series import GetTimeSeriesUseCase
from domain.value_objects.pagination import PageRequest

app = Server("nanu-financial-dw")

# Lazy-init repos
_asset_repo = None
_ds_repo = None
_ts_repo = None


def _get_repos():
    global _asset_repo, _ds_repo, _ts_repo
    if _asset_repo is None:
        _asset_repo = CassandraAssetRepository()
        _ds_repo = CassandraDataSourceRepository()
        _ts_repo = CassandraTimeSeriesRepository()
    return _asset_repo, _ds_repo, _ts_repo


TOOLS = [
    Tool(
        name="list_assets",
        description=(
            "Returns a paginated list of financial asset IDs available in the "
            "data warehouse. Use to discover what instruments exist."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "offset": {
                    "type": "integer",
                    "default": 0,
                    "description": "Starting position",
                },
                "limit": {
                    "type": "integer",
                    "default": 20,
                    "description": "Max items to return (1-100)",
                },
            },
        },
    ),
    Tool(
        name="get_asset_details",
        description=(
            "Returns all temporal versions of a specific asset. The first item "
            "is the latest version. Use after discovering an asset ID via list_assets."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {
                    "type": "string",
                    "description": "The asset identifier",
                }
            },
            "required": ["assetId"],
        },
    ),
    Tool(
        name="list_data_sources",
        description=(
            "Returns a paginated list of data source IDs (financial data providers) "
            "in the warehouse."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "offset": {"type": "integer", "default": 0},
                "limit": {"type": "integer", "default": 20},
            },
        },
    ),
    Tool(
        name="get_data_source_details",
        description=(
            "Returns details about a specific data source/provider including "
            "its supported attributes."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "dataSourceId": {"type": "string"}
            },
            "required": ["dataSourceId"],
        },
    ),
    Tool(
        name="get_time_series_data",
        description=(
            "Returns time-series records for a specific asset and data source "
            "within a bounded date range. Records are newest-first. Only the "
            "latest version per business date is returned. Max interval is 365 days."
        ),
        inputSchema={
            "type": "object",
            "properties": {
                "assetId": {"type": "string"},
                "dataSourceId": {"type": "string"},
                "startBusinessDate": {
                    "type": "string",
                    "description": "YYYY-MM-DD",
                },
                "endBusinessDate": {
                    "type": "string",
                    "description": "YYYY-MM-DD",
                },
                "includeAttributes": {
                    "type": "boolean",
                    "default": False,
                },
            },
            "required": [
                "assetId",
                "dataSourceId",
                "startBusinessDate",
                "endBusinessDate",
            ],
        },
    ),
]


@app.list_tools()
async def list_tools():
    return TOOLS


@app.call_tool()
async def call_tool(name: str, arguments: dict):
    asset_repo, ds_repo, ts_repo = _get_repos()

    try:
        if name == "list_assets":
            uc = ListAssetsUseCase(asset_repo=asset_repo)
            page = await uc.execute(
                PageRequest(
                    offset=arguments.get("offset", 0),
                    limit=min(arguments.get("limit", 20), 100),
                )
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "items": page.items,
                            "offset": page.offset,
                            "limit": page.limit,
                            "total": page.total,
                            "has_next": page.has_next,
                        }
                    ),
                )
            ]

        elif name == "get_asset_details":
            asset_id = arguments.get("assetId", "")
            if not asset_id:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps({"error": "assetId is required"}),
                    )
                ]
            uc = GetAssetDetailsUseCase(asset_repo=asset_repo)
            versions = await uc.execute(asset_id)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        [
                            {
                                "id": v.id,
                                "system_date": v.system_date.isoformat(),
                                "name": v.name,
                                "description": v.description,
                                "attributes": v.attributes,
                            }
                            for v in versions
                        ]
                    ),
                )
            ]

        elif name == "list_data_sources":
            uc = ListDataSourcesUseCase(ds_repo=ds_repo)
            page = await uc.execute(
                PageRequest(
                    offset=arguments.get("offset", 0),
                    limit=min(arguments.get("limit", 20), 100),
                )
            )
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        {
                            "items": page.items,
                            "offset": page.offset,
                            "limit": page.limit,
                            "total": page.total,
                            "has_next": page.has_next,
                        }
                    ),
                )
            ]

        elif name == "get_data_source_details":
            ds_id = arguments.get("dataSourceId", "")
            if not ds_id:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": "dataSourceId is required"}
                        ),
                    )
                ]
            uc = GetDataSourceDetailsUseCase(ds_repo=ds_repo)
            versions = await uc.execute(ds_id)
            return [
                TextContent(
                    type="text",
                    text=json.dumps(
                        [
                            {
                                "id": v.id,
                                "system_date": v.system_date.isoformat(),
                                "name": v.name,
                                "description": v.description,
                                "attributes": sorted(v.attributes),
                            }
                            for v in versions
                        ]
                    ),
                )
            ]

        elif name == "get_time_series_data":
            asset_id = arguments.get("assetId", "")
            ds_id = arguments.get("dataSourceId", "")
            start_str = arguments.get("startBusinessDate", "")
            end_str = arguments.get("endBusinessDate", "")

            if not all([asset_id, ds_id, start_str, end_str]):
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": "All required fields must be provided"}
                        ),
                    )
                ]

            try:
                start = date.fromisoformat(start_str)
                end = date.fromisoformat(end_str)
            except ValueError:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": "Invalid date format. Use YYYY-MM-DD."}
                        ),
                    )
                ]

            if (end - start).days > 365:
                return [
                    TextContent(
                        type="text",
                        text=json.dumps(
                            {"error": "Date range cannot exceed 365 days."}
                        ),
                    )
                ]

            uc = GetTimeSeriesUseCase(ts_repo=ts_repo)
            points = await uc.execute(asset_id, ds_id, start, end)

            records = []
            all_attrs = set()
            for p in points:
                values: dict = {}
                values.update(p.values_double)
                values.update(p.values_int)
                values.update(p.values_text)
                all_attrs.update(values.keys())
                records.append(
                    {
                        "businessDate": p.business_date.isoformat(),
                        "values": values,
                    }
                )

            result: dict = {
                "data": {
                    "assetId": asset_id,
                    "datasourceId": ds_id,
                    "records": records,
                }
            }
            if arguments.get("includeAttributes", False):
                result["attributes"] = sorted(all_attrs)

            return [TextContent(type="text", text=json.dumps(result))]

        else:
            return [
                TextContent(
                    type="text",
                    text=json.dumps({"error": f"Unknown tool: {name}"}),
                )
            ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=json.dumps({"error": str(e)}),
            )
        ]


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
