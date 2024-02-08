from aifs import search
import os

def test_search_index():
    files_path = os.getcwd() + "/testfuncs"
    query = "Lift those weights"
    results = search(query, path=files_path, python_docstrings_only=True)
    print(results)
    assert results

test_search_index();