# Roadmap

- [ ] Add file source to chunk, including page number if relevant.
- [ ] Handle file deletions (I think we can just more robustly detect indexed files vs present files)
- [ ] Add tqdm to each step
- [ ] Allow you to ignore certain files or paths (I think path should just accept a list, and if it's a list of files, those are the only files it will take. Then you can write your own logic for ignoring stuff)
- [ ] Make it work with just one file, like pointing to a single PDF.
- [ ] Put an `_.aifs` in each subdirectory, so indexing a path will index all subpaths
- [ ] Support multimodal — transcribe videos and audio, describing each scene / sound, describe images
