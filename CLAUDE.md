# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

GenealogyBook reads a **Gramps 6.0.3** SQLite database and generates a LaTeX book (via PyLaTeX) describing the ancestors of one start person. There is no test suite, linter config, or dependency manifest.

## Running

All paths in the code and in `config/config.xml` are relative to `source/`, so the working directory **must** be `source/`:

```bash
cd source && python main.py
```

- Input: `db/sqlite.db` (a copy of the Gramps database, opened read-only). Git ignores `db/*.db`.
- Config: `config/config.xml`. Every tag is required (`read_config_xml` indexes `[0]` unconditionally), including `<FiguresPath>`, which the README does not mention. `<Exclude>` and `<Appendix>` are `;`-separated lists.
- Output: `book/<Filename>.tex` plus `book/chapters/Ahnentafel.tex`, `Part_<n>.tex`, and `<GrampsID>.tex` per person.
- Compile the PDF from `book/` with `pdflatex MyBook.tex`. Run it twice so the `\personref`/`\pageref` cross-references resolve.
- Python dependencies (installed system-wide; `.venv` is empty): `pylatex`, `matplotlib`, `cartopy`, `pandas`, `numpy`, `Pillow`.

## Architecture

**Pipeline:** `main.py` opens the DB cursor → `gen_book.Book` reads the config, writes the preamble (packages, custom macros such as `\personref`, TikZ styles) → `ahnentafel_chapter.Ahnentafel` recursively walks father/mother links from the start person, building `__generation_list__` of `(handle, generation_index)`. Siblings get the same generation index as the person. → For each generation, `Book` writes a `Part_<n>` file and a `person_chapter.PersonChapter` per person, then `\include`s them in the main document. Appendices listed in the config are `\include`d from `AppendixPath` but are never generated.

**Data model layer** (`person.py`, `family.py`, `event.py`, `place.py`, `media.py`, `note.py`, `tag.py`, and the `*_ref.py`, `date.py`, `type.py` helpers): each class takes `(handle, cursor)`, runs `SELECT json_data FROM <table> WHERE handle=?`, and decodes Gramps 6's JSON object format into dunder-style attributes (`__gramps_id__`, `__given_names__`, …). Code throughout accesses these attributes directly rather than through getters. Objects are not cached, so the same person/family is re-queried many times. Gramps schema changes (e.g. the 5.x→6.0 move from pickled tuples to JSON) are handled here.

**`gramps_db.py`**: integer constants mirroring Gramps enums (event types, note types, gender, roles, place types, date modifiers). It also defines groupings (`c_vital_events_set`, `c_family_events_set`, `c_education_events_set`, …) that decide which section of a person chapter an event lands in.

**`person_chapter.py`** (largest file): `write_person_chapter()` builds sections in a fixed order: life sketch, vital info, parents graph, partners graph, education, profession, residence timeline, photos, documents, timeline. Several alternatives (`*_table`, residence map) exist but are commented out in that method. Graphs and timelines are emitted as raw TikZ strings.
- Life sketch precedence: `LifeSketchPath/LS_<GrampsID>.tex` if it exists (hand-written, `\input`), then Gramps notes of type Person, then auto-generated prose.
- Media selection depends on Gramps tags (`Portrait`, `Photo`+`Publishable`, `Document`+`Publishable`; notes tagged `Source` are skipped). Only JPEG/PNG are used. Relative media paths are resolved against the `media-path` value in the DB `metadata` table.

**`latex.py`**: PyLaTeX `Section` subclasses for Part/Chapter/…/Subparagraph, a `WrapFigure` environment, and `create_sub_level()`, which returns the next heading level down from the given one.

**`language.py`**: `gStrings` dict of `{key: {'en': ..., 'nl': ...}}`. `translate()` looks up by lowercased key and capitalizes the result if the input started uppercase. Without a language argument it uses the book language, which `Book` sets from `<Language>` via `language.set_language()`. New UI strings must be added to `gStrings` or they render empty with a warning.

**Excluded persons:** IDs in `<Exclude>` are not regenerated, which protects manually edited chapter files; they are still `\include`d in the main document.

## Conventions

- Hungarian-style prefixes: `p_` for parameters, `v_` for local variables, `c_` for constants. Class attributes use `__name__` dunder style.
- Modules import each other by bare name (`import person`), which relies on `source/` being the working directory.
- `support_functions.get_country_*` read `cow.txt` from the cwd, but the file lives in `config/`. This only matters if the disabled residence-map section is re-enabled.
- Untracked `source/countries.py` and `source/bb_countries.py` are standalone utilities for producing country bounding-box data and are not part of the book pipeline.
