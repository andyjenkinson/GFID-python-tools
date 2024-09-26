import sys
import argparse
import yaml
import json
import geojson

from field_id.api_client import APIClient, APIConfiguration

def main(argv):

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-i", "--inputfile", required=True, help="Boundaries to be registered: a GeoJSON FeatureCollection, Feature, Polygon or MultiPolygon")
    #argParser.add_argument("-o", "--outputfile", required=False, help="Output path; defaults to STDOUT")
    argParser.add_argument("-c", "--configfile", required=True, help="Path to config YAML file containing credentials")
    argParser.add_argument("-s", "--source", required=False, help="Name of the source to use when registering boundaries. If not specified as an argument, the source MUST be specified as a `varda:source_name` property within each GeoJSON Feature")
    argParser.add_argument("-p", "--permissions", required=False, help="Comma-separated list of permissions, e.g. `org_1234:view,all:discover`. Overrides any permissions specified with the `varda:permissions` property of each GeoJSON Feature")
    argParser.add_argument("-n", "--dry-run", action="store_true", help="Simulate the registration, performing validity checks without persisting the data in the registry")

    args = argParser.parse_args()
    print("args=%s" % args)

    input_fn = args.inputfile
    #output_fn = args.outputfile
    config_fn = args.configfile

    conf = read_yaml(config_fn)
    input_json = read_geojson(input_fn)
   
    api_config = APIConfiguration.from_dict(conf)
    api_config.client_id = conf['client_id']
    api_config.client_secret = conf['client_secret']
    if 'token_url' in conf:
        api_config.token_url = conf['token_url']

    if input_json.type == 'FeatureCollection':
        input_json = input_json.features # array of features
        for f in input_json:
            _set_source(f, args.source)
            _set_permissions(f, args.permissions)
    elif input_json.type in ['Polygon', 'MultiPolygon']:
        input_json = geojson.Feature(geometry=input_json)
        _set_source(input_json, args.source)
        _set_permissions(input_json, args.permissions)
    elif input_json.type == 'Feature':
        _set_source(input_json, args.source)
        _set_permissions(input_json, args.permissions)

    api_client = APIClient(config=api_config)
    response = api_client.register_boundaries(payload=input_json, dry_run=args.dry_run)
    print("--- Response ---")
    if (response.status_code == 204):
        print("Success - empty response")
    else:
        results = response.json()
        print(json.dumps(results, indent=2))
    print("---")

def _set_source(payload, source_name):
    if source_name:
        payload.properties['varda:source_name'] = source_name
    elif 'varda:source_name' not in payload.properties or not payload.properties['varda:source_name']:
        raise ValueError("Source name is mandatory but was not specified in either input file or --source parameter")


def _set_permissions(payload, permissions):
    if permissions:
        p_arr = [x.strip() for x in permissions.split(',')]
        p_map = dict(x.split(':') for x in p_arr)
        print(p_map)
        payload.properties['varda:permissions'] = p_map
    
    if 'varda:permissions' in payload.properties and payload.properties['varda:permissions']:
        for tenant in payload.properties['varda:permissions']:
            print("Checking permissions for "+tenant)
            perm = payload.properties['varda:permissions'][tenant]
            if (not perm in ['discover', 'view', 'manage']):
                raise ValueError("Permission type "+perm+" should be one of discover, view or manage")
        

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

def read_geojson(file_path):
    with open(file_path, "r") as f:
        return geojson.load(f)

if __name__ == "__main__":
   main(sys.argv[1:])