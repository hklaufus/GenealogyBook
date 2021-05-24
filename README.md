# GeneologyBook
Creates a LaTeX book from a Gramps SQLite database.

Gramps is Genealogical Research Software; for more information, please refer to the [Gramps Project website](https://gramps-project.org/).

## Folder structure
The project consists of three folders:
* book: This is the location where the `tex`-files will be created
* db: This is the location where the Gramps SQLite database must be copied to (`sqlite.db` and `meta_data.db`)
* source: The folder with the python code

## Usage
`cd` to your project folder `GenealogyBook\source` and start python3 with `python`.
Next `import hkGeneologyBook.py` and start with `hkGeneologyBook.Main()`
