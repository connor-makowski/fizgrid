#!/bin/bash
cd /app/

# Make a temp init.py that only has the content below the __README_CONTENT_IS_COPIED_ABOVE__ line
cp README.md type_enforced/__init__.py
sed -i '1s/^/\"\"\"\n/' type_enforced/__init__.py
echo "\"\"\"" >> type_enforced/__init__.py
echo "from .core import Grid" >> type_enforced/__init__.py


# Specify versions for documentation purposes
VERSION="0.0.1"
OLD_DOC_VERSIONS="0.0.1"
export version_options="$VERSION $OLD_DOC_VERSIONS"

# generate the docs for a version function:
function generate_docs() {
    INPUT_VERSION=$1
    if [ $INPUT_VERSION != "./" ]; then
        if [ $INPUT_VERSION != $VERSION ]; then
            pip install "./dist/type_enforced-$INPUT_VERSION.tar.gz"
        fi
    fi
    pdoc -o ./docs/$INPUT_VERSION -t ./doc_template type_enforced
}

# Generate the docs for the current version
generate_docs ./
generate_docs $VERSION

# Generate the docs for all the old versions
for version in $OLD_DOC_VERSIONS; do
    generate_docs $version
done;

# Reinstall the current package as an egg
pip install -e .
