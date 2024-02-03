from aifs import search
import os

def test_search_index():
    os.environ['AIFS_MINIMAL_PYTHON_INDEXING'] = 'true'
    files_path = os.getcwd() + "/testfuncs"
    query = "Lift those weights"
    results = search(query, path=files_path)
    print(results)
    assert results

test_search_index();