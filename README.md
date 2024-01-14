# rezbuild_utils

Python library providing utilities to build rez packages.

```python
import rezbuild_utils
help(rezbuild_utils)
```
# prerequisites

- python 3
- this is a [rez](https://github.com/AcademySoftwareFoundation/rez) package made to
work in the context of a rez infrastructure.
- documentation need `git` to be deployed


# documentation

https://knotsanimation.github.io/rezbuild_utils/

**local build**

```shell
cd .
# ensure package is built first (necessary for autodoc)
rez-build -i
rez-env sphinx furo rezbuild_utils
python ./doc/build-doc.py -a
```

The documentation can then be found in `./doc/build/html/index.html`