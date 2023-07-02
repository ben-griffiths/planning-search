#!/bin/bash

parent_folder="lambda"
child_folder="lambda/temp"

mkdir -p lambda/temp
find "$parent_folder" -type f -name "*.py" -exec cp {} "$child_folder" \;
pip install -r "$parent_folder/requirements.txt" --target "$child_folder"

cd "$child_folder" && zip -r "../../lambda.zip" . && cd ../..

rm -rf "$child_folder"
