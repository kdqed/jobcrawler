from collections import Counter
import json

from rapidfuzz import process, fuzz

from db import Job, JobLoc


loc_tag_to_name = {}
loc_name_to_tags = {}
all_tags = set()
autocomp = {}
autocomp_words = []

with open('location_lookup.txt', 'r') as f:
    lines = f.readlines()
    for line in lines:
        chunks = line.strip('\n').strip().split(', ')
        primary_tag = False
        primary_name = False
        if chunks[-1] == '_t':
            primary_tag = True
            chunks = chunks[:-1]
        elif chunks[-1] == '_n':
            primary_name = True
            chunks = chunks[:-1]
        
        tag = chunks[-1]
        if (tag not in loc_tag_to_name) or primary_tag:
            loc_tag_to_name[tag] = chunks[1]
        
        name = chunks[0]
        name_dict = {"tags": set(chunks[2:]), "name": chunks[1]}
        all_tags.update(name_dict['tags'])
        if primary_name:
            name_dict['primary'] = True
        if name not in loc_name_to_tags:
            loc_name_to_tags[name] = []
        loc_name_to_tags[name].append(name_dict)
        
        autocomp[chunks[1].lower()] = {'name': chunks[1], 'tag': chunks[-1]}
    autocomp_words = autocomp.keys()

 
def print_names():
    for key in loc_name_to_tags:
        print(key, loc_name_to_tags[key])
 
                    
def print_tags():
    for key in loc_tag_to_name:
        print(key, loc_tag_to_name[key])
        

def print_unnamed_tags():
    for tag in all_tags:
        if tag not in loc_tag_to_name:
            print(tag)

            
def _autocomplete_sort_key(match, term):
    name, score, idx = match
    prefix_match = name.lower().startswith(term.lower())
    return (not prefix_match, -score)
    
    
def autocomplete(term: str, limit = 3):
    term = term.lower()
    ex = process.extract(term, autocomp_words, scorer=fuzz.partial_ratio, limit=limit)
    ex.sort(key= lambda x: _autocomplete_sort_key(x, term))
    result = []
    for e in ex:
        result.append(autocomp[e[0]])
    return result
    

def get_name_by_tag(tag: str):
    return loc_tag_to_name.get(tag)


def get_location_tags(loc_json: str):
    loc = json.loads(loc_json)
    if type(loc) is dict:
        loc = [loc]
        
    tags = set()
        
    for obj in loc:
        addr = obj['address']
        country = (addr.get('addressCountry') or '').lower().split(",")[::-1]
        region = (addr.get('addressRegion') or '').lower().split(",")[::-1]
        locality = (addr.get('addressLocality') or '').lower().split(",")[::-1]
        
        all_names = country + region + locality
        tags = set()
        
        for chunk in all_names:
            name = chunk.strip()
            tagsets = loc_name_to_tags.get(name, [])
            if len(tagsets) == 0:
                pass
            elif len(tagsets) == 1:
                tags.update(tagsets[0]['tags'])
            else:
                to_use = [t for t in tagsets if t.get('primary')][0]
                for tagset in tagsets:
                    i1 = len(to_use['tags'] & tags)
                    i2 = len(tagset['tags'] & tags)
                    if i2 > i1:
                        to_use = tagset
                tags.update(to_use['tags'])
    
    return list(tags)


def dump_undefined(src: str, cutoff: int = 5):
    names = []
    for job in Job.select(src=src):
        loc = json.loads(job.loc_json)
        if type(loc) is dict:
            loc = [loc]
        
        for obj in loc:
            addr = obj['address']
            names += (addr.get('addressCountry') or '').lower().split(',')[::-1]
            names += (addr.get('addressRegion') or '').lower().split(',')[::-1]
            names += (addr.get('addressLocality') or '').lower().split(',')[::-1]
         
    names = list(filter(lambda x: x, map(lambda x: x.strip(), names)))
    frequencies = Counter(names)
    frequencies = [[f, frequencies[f]] for f in frequencies]
    frequencies.sort(key = lambda x: x[1], reverse=True)
    for f in frequencies:
        if f[1] >= cutoff:
            print(f[0], f[1])

    
def redo_tags(src: str):
    for job in Job.select(src=src):
        loc_tags = get_location_tags(job.loc_json)
        for loc_tag in loc_tags:
            JobLoc.add_tag(job.id, loc_tag)


if __name__ == "__main__":
    import fire
    fire.Fire()