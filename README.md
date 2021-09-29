# Conda TUI using Textual

# Resources

* [Textual Repo](https://github.com/willmcgugan/textual)
* [Rich Repo](https://github.com/willmcgugan/rich)
* [Rich Docs](https://rich.readthedocs.io/en/latest)
* [ASCII Art Generator](https://www.text-image.com/convert/ascii.html)

# Installing dependencies and running the app

```
conda env create -n conda-tui
conda activate conda-tui
python app.py
```

# Code quality

I've included some simple config for code formatting using [`pre-commit`](https://pre-commit.com/).

* Formatting with [`black`](https://black.readthedocs.io)
* Linting with [`flake8`](https://flake8.pycqa.org)
* Type checking with [`mypy`](https://mypy.readthedocs.io)
