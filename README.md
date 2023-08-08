# A conda Text User Interface (TUI) built with Textual

![logo](etc/logos/conda-tui-color-background.png)

> This is a project that was originally developed during [@anaconda](https://github.com/anaconda) hackdays.
> It is currently in its infancy, and we welcome any contributions or suggestions from the community!
>
> Due to its stage of development, it is recommended to try it out and provide feedback.

`conda-tui` is a snake-chef that follows and creates recipes to deliver delicious homemade packages.

`conda-tui` is also an experimental Text User Interface (TUI) for conda built with [Textual](https://github.com/Textualize/textual).
It aims to provide a clean and easy interface centered around common interactive use cases, wrapped around the conda CLI.

<img width="1194" alt="image" src="https://github.com/anaconda-hackdays/conda-tui/assets/11037737/3c4d273c-bb0e-4c0b-bf9b-34f816478760">

# Installation

1. Ensure you have `conda` or `miniconda` installed
2. Install the package into a test environment:
   * `conda create -n tui -c conda-forge -c mattkram/label/dev conda-tui conda`
   * `conda activate tui`
3. Run it! `conda tui`

# Features

> This is very likely to change. Have an idea? Create an issue!

* Display a list of all `conda` environments (`conda env list`)
* Navigate to any environment to view all packages installed (`conda list`)
* Display packages that can be updated (`conda update --all --dry-run`)
  
  <img width="858" alt="image" src="https://github.com/anaconda-hackdays/conda-tui/assets/11037737/d3c133c8-c074-4a24-a5f1-bbda271f028c">
  <img width="1727" alt="image" src="https://github.com/anaconda-hackdays/conda-tui/assets/11037737/1314947f-de3a-461e-982a-6e01b49fe456">

# Dev setup

1. Ensure you have `conda` or `miniconda` installed
1. Setup a new conda dev environment: `make setup`
1. Activate the environment: `conda activate ./env`
1. Install `pre-commit`: `pre-commit install`
1. Run the application: `make run`
1. Run the type checks: `make type-check`
1. Run the tests: `make test`

# Resources

* [Textual Repo](https://github.com/willmcgugan/textual)
* [Rich Repo](https://github.com/willmcgugan/rich)
* [Rich Docs](https://rich.readthedocs.io/en/latest)
* [ASCII Art Generator](https://www.text-image.com/convert/ascii.html)

# Icon sources

The logo was constructed from free icons, which require attribution:

* [Snake] made by [Freepik]
* [Chef hat] made by [Those Icons]

[Snake]: https://www.flaticon.com/free-icon/snake_194210?term=snake&related_id=194210
[Freepik]: https://www.flaticon.com/authors/freepik
[Chef hat]: https://www.flaticon.com/free-icon/chef_481486?term=chef%20hat&related_id=481486
[Those Icons]: https://www.flaticon.com/authors/those-icons
