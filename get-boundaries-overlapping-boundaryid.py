import sys
import argparse
import yaml
import json
import re

from field_id.api_client import APIClient, APIConfiguration

def main(argv):

    argParser = argparse.ArgumentParser()
    argParser.add_argument("-o", "--outputfile", required=False, help="Output path; defaults to STDOUT")
    argParser.add_argument("-c", "--configfile", required=True, help="Path to config YAML file containing credentials")
    group = argParser.add_mutually_exclusive_group(required=True)
    group.add_argument("-i", "--inputfile", help="Path to a comma or line-separated list of Global BoundaryIDs")
    group.add_argument("-b", "--gbid", help="Comma-separated list of Global BoundaryIDs")

    args = argParser.parse_args()
    print("args=%s" % args)

    input_fn = args.inputfile
    gbid_string = args.gbid
    output_fn = args.outputfile
    config_fn = args.configfile

    conf = read_yaml(config_fn)
    if input_fn:
        gbid_string = open(input_fn, 'r').read().strip()
        gbid_string = re.sub("[\s,]+", ',', gbid_string)

    output_fh = None
    if output_fn:
        output_fh = open(output_fn, 'w')
   
    api_config = APIConfiguration.from_dict(conf)
    api_client = APIClient(config=api_config)

    query_params = {
        'boundary_relationships.boundary_id': gbid_string,
    }
    response = api_client.get_boundaries(args=query_params, limit=50)
    results = response.json()
    print(results)

    boundaries = results['features']

    for result in boundaries:
        
        for ref in result['properties']['boundary_references']:
            # expand to ALL the properties of the reference, not only the Varda-defined ones
            response = api_client.get_boundary_reference(boundary_reference_id=ref['id'])
            ref_feature = response.json()
            for key in ref_feature['properties']:
                ref[key] = ref_feature['properties'][key]

    if (output_fh):
        print("--- Printing response to %s ---" % output_fn)
        print(json.dumps(results, indent=2), file=output_fh)
    else:
        print("--- Response ---")
        print(json.dumps(results, indent=2))
        print("---")

def read_yaml(file_path):
    with open(file_path, "r") as f:
        return yaml.safe_load(f)

def read_json(file_path):
    with open(file_path, "r") as f:
        return json.load(f)

if __name__ == "__main__":
   main(sys.argv[1:])