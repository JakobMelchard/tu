# Licence

This repository holds two kinds of material under two licences.

## Prose: CC BY-SA 4.0

Notes, source registers, TISS transcriptions, READMEs and all other prose under
`content/` and `templates/` are licensed under the
[Creative Commons Attribution-ShareAlike 4.0 International licence](https://creativecommons.org/licenses/by-sa/4.0/).
You may share and adapt them, also commercially, if you give credit to the
TU Wien study wiki contributors, link the licence, and release your changes
under the same licence.

## Code: MIT

Code under `content/courses/*/src/`, `templates/course/src/` and `scripts/` is
licensed under the MIT licence:

```
Copyright (c) 2026 TU Wien study wiki contributors

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
```

## Exceptions

The files below are not covered by CC BY-SA 4.0 or MIT. They keep their own
licence, stated in the course's `refs/SOURCES.md` and, where required, in a
licence file next to them. Paths are relative to `content/courses/`.

Third-party files, vendored unmodified:

| path | licence |
|---|---|
| `*/refs/rfc/` (`advanced-cryptography`, `introduction-to-cryptography`, `introduction-to-networking`) | IETF RFCs (IETF Trust or Internet Society copyright), redistributed unmodified as the RFCs permit |
| `*/refs/nist/` (`advanced-cryptography`, `introduction-to-cryptography`) | NIST publications, works of the US government |
| `introduction-to-cryptography/refs/vectors/` | Wycheproof test vectors, Apache-2.0 (`LICENSE-Apache-2.0.txt`) |
| `numerical-simulation-and-scientific-computing-i/refs/vendor/openmp-api-specification-5.2.pdf` | OpenMP ARB copyright, copied unmodified under the permission notice on its title page |
| `numerical-simulation-and-scientific-computing-i/refs/vendor/hestenes-stiefel-1952-conjugate-gradients.pdf` | work of the US government (J. Res. NBS) |
| `numerical-simulation-and-scientific-computing-i/refs/vendor/vtkCellType.h` | BSD-3-Clause, Ken Martin, Will Schroeder, Bill Lorensen (`LICENSE-VTK`) |
| `database-systems/refs/vendor/sqlite/`, `advanced-database-systems/refs/vendor/sqlite-lang_with.html` | SQLite documentation, public domain |
| `advanced-database-systems/refs/vendor/pg18-*.html` | PostgreSQL documentation, PostgreSQL Licence (`LICENSE-PostgreSQL.txt`) |
| `computational-science-on-many-core-architectures/refs/vendor/rupp-cpu-gpu-mic-comparison/` | Karl Rupp, CC BY 4.0 (`LICENSE.txt`) |
| `asc-school-i-hpc/refs/vendor/asc-*.md` | ASC Research Center, TU Wien (VSC training slide sources), CC BY-SA 4.0 (`LICENSE-CC-BY-SA-4.0.txt`) |
| `asc-school-i-hpc/refs/vendor/mpi-5.0-standard.pdf` | University of Tennessee copyright, copied unmodified under the MPI Forum permission notice on page ii |

Material adapted from MIT OpenCourseWare, licensed **CC BY-NC-SA 4.0**
(non-commercial), prose and code alike:

| path | adapted from |
|---|---|
| `introduction-to-networking/src/exercises/mit-6.02-2012/` | MIT 6.02 *Introduction to EECS II*, Fall 2012, MIT OpenCourseWare |
| `introduction-to-networking/notes/12-substitute-practice-set.md` | the same, plus CC BY-SA 3.0 material from UCLouvain CNP3 |
| `quantum-computing-complexity-theory-and-algorithmics/src/exercises/mit-18.404j-2020/` | MIT 18.404J *Theory of Computation*, Michael Sipser, Fall 2020, MIT OpenCourseWare |
| `quantum-computing-complexity-theory-and-algorithmics/src/exercises/mit-6.046j-2015/` | MIT 6.046J *Design and Analysis of Algorithms*, Erik Demaine, Srini Devadas, Nancy Lynch, Spring 2015, MIT OpenCourseWare |
| `quantum-computing-complexity-theory-and-algorithmics/notes/01-practice-set-substitute-sources.md` | the two MIT courses above |

MIT OpenCourseWare material is used under
<https://ocw.mit.edu/terms/> and
<https://creativecommons.org/licenses/by-nc-sa/4.0/>. Each of these files and
folders names its source at the top.

Material adapted from *Computer Networking: Principles, Protocols and Practice*
(Olivier Bonaventure, UCLouvain), CC BY-SA 3.0, is released under CC BY-SA 4.0,
code included: `introduction-to-networking/src/exercises/uclouvain-cnp3-2019/`.

## Quartz

The site generator under `quartz/` and its configuration are
[Quartz](https://github.com/jackyzha0/quartz), MIT licensed; see
[LICENSE.txt](LICENSE.txt).
