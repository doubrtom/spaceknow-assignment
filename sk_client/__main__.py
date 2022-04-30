"""Run main task for sk_client project."""
from pathlib import Path

from .api_client import SpaceKnowClient
from . import utils


def set_auth_token_to_api_client(space_know_client: SpaceKnowClient):
    """Set auth token to SpaceKnowClient.

    It tries to load auth token from file, so we do not spam AUTH server.
    If not found, get auth token from auth server and save it to file.
    """
    auth_token_file = Path("auth_token.txt")

    if auth_token_file.is_file():
        with auth_token_file.open("r", encoding="utf-8") as file:
            id_token = file.read().strip()
        space_know_client.set_auth_token(id_token)
    else:
        auth_data = space_know_client.auth_api.get_auth_data(utils.load_credentials())
        with auth_token_file.open("w", encoding="utf-8") as file:
            file.write(auth_data["id_token"])
        space_know_client.set_auth_token(auth_data["id_token"])


api_client = SpaceKnowClient()
set_auth_token_to_api_client(api_client)

# === User info
# user_info = api_client.user_api.get_user_info()
# utils.pretty_print_json(user_info)

# === Remaining credit
# credit = api_client.credits_api.get_remaining_credit()
# print(credit)

# === Search imagery
# geojson_location = utils.load_geojson_data("parking_2")
# search_imagery_data = utils.load_analysis_settings("search_imagery")
# search_imagery_data["extent"] = geojson_location
# pipeline_data = api_client.imagery_api.search_initiate(search_imagery_data)

# === Retrieve imagery
# pipeline_data = {"nextTry": 5, "pipelineId": "Aum2faFykPhIUuYmwY9Q", "status": "NEW"}
# # pipeline_status = api_client.tasking_api.get_status(pipeline_data["pipelineId"])
# imagery_found = api_client.imagery_api.search_retrieve(pipeline_data["pipelineId"])
# utils.pretty_print_json(imagery_found)


# === Run kraken - analysis "cars"
# # Scene ID1:
# GuoBFqtuBllGqZWHb395VXytBgtnXKV7K48kYM8ag5FDq0KfkK_Qo0P-h36IUplIi_LkvUfrPLIxkYYr
# # Scene ID2:
# GuoBFqtuBllGqZWHb395VXytBgtnXKV7LKqbmUuFp3UGXHllmbTepA-ESGr0a96To3V19doB7iL6Q9Mj
# analysis_data = {
# "scene_ids": [
# "GuoBFqtuBllGqZWHb395VXytBgtnXKV7K48kYM8ag5FDq0KfkK_Qo0P-h36IUplIi_LkvUfrPLIxkYYr"
# ],
# "geojson": utils.load_geojson_data("parking_2")
# }
# # allocated_data = api_client.credits_api.allocate_geojson(**analysis_data)
# # allocated_data = api_client.credits_api.check_allocated_area(**analysis_data)
# pipeline_data = api_client.kraken_api.release_initiate(
#     "cars",
#     **analysis_data
# )
# utils.pretty_print_json(pipeline_data)


# === check kraken status - "cars"
# pipeline_data = {"nextTry": 5, "pipelineId": "kpmfCJzfvfDbZhYm1ILQ", "status": "NEW"}
# pipeline_status = api_client.tasking_api.get_status(pipeline_data["pipelineId"])
# utils.pretty_print_json(pipeline_status)


# === retrieve kraken result - detections of "cars" in geojson
# pipeline_data = {"nextTry": 5, "pipelineId": "kpmfCJzfvfDbZhYm1ILQ", "status": "NEW"}
# data = api_client.kraken_api.release_retrieve(pipeline_data["pipelineId"])
# utils.pretty_print_json(data)
#
# for tile in data["tiles"]:
#     detection_tile_data = api_client.kraken_api.get_tile_data(
#         data["mapId"], tile[0], tile[1], tile[2], "detections.geojson"
#     )
#     utils.save_detection_tile_data(detection_tile_data, tile[0], tile[1], tile[2])


# === Run kraken - analysis "imagery"
# # Scene ID1:
# GuoBFqtuBllGqZWHb395VXytBgtnXKV7K48kYM8ag5FDq0KfkK_Qo0P-h36IUplIi_LkvUfrPLIxkYYr
# # Scene ID2:
# GuoBFqtuBllGqZWHb395VXytBgtnXKV7LKqbmUuFp3UGXHllmbTepA-ESGr0a96To3V19doB7iL6Q9Mj
# analysis_data = {
# "scene_ids": [
# "GuoBFqtuBllGqZWHb395VXytBgtnXKV7K48kYM8ag5FDq0KfkK_Qo0P-h36IUplIi_LkvUfrPLIxkYYr"
# ],
# "geojson": utils.load_geojson_data("parking_2")
# }
# # allocated_data = api_client.credits_api.allocate_geojson(**analysis_data)
# # allocated_data = api_client.credits_api.check_allocated_area(**analysis_data)
# pipeline_data = api_client.kraken_api.release_initiate(
#     "imagery",
#     **analysis_data
# )
# utils.pretty_print_json(pipeline_data)


# === check kraken status - "imagery"
# pipeline_data = {"nextTry": 5, "pipelineId": "qhTFqux0Vx4eu9Ym1fzg", "status": "NEW"}
# pipeline_status = api_client.tasking_api.get_status(pipeline_data["pipelineId"])
# utils.pretty_print_json(pipeline_status)


# === retrieve kraken result - detections of "imagery" in geojson
# pipeline_data = {"nextTry": 5, "pipelineId": "qhTFqux0Vx4eu9Ym1fzg", "status": "NEW"}
# data = api_client.kraken_api.release_retrieve(pipeline_data["pipelineId"])
# utils.pretty_print_json(data)
#
# for tile in data["tiles"]:
#     imagery_tile_data = api_client.kraken_api.get_tile_data(
#         data["mapId"], tile[0], tile[1], tile[2], "truecolor.png"
#     )
#     utils.save_imagery_tile_data(imagery_tile_data, tile[0], tile[1], tile[2])
