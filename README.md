# GenealogyBook
These python scripts create a LaTeX book from a Gramps SQLite database.

Gramps is Genealogical Research Software; for more information, please refer to the [Gramps Project website](https://gramps-project.org/).

## Version
The python scripts are compatible with the Gramps Database for Gramps version 6.0.3

## Folder structure
The project consists of three folders:

* `.\book`: This is the location where the main `tex`-file will be created.
* `.\db`: This is the location where the Gramps SQLite database must be copied to (`sqlite.db` and `meta_data.db`).
* `.\source`: The folder with the python code.
* `.\config`: The folder containing a configuration file `config.xml`.

## Usage
### Start programme
To start, open a terminal window, `cd` to the project folder `...\GenealogyBook\source`.
From there, execute `python main.py`.

### Book
The python scripts will create a LaTeX book, for which the file name of the main document can be set in `cconfig.xml`, and is by default set to `MyBook.tex`.

Additionally, the document title and the author can be set in `config.xml`.

The book starts with a chapter describing the *Ahnentafel* (familytree), for which the pedigree of the subject person is described, using the binary (atree) numbering method (See [Wikipedia](https://en.wikipedia.org/wiki/Genealogical_numbering_systems)).

Next, each generation of the *Ahnentafel* is described in a book *Part*.

Each person in a generation of the *Ahnentafel* is then described in a *Chapter*. The chapter is written to a separate file and will be `included` in the main document. The names of the chapter files are set to the Gramps ID of that person (e.g. `I0001.tex`).

### Tags
In Gramps, tag photo's and documents as follows:

* Pictures tagged with `Portrait`will be used as portrait picture in the section *Life Sketch*.
* Pictures tagged with `Photo` *and* `Publishable` will be included in section *Photos*.
* Scans tagged with `Document` *and* `Publishable`  will be included in section *Documents*.

### Language
The option for the language is set in the file `config.xml`; the translation strings are described in the *dictionary of dictionaries* named `gStrings`.

### Configuration file
The file `config.xml` allows for setting default values:
* `<Author> ... </Author>`: Set name of author
* `<Title> ... </Title>`: Set the title of the book
* `<Filename> ... </Filename>`: Set the file name of the main LaTeX file
* `<StartPersonId> ... </StartPersonId>`: Set the Id of the first person
* `<Language> ... </Language>`: Set the language
* `<BookPath> ... </BookPath>`: Set the path to where the LaTeX file for the _main document_ are to be stored
* `<ChapterPath> ... </ChapterPath>`: Set the path to where the LaTeX files for the _chapters_ are to be stored
* `<AppendixPath> ... </AppendixPath>`: Set the path to where the LaTeX files for the appendices can be found; the files are **not** created by the python routines.
* `<LifeSketchPath> ... </LifeSketchPath>`: Set the path to where the LaTeX files for the life sketches can be found; the files are **not** created by the python routines, and will be used for the first life sketch section for a person chapter.
* `<Exclude> ... </Exclude>`: A list of Person ID's *NOT* to (over-)write a chapter for; the main LaTeX file will however still do an `\include`. This is to prevent overwriting chapter that were manually changed.
* `<Appendix> ... </Appendix>`: A list of file names to be included as an Appendix; `AppendixPath` is the location where these files are to be found.