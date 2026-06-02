import json

from db import Job, JobLoc


all_tags = {
    "atlanta": ["r-us-atlanta", "r-us-georgia", "c-us"],
    "bangalore": ["r-in-bengaluru", "c-in"],
    "bengaluru": ["r-in-bengaluru", "c-in"],
    "bogotá, colombia": ["r-co-bogota", "c-co"],
    "boston": ["r-us-boston", "c-us"],
    "buenos aires": ["r-ar-buenos-aires", "c-ar"],
    "calgary": ["r-ca-calgary", "c-ca"],
    "chicago": ["r-us-chicago", "c-us"],
    "ciudad de méxico, mexico": ["r-mx-cdmx", "c-mx"],
    "connecticut": ["r-us-connecticut", "c-us"],
    "delaware": ["r-us-delaware", "c-us"],
    "delhi": ["r-in-delhi", "c-in"],
    "detroit": ["r-us-detroit", "c-us"],
    "el segundo, ca": ["r-us-el-segundo", "c-us"],
    "florida": ["r-us-florida", "c-us"],
    "frankfurt": ["r-de-frankfurt", "c-de"],
    "fredericton": ["r-ca-fredericton", "r-ca-new-brunswick", "c-ca"],
    "georgia": ["r-us-georgia", "c-us"],
    "halifax, nova scotia": ["r-ca-halifax", "r-ca-nova-scotia", "c-ca"],
    "london": ["r-gb-london", "c-gb"],
    "maine": ["r-us-maine", "c-us"],
    "maryland": ["r-us-maryland", "c-us"],
    "massachusetts": ["r-us-massachusetts", "c-us"],
    "miami": ["r-us-miami", "r-us-florida", "c-us"],
    "milpitas, california": ["r-us-milpitas", "c-us"],
    "minneapolis": ["r-us-minneapolis", "r-us-minnesota", "c-us"],
    "munich": ["r-de-munich", "c-de"],
    "new-hampshire": ["r-us-new-hampshire", "c-us"],
    "new jersey": ["r-us-new-jersey", "c-us"],
    "new york": ["r-us-new-york", "c-us"],
    "new york city metro": ["r-us-new-york", "c-us"],
    "north carolina": ["r-us-north-carolina", "c-us"],
    "ohio": ["r-us-ohio", "c-us"],
    "ottawa": ["r-ca-ottawa", "r-ca-ontario", "c-ca"],
    "pennsylvania": ["r-us-pennsylvania", "c-us"],
    "quebec city": ["r-ca-quebec", "c-ca"],
    "quebec city": ["r-ca-quebec-city", "r-ca-quebec", "c-ca"],
    "remote- eastern canada": ["remote-ca", "c-ca"],
    "remote germany": ["remote-de", "c-de"],
    "remote uk": ["remote-gb", "c-gb"],
    "remote us": ["remote-us", "c-us"],
    "rhode-island": ["r-us-rhode-island", "c-us"],
    "singapore": ["r-sg-singapore", "c-sg"],
    "stuttgart": ["r-de-stuttgart", "c-de"],
    "south carolina": ["r-us-south-carolina", "c-us"],
    "texas": ["r-us-texas", "c-us"],
    "vancouver": ["r-ca-vancouver", "c-ca"],
    "vermont": ["r-us-vermonet", "c-us"],
    "virginia": ["r-us-virginia", "c-us"],
    "washington d. c.": ["r-us-washington-dc", "c-us"],
}


def get_location_tags(loc_json, src):
    loc = json.loads(job.loc_json)
    if type(loc) is dict:
        loc = [loc]
        
    tags = set()
        
    for obj in loc:
        addr = obj['address']
        locality = addr.get('addressLocality')
        region = addr.get('addressRegion')
        country = addr.get('addressCountry')
        if src == "lever":
            if locality:
                for tag in all_tags.get(locality.lower()) or []:
                    tags.add(tag)
    
    return list(tags)


if __name__ == "__main__":
    import sys
    
    src = sys.argv[1]
    for job in Job.select(src=src):
        loc_tags = get_location_tags(job.loc_json, src)
        for loc_tag in loc_tags:
            JobLoc.add_tag(job.id, loc_tag)