# Roadmap

- [x] Add file source to chunk metadata, including page number if relevant, and ensure this is displayed when running `search`.
- [x] Handle file deletions (I think we can just more robustly detect indexed files vs present files)
- [x] Add tqdm to each step (Uses `rich.progress`)
- [x] Allow you to ignore certain files or paths (I think path should just accept a list, and if it's a list of files, those are the only files it will take. Then you can write your own logic for ignoring stuff)
- [x] Make it work with just one file, like pointing to a single PDF.
- [x] Put an `_.aifs` in each subdirectory, so indexing a path will index all subpaths (Well, everything is now maintained in collections in `aifs` cache directory.)
- [ ] Support multimodal — transcribe videos and audio, describing each scene / sound, describe images
