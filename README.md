# gfid-python-tools
 Helper scripts and tools for interacting with the Global FieldID API

## Examples

### Fetch open field boundaries 
Get the current boundary for each of a given list of GFIDs. Note will only return a boundary if the GFID is active (i.e. has an active boundary).
```
python3 get-boundaries-by-fieldid.py -f 15YB.2ZH3,15RQ.91NB
                                     -o local/gfid-boundaries.geojson
                                     -c local/config.yaml
python3 get-boundaries-by-fieldid.py -i examples/data/fieldid-list.txt
                                     -o local/gfid-boundaries.geojson
                                     -c local/config.yaml
```

### GFID Search
Search for a GFID matching a polygon/feature.
```
python3 search-fields-with-geometry.py -i input-boundary.geojson
                                       -c local/config.yaml
```

### Fetch any boundaries by ID
Fetch full details for a list of boundary IDs, including all linked source-system references

Performs a GET /boundaries/{id} for each boundary, and a GET /boundary-references/{id} for each of the references linked to it
```
python3 get-boundary.py -b 8ab8863d-d05c-4c9b-bb05-0d8720a3f97b,af6a0e46-2fed-4ea0-9748-75b2499204bb
                        -o local/boundaries-array.json
                        -c local/config.yaml
python3 get-boundary.py -i examples/data/boundaryid-list.txt
                        -o local/boundaries-array.json
                        -c local/config.yaml
```

### Register boundaries
Register one or more boundaries in the GFID registry. **Requires boundary:create privileges**

Input is:
- a file containing a GeoJSON FeatureCollection, Feature, Polygon or MultiPolygon
- source name (overrides any varda:source_name set in Feature properties)
- permissions (overrides any varda:permissions set in Feature properties)
- config file with credentials
```
python3 register-boundaries.py -i local/my-boundaries.geojson
                               -s "My Source"
                               -p "varda:manage,org_123:manage,org_456:view,org_789:discover"
                               -c local/config.yaml
```
