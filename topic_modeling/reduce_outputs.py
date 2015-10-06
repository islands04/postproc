"""
Copyright 2015 Georgia Institute of Technology

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

     http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.

-----

This application simplifies the topic modeling outputs generated from Nonnegative 
Matrix Factorization (NMF) by representing the top terms in CSV files and using the
probability assignments to output the labels per document in order of descending
probabilty. 

Contributors: Ramakrishnan Kannan, Tiffany Huang, Barry Drake, Ashley Beavers

Last updated: 5 Oct 2015

"""
import numpy as np
import sys
import os
import argparse
import common
import xml.etree.ElementTree as ET
import json

# parse the XML output file and extract the top terms
def extract_top_terms_from_xml(xml_file):
    try:
        with open(xml_file):
            pass
    except IOError:
        sys.exit("Error: No such clusters file: %s." % (xml_file))
    try:
        tree = ET.parse(xml_file)
    except ET.ParseError:
        sys.exit("Error: Bad XML - unable to parse: %s." % (xml_file))
    dataset = tree.getroot()
    terms = []
    for i,node in enumerate(dataset):
        temp = []
        for term in node[1]:
            temp.append(term.attrib['name'])
        terms.append(temp)
    return terms, i + 1

# parse the JSON output file and extract the top terms
def extract_top_terms_from_json(json_file):
    try:
        with open(json_file) as js:
            try:
                tree = json.load(js)
            except ValueError:
                sys.exit("Error: Bad JSON - unable to parse: %s." % (json_file))
    except IOError:
        sys.exit("Error: No such clusters file: %s." % (json_file))
    terms = []
    for i,node in enumerate(tree['nodes']):
        temp = []
        for term in node['top_terms']:
            temp.append(term)
        terms.append(temp)
    return terms, i + 1

# write the simplified CSV top terms output
def write_reduced_terms(terms, outdir, num_clusters):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    print 'Writing reduced terms...'
    np.savetxt(outdir + os.sep + 'clusters_' + str(num_clusters) + '.csv', terms, delimiter=",", fmt="%s")

# compute labels in order of descending probabilty using the fuzzy assignments output file
def compute_label_assignments(fuzzyfile):
    try:
        fuzzy = np.loadtxt(fuzzyfile, delimiter=',')
    except IOError:
        sys.exit("Error: No such fuzzy assignments file: %s." % (fuzzyfile))
    if fuzzy.shape[0] == 0:
        sys.exit("Error: Fuzzy assignment file contains no samples: %s." % (fuzzyfile))
    if len(fuzzy.shape) == 1:
        sys.exit("Error: Fuzzy assignment file only contains one value per sample: %s." % (fuzzyfile))
    cluster_members = np.argsort(fuzzy, axis=1)[:, ::-1]
    cluster_indices = cluster_members[:,]
    return cluster_indices        

# write the assignments/labels output file
def write_assignments(outdir, num_clusters, assignments):
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    print 'Writing assignments...'
    np.savetxt(outdir + os.sep + 'assignments_labels_' + str(num_clusters) + '.csv', 
        assignments, delimiter=",", fmt="%i")

#------------------------------------------------------------------------------------------------
# COMMAND LINE APPLICATION
#------------------------------------------------------------------------------------------------
if __name__ == "__main__":    

    # argument parser for required and optional arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--topicspath", action="store", 
        required=True, metavar="topicspath")
    parser.add_argument("--fuzzypath", action="store", 
        required=True, metavar="fuzzypath")
    parser.add_argument("--outdir", action="store", 
        required=False, metavar="outdir", default='.')
    args = parser.parse_args()

    # determine output file format
    if 'xml' in args.topicspath:
        terms, num_clusters = extract_top_terms_from_xml(args.topicspath)
    elif 'json' in args.topicspath:
        terms, num_clusters = extract_top_terms_from_json(args.topicspath)
    else:
        print 'File format not supported: %s' % (args.topicspath)
        sys.exit(1)
    # write the simplified top terms output file
    write_reduced_terms(terms, args.outdir, num_clusters)
    # compute and write the label probabilities output file
    assignments = compute_label_assignments(args.fuzzypath)
    write_assignments(args.outdir, num_clusters, assignments)

