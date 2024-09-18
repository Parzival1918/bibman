#!/bin/bash
# Script to that all occurences of the version number are the same
# Take the one in pyproject.toml as the reference

# Get the version number from pyproject.toml, only use one of the lines
version=$(grep "version" pyproject.toml | head -n 1 | cut -d '"' -f 2)

# Check that the version number is the same in all files
grep -q $version src/bibmancli/version.py || echo "Version number is not the same in src/bibmancli/version.py"
grep -q $version CHANGELOG.md || echo "Version number is not the same in CHANGELOG.md"
grep -q $version docs/changelog.md || echo "Version number is not the same in docs/changelog.md"
grep -q $version flake.nix || echo "Version number is not the same in flake.nix"
# check that pyproject.toml has the same version number in the second appearance
grep $version pyproject.toml | wc -l | grep -q 2 || echo "Version number is not the same in tool.poetry in pyproject.toml"
