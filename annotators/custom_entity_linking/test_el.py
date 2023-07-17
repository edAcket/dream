import requests

use_context = True

@pytest.mark.parametrize(
    "request_data", "gold_results",
    [
        {
            "user_id": ["1234"],
            "entity_substr": [["forrest gump"]],
            "entity_tags": [[[("film", 1.0)]]],
            "context": [["who directed forrest gump?"]],
        }
    ],
    ["film/123"]
)
def test_entity_linking(url: str, request_data: list[dict], gold_results: list):
    inserted_data = {
        "user_id": "1234",
        "entity_info": {
            "entity_substr": ["forrest gump"],
            "entity_ids": ["film/123"],
            "tags": ["film"],
        },
    }
    requests.post(f"{url}/add_entities", json=inserted_data)

    count = 0
    for data, gold_result in zip(request_data, gold_results):
        result = requests.post(f"{url}/model", json=data).json()

        entity_ids = []
        for entity_info_list in result:
            for entity_info in entity_info_list:
                entity_ids = entity_info.get("entity_ids")

        if entity_ids == gold_result:
            count += 1
        else:
            print(f"Got {result}, but expected: {gold_result}")

    assert count == len(request_data)