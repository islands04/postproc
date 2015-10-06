# post-processing


This set of tools is for post processing NMF outputs from SmallK.

## Topic Modeling
The `topic_modeling/` directory contains applications useful for extracting topic modeling results from NMF input and output files.

If NMF was run on a sparse term-document matrix and there exist associated dictionary and documents files, the output W and H matrices along with these original files can be used to generate topic models.

##generate_outputs.py

Running the application without any arguments will present a list of required and optional input arguments.

```
python topic_modeling/generate_outputs.py
```
Output:

```
usage: generate_outputs.py [-h] 
							--dictpath dictpath 
							--docpath docpath
                            --matrixpath matrixpath 
                            --infile_w infile_w
                            --infile_h infile_h 
                            --maxterms maxterms
                           [--outdir outdir] 
                           [--tabstrip tabstrip]
                           [--format format]
``` 
###Inputs

**dictpath**: filepath for the input dictionary file, such as `dictionary.txt`

**docpath**: filepath for the input documents file, such as `documents.txt`

**matrixpath**: filepath for the input matrix file, such as `matrix.mtx`

**infile_w**: filepath for the NMF W matrix output, such as `w.csv`

**infile_h**: filepath for the NMF H matrix output, such as `h.csv`

**maxterms**: number of top terms desired in the output files

**[outdir]**: output directory, defaults to the current directory

**[tabstrip]**: whether or not to strip content from the dictionary file beyond the first tab, defaults to False

**[format]**: cluster topics output file format (XML or JSON), defaults to XML

###Outputs

This application will generate three files:

**assignments_fuzzy_[k].csv**: This file contains one line per document with k elements, each representing the probability of that document belonging to the kth cluster. This is the soft clustering result.

**assignments_[k].csv**: This file contains one element per document, representing the cluster to which that document was assigned. This is the hard clustering result.

**clusters_[k].{xml,json}**: This file contains JSON or XML formatted data that represents the cluster ids, the number of documents per cluster, and the top terms per cluster. 

###Usage

A sample run of this application might look like the following:

```
python topic_modeling/generate_outputs.py \
	--dictpath test_data/dictionary.txt \
	--docpath test_data/documents.txt \
	--matrixpath test_data/matrix.mtx \
	--infile_w test_data/w.csv \
	--infile_h test_data/h.csv \
	--maxterms 5 \
	--outdir results
```

This would generate the following files:

```
results/
	clusters_10.xml
	assignments_fuzzy_10.csv
	assignments_10.csv
```

##reduce_outputs.py

Running the application without any arguments will present a list of required and optional input arguments.

```
python topic_modeling/reduce_outputs.py
```
Output:

```
usage: reduce_outputs.py [-h] 
						  --topicspath topicspath 
						  --fuzzypath fuzzypath
                         [--outdir outdir]
``` 
###Inputs

**topicspath**: filepath for the input topics file, such as `clusters_10.json`

**fuzzypath**: filepath for the input fuzzy assignments file, such as `assignments_fuzzy_10.csv`

**[outdir]**: output directory, defaults to the current directory

###Outputs

This application will generate two files:

**assignments_labels_[k].csv**: This file contains one line per document with k elements, representing in decreasing probability the clusters to which that document belongs. This is the soft clustering result. For example, a particular line might look like

```
6,5,2,8,3,9,1,4,7,0
```
This would mean that the document is most likely to belong to cluster 6, then cluster 5, and so on.

**clusters_[k].csv**: This file contains one line per cluster with top terms for that cluster separated by commas. 

###Usage

A sample run of this application might look like the following:

```
python topic_modeling/reduce_outputs.py \
	--topicspath results/clusters_10.xml \
	--fuzzypath results/assignments_fuzzy_10.csv \
	--outdir reduced_results
```

This would generate the following files:

```
reduced_results/
	clusters_10.csv
	assignments_labels_10.csv
```



