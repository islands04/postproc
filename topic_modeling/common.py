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

This file contains utility functions that are used in the post-processing applications.

Contributors: Ramakrishnan Kannan, Tiffany Huang, Barry Drake, Ashley Beavers

Last updated: 5 Oct 2015

"""
import numpy as np
import sys

# load the dictionary file, optionally removing any content beyond the first tab
def load_dictionary(dictpath, tabstrip=False):
    try:
        with open(dictpath, 'r') as dictionaryPath:
            dictionary = dictionaryPath.read().split("\n")
            dictionary.pop()
    except IOError:
        sys.exit("Error: No such dictionary file: %s." % (dictpath))
    if tabstrip:
        for i, line in enumerate(dictionary):
            dictionary[i] = line.split('\t')[0].strip()
    return dictionary

# ensure that the dimensions of the matrix files match 
def check_matrix_files_dimensions(docpath, dictpath, matrixfile):
    try:
        with open(docpath) as f:
            for i, l in enumerate(f):
                pass
        num_docs = i + 1
    except IOError:
         sys.exit("Error: No such documents file: %s." % (docpath))
    try:
        with open(dictpath) as f:
            for i, l in enumerate(f):
                pass
        num_terms = i + 1   
    except IOError:
         sys.exit("Error: No such dictionary file: %s." % (dictpath))
    try:
        with open(matrixfile) as f:
            found = False
            for i, l in enumerate(f):
                if i == 0:
                    pass
                else:
                    if not l.startswith("%") and not found:
                        [terms, docs, nz] = map(int, l.split(' '))
                        found = True
                        t = 0
                    else:
                        t += 1
    except IOError:
         sys.exit("Error: No such matrix file: %s." % (matrixfile))
    if nz != t:
        sys.exit("Error: Matrix non-zero count and header non-zero count do not match.")
    if num_docs != docs:
        sys.exit("Error: Documents list and the number of matrix columns do not match.")
    if num_terms != terms:
        sys.exit("Error: Dictionary list and the number of term rows do not match.")
    return num_docs, num_terms

# ensure that the dimensions of the w and h matrix match the matrix files
def check_nmf_outputs_dimensions(matrixfile, wfile, hfile, maxterms):
    with open(matrixfile) as f:
        for i, l in enumerate(f):
            if i == 0:
                pass
            else:
                if not l.startswith("%"):
                    [terms, docs, nz] = map(int, l.split(' '))
                    break
                else:
                    pass
    try:
        w = np.loadtxt(wfile, delimiter=',')
    except IOError:
         sys.exit("Error: No such W file: %s." % (wfile))
    try:
        h = np.loadtxt(hfile, delimiter=',')
    except IOError:
         sys.exit("Error: No such H file: %s." % (hfile))

    if w.shape[0] != terms:
        if w.shape[1] != terms:
            sys.exit("Error: W matrix size and the number of term rows in input matrix do not match.")
        else:
            print 'Warning: Transposing W matrix...'
            w = w.T
    if h.shape[1] != docs:
        if h.shape[0] != docs:
            sys.exit("Error: H matrix size and the number of document columns in input matrix do not match.")
        else:
            print 'Warning: Transposing H matrix...'
            h = h.T
    if w.shape[1] != h.shape[0]:
        if w.shape[0] != h.shape[1]:
            sys.exit("Error: W and H matrix sizes do not match.")
    if terms < maxterms:
        sys.exit("Error: Maxterms must be less than the length of the dictionary")
    num_clusters = w.shape[1]
    return w, h, num_clusters
