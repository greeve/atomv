#!/usr/bin/env python
# -*- coding: utf-8 -*-

import sys
from optparse import OptionParser
import requests
import json
from collections import Counter

ATOM_URL = "http://atom.lib.byu.edu/{slug}"
ATOM_SEARCH = "/search/json/?q={query}"
ATOM_BROWSE = "/browse/json/"
ATOM_FIELD = "/values/?fields={field}"
ATOM_ADV = "/search/json/?adv={query}"


def _test(verbose=None):
    import doctest
    doctest.testmod(verbose=verbose)


def _profile_main(filename=None):
    import cProfile
    import pstats
    prof = cProfile.Profile()
    ctx = """_main(filename)"""
    prof = prof.runctx(ctx, globals(), locals())
    stats = pstats.Stats(prof)
    stats.sort_stats("time")
    stats.print_stats(10)


def _blurt(s, f):
    pass


def clean(data):
    """
    TODO
    """
    return [0 if x == '' else x for x in data]


def type_counts(response):
    data = response.json()
    field = response.url.split("=")[-1]
    slug = response.url.split("/")[3]
    all_data = []
    for field_type in data[field]:
        # ATOM_ADV = "/search/json/?adv=collection_e%3AAdvertisements"
        query = field + "_e%3A" + field_type
        url = ATOM_URL.format(slug=slug) + ATOM_ADV.format(query=query)

        r = requests.get(url)
        if r.status_code == 200:
            print(field_type)
            all_data.append(item_counts(aggregate_data(r), field_type))
        else:
            print(r.status_code, r.url)
    print(json.dumps(all_data))


def item_counts(data=None, field=None):
    dates = [d['dateoriginal'] for d in data['results']]
    years = [year.split("-")[0] for year in dates]
    date_counter = Counter(years)
    items = [[int(k), v] for k, v in date_counter.most_common() if k != ''] #noqa
    return {"items": items, "name": field, "total": data['total_results']}


def aggregate_data(response):
    data = response.json()

    if data["results"] is None or data is None:
        print("Failed to retrive results for url: ", response.url)
        return -1

    if data['total_pages'] > 1:
        for page in range(2, data['total_pages'] + 1):
            params = {"p": page}
            r = requests.get(response.url, params=params)
            if r.status_code == 200:
                more_data = r.json()
            else:
                more_data = None
            if more_data is None or more_data['results'] is None: #noqa
                print('Failed to retrieve data')
                print(data)
                continue
            data['results'].extend(more_data['results'])

    return data


def barchart(data):
    dates = [d['dateoriginal'] for d in data['results']]
    years = [year.split("-")[0] for year in dates]
    date_counter = Counter(years)
    dataset = [{"date": k, "frequency": v} for k, v in date_counter.most_common() if k != ''] #noqa
    max_year = max(dataset, key=lambda x: x['date'])
    min_year = min(dataset, key=lambda x: x['date'])
    some_years = [x['date'] for x in dataset]
    for x in range(int(min_year['date']), int(max_year['date'])):
        if str(x) not in some_years:
            dataset.append({'date': str(x), 'frequency': 0})
    dataset.sort(key=lambda d: (d['date'], d['frequency']))
    print(json.dumps(dataset))


def _main(params=None):
    if not params:
        return -1

    slug = params.get("slug", "")

    if not slug:
        return -1

    query = params.get("query", None)
    field = params.get("field")

    url = ""
    if field:
        if query is not None:
            url = ATOM_URL.format(slug=slug) + ATOM_FIELD.format(field=query)
    else:
        if query is not None:
            url = ATOM_URL.format(slug=slug) + ATOM_SEARCH.format(query=query)
        else:
            url = ATOM_URL.format(slug=slug) + ATOM_BROWSE

    r = requests.get(url)
    if r.status_code == 200:
        if field:
            type_counts(r)
        else:
            barchart(aggregate_data(r))
    else:
        print(r.status_code, r.url)

    return 0

if __name__ == "__main__":
    usage = "usage: %prog [options] [slug] [query]"
    parser = OptionParser(usage=usage)
    parser.add_option('--profile', '-P',
                      help="Print out profiling stats",
                      action='store_true')
    parser.add_option('--test', '-t',
                      help='Run doctests',
                      action='store_true')
    parser.add_option('--verbose', '-v',
                      help='print debugging output',
                      action='store_true')
    parser.add_option('--field', '-f', help='search all field values',
                      action='store_true')

    (options, args) = parser.parse_args()

    if options.verbose:
        def really_blurt(s, f=()):
            sys.stderr.write(s % f + '\n')
        _blurt = really_blurt # noqa

    # Assign non-flag arguments here.
    params = None
    if args:
        if len(args) == 2:
            params = {"slug": args[0], "query": args[1]}
        else:
            params = {"slug": args[0]}

    if options.field:
        if params:
            params["field"] = options.field
        else:
            params = {"field": options.field}

    if options.profile:
        _profile_main(params)
        exit()

    if options.test:
        _test(verbose=options.verbose)
        exit()

    sys.exit(_main(params))
