# GenealogyBook
These python scripts create a LaTeX book from a Gramps SQLite database.

Gramps is Genealogical Research Software; for more information, please refer to the [Gramps Project website](https://gramps-project.org/).

## Folder structure
The project consists of three folders:

* `.\book`: This is the location where the `tex`-files will be created.
* `.\db`: This is the location where the Gramps SQLite database must be copied to (`sqlite.db` and `meta_data.db`).
* `.\source`: The folder with the python code.

## Usage
### Start programme
To start, open a terminal window, `cd` to the project folder `...\GenealogyBook\source`.
From there, execute `python hkBook.py`.

### Book
The python scripts will create a LaTeX book, for which the file name of the main document can be set in `hkGenealogyBook.py`, and is by deafult set to `MyBook.tex`.

Additionally, the document title and the author can be set in `hkGenealogyBook.py`.

The book starts with a chapter describing the *Ahnentafel* (familytree), for which the pedigree of the subject person is described, using the binary (atree) numbering method (See [Wikipedia](https://en.wikipedia.org/wiki/Genealogical_numbering_systems)).

Next, each generation of the *Ahnentafel* is described in a book *Part*.

Each person in a generation of the *Ahnentafel* is then described in a *Chapter*. The chapter is written to a separate file and will be `included` in the main document. The name of the chapter files is set to the Gramps ID of that person (e.g. `I0001.tex`).

### Fields
| Variable | Comment | Default value |
| :-- | :-- | :-- |
| vBookAuthor | Name of the author | \<Author\> |
| vBookTitle | Title of the LaTeX book | \<Title\> |
| vBookFilename | Filename of the main LaTeX document | MyBook |
| vStartPersonId | Subject of the family tree | I0000 |

### Tags
In Gramps, tag photo's and documents as follows:

* Pictures tagged with `Portrait`will be used as portrait picture in the section *Life Sketch*.
* Pictures tagged with `Photo` *and* `Publishable` will be included in section *Photos*.
* Scans tagged with `Document` *and* `Publishable`  will be included in section *Documents*.

### Language
The option for the language is set in the file `hkLanguage.py`; the translation strings are described in the *dictionary of dictionaries* named `gStrings`.
