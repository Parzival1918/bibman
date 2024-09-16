# html

![GIF](../media/html.gif)

Command to **create a simple HTML page to view your library contents and search interactively.**

Check my references created using this command and hosted in GitHub Pages [here](https://parzival1918.github.io/references/).

??? tip "Publishing library using GitHub Actions"
    The GitHub Action I use to publish my library to GitHub Pages is the following:

    ```yaml
    name: deploy-pages

    # Only run this when the master branch changes
    on:
    push:
        branches:
        - main

    # This job installs dependencies, creates the HTML page and deploys it to GitHub Pages
    jobs:
    deploy-mkdocs:
        runs-on: ubuntu-latest
        permissions:
        contents: write  # To push a branch 
        pages: write  # To push to a GitHub Pages site
        id-token: write # To update the deployment status
        steps:
        - uses: actions/checkout@v4

        - name: Set up Python 3.12
        uses: actions/setup-python@v5
        with:
            python-version: 3.12

        # Install bibman
        - name: Install dependencies
        run: |
            python -m pip install bibmancli

        # create .bibman.toml file pointing to the current directory
        - name: Create .bibman.toml
        run: |
            echo "[library]" > .bibman.toml
            echo "location = '.'" >> .bibman.toml

        # Build the book
        - name: Build the page
        run: |
            python -m bibmancli html --yes --location .

        - name: Setup Pages
        uses: actions/configure-pages@v5

        - name: Upload artifact
        uses: actions/upload-pages-artifact@v3
        with:
            # Upload entire repository
            path: '_site'
        - name: Deploy to GitHub Pages
        id: deployment
        uses: actions/deploy-pages@v4
    ```

    So, every time I push to the `main` branch, the GitHub Action will create the HTML page and deploy it to GitHub Pages.

## Usage

```bash
bibman html [OPTIONS]
```

## Options

* `--folder-name` The name of the folder inside the library where the HTML contents will be written. Default is `_site`.
* `--overwrite/--no-overwrite` Overwrite the contents of the folder if it already exists. Default is `--overwrite`.
* `--launch/--no-launch` Launch the HTML page in the default browser after creating it. Default is `--no-launch`.
* `--yes/--no` Skip the confirmation prompt and create the HTML page immediately. Default is `--no`. Usefull for CI/CD pipelines.
* `--location` The location of the [`.bibman.toml` file](../config-format/index.md). If not provided, the program will search for it in the current directory and its parents.