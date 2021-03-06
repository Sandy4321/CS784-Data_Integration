# coding: utf8 
#!/usr/bin/python

import requests
from lxml import html
import json, time, re
import shutil, sys, os
import random

cities = ['madison', 'milwaukee']
base_urls = ["http://%s.craigslist.org" % s for s in cities]
IMGDIR = 'car_images/'
HTMLDIR = 'craiglist/html_craiglist/'

cars = []
def get_all_links(city='madison', limmit_hop = 100, fromFile=None):
    base_url = "http://%s.craiglist.org" % city
    url = "%s/search/cta" % base_url
    if fromFile:
        with open(fromFile) as f:
            links = [x.strip() for x in f.readlines()]
            return links
    links = []
    last_len = 0
    for i in xrange(limmit_hop):
        full_url = url+"?s=%d&" % (i*100)
        first_page = requests.get(full_url)
        tree = html.fromstring(first_page.text)
        links.extend("%s/%s" % (base_url, l)
                     for l in tree.xpath("//p[@class='row']/a/@href"))
        print "Hop count:", i, full_url
        if last_len == len(links):
            break # probably done with crawling the links
        last_len = len(links)
        if random.randint(0,10)<2:
            time.sleep(1)
    print len(links)
    return links

def get_car_info(links):
    for i,url in enumerate(links):
        print "Downloading:", url
        if i%100==0:
            print ">>>>>>   Done processing %d cars!!!" % i 
        car_info(url)
        if i%10==0:
            time.sleep(1)
    with open('car_data.json', 'wb') as fp:
        json.dump(cars, fp, indent=2)

def car_info(url):
    global cars
    page = requests.get(url)
    tree = html.fromstring(page.text)
    m = re.match(r"http://(?P<city>\w+)\..*/(?P<id>\d+)\.html", url)
    if m:
        m = m.groupdict()
        _id_, city = m['id'], m['city']
        fname = "%s_%s.html" % (city, _id_)
        print "Writing:", fname
        with open("%s/%s.html" % ( HTMLDIR, fname), 'w') as f:
            f.write(page.text.encode('ascii', errors='ignore'))
    else:
        return None
    try:
        title = tree.xpath("//h2[@class='postingtitle']/text()")[1].strip()
        title = title.encode('ascii', errors='ignore')
    except IndexError:
        return None
    c = {"id": _id_, "title": title}
    c["make"], c["cost"], c["location"], c["year"] = parse_title(title)

    attr = extract_atrribute(tree)
    c['attr'] = attr
    c['body'] = ''.join(tree.xpath('//section[@id="postingbody"]/text()'))
    # get images
    # c['img'] = []
    # for img in tree.xpath("//div[@id='thumbs']/a"):
    #     imgid = img.xpath('@data-imgid')[0]
    #     fname = imgid + ".jpg"
    #     # l = img.xpath('@href')[0]
    #     # with open(IMGDIR+fname, 'wb') as f:
    #     #     shutil.copyfileobj(requests.get(l, stream=True).raw, f)
    #     c['img'].append(fname)

    cars.append(c)

def parse_title(s):
    s = unicode(s).encode('ascii', errors='ignore')
    first_part, _, second_part = s.partition('-')
    first_part = first_part.strip()
    second_part = second_part.strip()
    reg_c = re.compile(r".*(\$\d+).*")
    reg_l = re.compile(r".*\((.*)\).*")
    reg_y = re.compile(r"^(\d{2,4}) .*")

    l = reg_l.match(second_part)
    if l: 
        l = l.groups(1)[0]
    c = reg_c.match(second_part)
    if c: 
        c = c.groups(1)[0]
    y = reg_y.match(first_part)
    m = ""
    if y:
        y = y.groups(1)[0]
        if len(y) == 2:
            if y>50: y = '19' + y
            else : y = '20' + y
        m = first_part[len(y)+1:].strip()
    if not y and not c: m = first_part
    return m,c,l,y

def extract_atrribute(tree):
    attr = {}
    for attrib in tree.xpath("//p[@class='attrgroup']/span"):
        a = attrib.text_content()
        k = a.split(':')
        if len(k)<2:
            k,v = 'title', k[0]
        else:
            k, v = k[0], ','.join(k[1:])
            v = v.strip()
            k = k.strip()
        attr[k] = v
    # get posted and updated date
    for key in ['posted', 'updated']:
        p = tree.xpath('//p[@class="postinginfo"][contains(text(), "%s")][1]' % key) 
        if p:
            attr[key] = p[0].xpath('//time/@datetime')[0]
    return attr

def clean_car_json_data(fname):
    D = json.load(open(fname))
    for elem in D:
        # remove non alphanumeric characters from make, cost, localtion, year
        # fix year
        for k,v in zip(['make', 'cost', 'location', 'year'], parse_title(elem['title'])):
            elem[k] = v if v else ""
        # fix the attrib from html pages
        with open(HTMLDIR + elem['id'] + '.html') as f:
            tree = html.fromstring(f.read())
            elem['attr'] = extract_atrribute(tree)
    with open('craiglist/car_data_new.json', 'wb') as fp:
        json.dump(D, fp, indent=4, sort_keys=True)

def flatten_table(fname):
    D = json.load(open(fname))
    E = []
    for elem in D:
        X = dict(((key, elem[key]) for key in
                  ['cost', 'location', 'title', 'make', 'year', 'id'] ))
        for k,v in elem['attr'].items():
            if k not in ['posted', 'updated']:
                X['attr_%s' % k] = v
            else:
                X[k] = v
        E.append(X)
    with open('craiglist/car_data_present.json', 'wb') as fp:
        json.dump(E, fp, indent=4, sort_keys=True)
    
            

if __name__ == "__main__":
    # links = get_all_links(cities[0], 100, fromFile='list_links.txt')
    # links.extend(get_all_links(cities[1], 100))
    # with open('list_links.txt', 'w') as f:
    #     f.write('\n'.join(links))
    # print links
    # get_car_info(links)
    # print parse_title(u"\u2606\u2606 1990 CADILLAC SEDAN DEVILLE \u2606\u2606 - $1200 (Marshall, Wi 53559)")
    # with open(HTMLDIR + '4704328594.html') as f:
    #    tree = html.fromstring(f.read())
    #    print json.dumps(extract_atrribute(tree), indent=4)
    # clean_car_json_data('craiglist/car_data.json')
    flatten_table(sys.argv[1])
