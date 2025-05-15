#!/bin/bash
cd /app/

# Make a temp init.py that only has the content below
cp README.md fizgrid/__init__.py
sed -i '1s/^/\"\"\"\n/' fizgrid/__init__.py
echo "\"\"\"" >> fizgrid/__init__.py
# echo "" >> fizgrid/__init__.py


# Specify versions for documentation purposes
VERSION="1.4.0"
OLD_DOC_VERSIONS="1.3.0 1.2.0 1.1.1 1.0.0"
export version_options="$VERSION $OLD_DOC_VERSIONS"

# generate the docs for a version function:
function generate_docs() {
    INPUT_VERSION=$1
    if [ $INPUT_VERSION != "./" ]; then
        if [ $INPUT_VERSION != $VERSION ]; then
            pip install "./dist/fizgrid-$INPUT_VERSION.tar.gz"
        fi
    fi
    pdoc -o ./docs/$INPUT_VERSION -t ./doc_template fizgrid
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
