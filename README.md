# x4-galaxy-generator
Converts JSON to XML that is read by X4 Foundations.

Generates the following XML files:
* index/
    * macros.xml
* libraries/
    * mapdefaults.xml
* maps/
    * {prefix}_map/
        * clusters.xml
        * galaxy.xml
        * sectors.xml
        * zones.xml

The current implementation generates simple clusters with one to many sectors. Inter-cluster
connections are generated, but inter-sector connections are not.

## Usage
Simply run with a *.json passed in as the argument:

    python -m generator {map}.json
