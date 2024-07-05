import json

def code_to_code(code):
    return {
        'CON': 'con',
        'LAB': 'lab',
        'LD': 'lib',
        'GRN': 'grn',
        'SNP': 'snp',
        'PC': 'pc',
        'REF': 'ref',
        'OTH': 'oth',
    }[code]

def parse(path):
    json_paths = list(path.glob('*.json'))
    assert len(json_paths) == 1

    with open(json_paths[0]) as f:
        data = json.load(f)
        return [parse_one(seat) for seat in data['locations']]

def parse_one(r):
    return {
        'code': r['id'],
        'name': r['name'],
    } | {code_to_code(party['party']['code']): party['probability'] for party in r['parties']}