from aifs import search
import os

def test_search_this():
    os.environ['AIFS_MINIMAL_PYTHON_INDEXING'] = 'false'
    current_dir_path = os.path.dirname(os.path.realpath(__file__))
    query = "test search"
    results = search(query, path=current_dir_path)
    print(results)
    assert results

def test_search_desktop():
    os.environ['AIFS_MINIMAL_PYTHON_INDEXING'] = 'false'
    desktop_path = os.path.expanduser("~/Desktop")
    query = "forest gump"
    results = search(query, path=desktop_path)
    print(results)
    assert results
