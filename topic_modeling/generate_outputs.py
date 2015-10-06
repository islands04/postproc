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

This application performs topic modeling from Nonnegative Matrix 
Factorization (NMF) by extracting the top terms in each cluster
and the soft and hard cluster assignments for each document.

Contributors: Ramakrishnan Kannan, Tiffany Huang, Barry Drake, Ashley Beavers

Last updated: 5 Oct 2015

"""
import numpy as np
import os
import argparse
import common
from collections import Counter

# compute soft assignments for each document, using the normalized values of the 
# h matrix to represent the proabilities for each document's cluster assignment
def compute_fuzzy_assignments(num_clusters, num_docs, h):
    hT = h.T # in place operation to transpose the h matrix
    # create empty stucture to store probabilities
    probabilities = np.empty((num_docs, num_clusters))
    # iterate through each row, compute the sum, use sum to determine probability
    i = 0
    for m in hT:
        inv_sum = 1/sum(m)
        j = 0
        for n in m:
            probabilities[i,j] = n*inv_sum
            j += 1
        i += 1
    return probabilities

# compute hard assignments for each document
def compute_assignments(h):
    hT = h.T # in place operation to transpose the h matrix
    # sort by size of element per document
    cluster_members = np.argsort(hT, axis=1)[:, ::-1]
    # extract first element of sorted values as cluster label
    cluster_indices = cluster_members[:, 0]
    # determine how many of each label there are in the dataset
    counts = dict(Counter(cluster_indices))
    return cluster_indices, counts

# use the w matrix to identify the most important terms
def extract_top_terms(num_clusters, maxterms, dictionary, w):
    print 'Extracting top terms...'
    # create empty structure to store terms
    top_terms = np.empty((num_clusters, maxterms), dtype=object)
    wT = w.T # in place operation to transpose the h matrix
    # extract top terms for each cluster in descending order
    for cluster in range(num_clusters):
        terms = wT[cluster, :]
        sorted_index = np.argsort(terms)[::-1]
        top_index = sorted_index[0:maxterms]
        top_terms[cluster, :] = np.array(dictionary)[top_index]
    return top_terms

# write the topics for each cluster in XML format
def write_topics_xml(outdir, num_docs, num_clusters, counts, topterms, assignments):
    with open(outdir + os.sep + 'clusters_' + str(num_clusters) + '.xml', 'w') as topics:
        topics.write('<?xml version="1.0"?>\n')
        topics.write('<DataSet id="' + str(num_docs) + '">\n')
        for i, cluster in enumerate(topterms):
            topics.write('    <node id="' + str(i) + '">\n')
            topics.write('        <doc_count>' + str(counts[i]) + '</doc_count>\n')
            topics.write('        <top_terms>\n')
            for term in cluster:
                topics.write('            <term name="' + term + '"/>\n')
            topics.write('        </top_terms>\n')
            topics.write('    </node>\n')
        topics.write('</DataSet>\n')

# write the topics for each cluster in JSON format
def write_topics_json(outdir, num_docs, num_clusters, counts, topterms, assignments):
    with open(outdir + os.sep + 'clusters_' + str(num_clusters) + '.json', 'w') as topics:
        topics.write('{\n')
        topics.write('    "doc_count": ' + str(num_docs) + ',\n')
        topics.write('    "nodes": [\n')
        length = len(topterms)
        for i, cluster in enumerate(topterms):
            topics.write('        {\n')
            topics.write('            "id": ' + str(i) + ',\n')
            topics.write('            "doc_count": ' + str(counts[i]) + ',\n')
            topics.write('            "top_terms": [\n')
            terms = ',\n'.join(['                "' + term + '"' for term in cluster])
            topics.write(terms + '\n')
            # for term in cluster:
            #     topics.write('                "' + term + '",\n')
            topics.write('            ]\n')
            if i < length-1:
                topics.write('        },\n')
            else:
                topics.write('        }\n')
        topics.write('    ]\n')
        topics.write('}\n')

# write the output files: XML/JSON topics, CSV fuzzy assignments
def write_report(outdir, num_docs, num_clusters, prob, counts, topterms, assign, format='XML'):
    # ensure the output directory exists
    if not os.path.exists(outdir):
        os.makedirs(outdir)
    print 'Writing detailed output files...'
    # determine format of topics
    if format.lower() == 'xml':
        write_topics_xml(outdir, num_docs, num_clusters, counts, topterms, assign)
    elif format.lower() == 'json':
        write_topics_json(outdir, num_docs, num_clusters, counts, topterms, assign)
    else:
        print 'File format not supported: %s' % (format)
        sys.exit(1)
    # save fuzzy assignments with 3 decimal places and scientific notation
    np.savetxt(outdir + os.sep + 'assignments_fuzzy_' + str(num_clusters) + '.csv', 
        prob, delimiter=",", fmt="%.3e")
    # save hard assignments
    with open(outdir + os.sep + 'assignments_' + str(num_clusters) + '.csv', 'w') as f:
        f.write(','.join([str(x) for x in assign]))

#------------------------------------------------------------------------------------------------
# COMMAND LINE APPLICATION
#------------------------------------------------------------------------------------------------

if __name__ == "__main__":    
    
    # argument parser for required and optional arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("--dictpath", action="store", 
        required=True, metavar="dictpath")
    parser.add_argument("--docpath", action="store", 
        required=True, metavar="docpath")
    parser.add_argument("--matrixpath", action="store", 
        required=True, metavar="matrixpath")
    parser.add_argument("--infile_w", action="store", 
        required=True, metavar="infile_w")
    parser.add_argument("--infile_h", action="store", 
        required=True, metavar="infile_h")
    parser.add_argument("--maxterms", action="store", 
        required=True, metavar="maxterms", type=int)
    parser.add_argument("--outdir", action="store", 
        required=False, metavar="outdir", default='.')
    parser.add_argument("--tabstrip", action="store", 
        required=False, metavar="tabstrip", type=int, default=0)
    parser.add_argument("--format", action="store", 
        required=False, metavar="format", default='XML')
    args = parser.parse_args()

    # ensure the matrix, dictionary, and documents files are of compatible sizes
    num_docs, num_terms = common.check_matrix_files_dimensions(args.docpath, args.dictpath, 
        args.matrixpath)
    # validate shapes of w and h matrices and load them
    w, h, num_clusters = common.check_nmf_outputs_dimensions(args.matrixpath, args.infile_w, 
        args.infile_h, args.maxterms)
    # load the dictionary
    dictionary = common.load_dictionary(args.dictpath, tabstrip=args.tabstrip)
    # use the w matrix to determine top terms
    topterms = extract_top_terms(num_clusters, args.maxterms, dictionary, w)
    # use the h matrix to determine fuzzy assignments
    probabilities = compute_fuzzy_assignments(num_clusters, num_docs, h)
    # use the h matrix to determine fuzzy assignments
    assignments, counts = compute_assignments(h)
    # write the output files
    write_report(args.outdir, num_docs, num_clusters, probabilities, counts, topterms, 
        assignments, args.format)


