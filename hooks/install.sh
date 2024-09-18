# install script for git hooks

# Pre commit hook
# Description: Run the rye lint and rye fmt --check commands before commiting
# to ensure that the code is properly formatted and linted.
# If the commands fail, the commit will be aborted.

echo "Installing pre-commit hook..."
cp hooks/pre-commit .git/hooks/pre-commit
chmod +x .git/hooks/pre-commit
echo "Done"
