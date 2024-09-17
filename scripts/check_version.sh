#!/bin/bash
# Script to that all occurences of the version number are the same
# Take the one in pyproject.toml as the reference

# Get the version number from pyproject.toml
version=$(grep "version =" pyproject.toml | cut -d '"' -f 2)

# Check that the version number is the same in all files
grep -q $version src/bibmancli/version.py || echo "Version number is not the same in src/bibmancli/version.py"
grep -q $version CHANGELOG.md || echo "Version number is not the same in CHANGELOG.md"
grep -q $version docs/changelog.md || echo "Version number is not the same in docs/changelog.md"