"""AIFS CLI Integration."""

import json
from pathlib import Path
from typing import Annotated, Literal

from cyclopts import App, Parameter

app = App(
    name='aifs', 
    help="Local semantic search. Stupidly simple.",
    version_flags=['version'], 
    help_flags=['help', '-h'])

app['help'].group = app.group_parameters
app['version'].group = app.group_parameters

def print_json(__input: list | dict):
    print(json.dumps(__input, indent=4))

@app.command(name='embedder')
def embedder(
    *,
    select: Annotated[bool, Parameter(negative="", show_default=False)] = False
):
    """
    Default embedder.

    @param select: Select from available embedders.
    """
    from . import settings
    if select is False:
        print_json(settings.DEFAULT_EMBEDDER)
        return
    
    from minifzf import Selector #https://github.com/synacktraa/minifzf
    from .embedder import Embedder
    selector = Selector.from_mappings(Embedder.available_models)
    selected = selector.select()
    if not selected:
        return

    settings.DEFAULT_EMBEDDER_FILE.write_text(json.dumps(selected))

@app.command(name='search')
def search(
    dir: Path = Path.cwd(), 
    /, 
    *, 
    query: Annotated[str, Parameter(name=('-q', '--query'))],
    max_results: Annotated[int, Parameter(name=('-k', '--max-results'))] = 5,
    threshold: Annotated[float, Parameter(name=('-t', '--threshold'))] = None,
    _return: Annotated[Literal['path', 'context'], Parameter(name=('-r', '--return'))] = None,
):
    """
    Perform semantic search in a directory.

    @param dir: Start search directory path.
    @param query: Search query string.
    @param max_results: Maximum result count.
    @param threshold: Minimum filtering threshold value.
    @param _return: Component to return.
    """

    if not dir.exists():
        print(f"{str(dir)!r} doesn't exists on the system.")
        return
    if not dir.is_dir():
        print(f"{str(dir)!r} is not a directory.")
        return
    
    from . import Directory, AIFileSystem
    mapping = AIFileSystem().search(query, Directory(dir), max_results, threshold)
    if mapping:
        if len(mapping) == 1:
            if _return == 'path':
                print(list(mapping)[0])
            elif _return == 'context':
                print_json(list(mapping.values())[0])
            else:
                print_json(mapping)
            return
        
        from minifzf import Selector
        selector = Selector(
            rows=[(filepath,) for filepath in mapping], headers=[query])
        selected = selector.select(disable_print=True)
        if selected:
            if _return == 'path':
                print(selected)
            elif _return == 'context':
                print_json(mapping[selected])
            else:
                print_json({selected: mapping[selected]})


@app.command(name='index')
def index(path: Path, /):
    """
    Index a file or directory.
    
    @param path: Path to file or directory.
    """
    if not path.exists():
        print(f"{str(path)!r} doesn't exists on the system.")
        return
    from . import File, Directory, AIFileSystem
    if path.is_file():
        target = File(path)
    elif path.is_dir():
        target = Directory(path)
    else:
        print(f"Only file and directory can be indexed.")
        return
    
    AIFileSystem().index(target)

if __name__ == "__main__":
    app()