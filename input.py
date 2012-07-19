
def store(measurements):
    import json
    with open(’measurements.json’, ’w’) as f:
        f.write(json.dumps(measurements))

