# Sample Documents

Place any ``.txt`` or ``.md`` files you want the assistant to be able to answer
questions about in this directory. The ``scripts/load_documents.py`` script will
read all files recursively, split them into manageable chunks and index them in
the persistent ChromaDB store.
