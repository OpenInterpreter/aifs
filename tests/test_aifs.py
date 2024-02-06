from aifs import AIFileSystem
from aifs.indexables import File

aifs_instance = AIFileSystem()

def test_index_file():
    file = File(__file__)
    assert aifs_instance.index(file) is None

def test_index_file():
    directory = File(__file__).directory & '..' 
    assert aifs_instance.index(directory) is None

def test_is_indexed():
    file = File(__file__)
    assert aifs_instance.is_indexed(file) is True

def test_search():
    directory = File(__file__).directory
    assert aifs_instance.search(
        query="Test If file is indexed.", directory=directory
    )