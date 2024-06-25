# gfid-python-tools
 Helper scripts and tools for interacting with the Global FieldID API

## Examples

### Fetch open field boundaries 
Get the current boundary for each of a given list of GFIDs. Note will only return a boundary if the GFID is active (i.e. has an active boundary).
```
python3 get-boundaries-by-fieldid.py -f 15YB.2ZH3,15RQ.91NB
                                     -o gfid-boundaries.geojson
                                     -c local/config.yaml
python3 get-boundaries-by-fieldid.py -i gfid-list.txt
                                     -o gfid-boundaries.geojson
                                     -c local/config.yaml
```

### GFID Search
Search for a GFID matching a polygon/feature.
```
python3 search-fields-with-geometry.py -i input-boundary.geojson
                                       -c local/config.yaml
```
