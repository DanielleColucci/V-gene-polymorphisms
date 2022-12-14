import collections as coll
import gzip
import os
import re
import sys
import textwrap
import datetime
from traceback import format_list
import warnings
import numpy as np


def check_scripts_dir():
    """
    Check we're in the right directory (Scripts)
    """

    if not os.getcwd().endswith('Scripts'):
        if 'Scripts' in os.listdir(os.getcwd()):
            os.chdir('Scripts')
        else:
            raise Exception("Check your current working directory: this is designed to be run from /Scripts")

def read_fa(ff):
    """
    :param ff: opened fasta file
    read_fa(file):Heng Li's Python implementation of his readfq function (tweaked to only bother with fasta)
    https://github.com/lh3/readfq/blob/master/readfq.py
    """

    last = None                                 # this is a buffer keeping the last unprocessed line
    while True:                                 # mimic closure
        if not last:                            # the first record or a record following a fastq
            for l in ff:                        # search for the start of the next record
                if l[0] in '>':                 # fasta header line
                    last = l[:-1]               # save this line
                    break
        if not last:
            break
        name, seqs, last = last[1:], [], None
        for l in ff:                            # read the sequence
            if l[0] in '>':
                last = l[:-1]
                break
            seqs.append(l[:-1])
        if not last or last[0] != '+':          # this is a fasta record
            yield name, ''.join(seqs), None     # yield a fasta record
            if not last:
                break
        else:
            raise IOError("Input file does not appear to be a FASTA file - please check and try again")

def fastafy(gene, seq_line):
    """
    :param gene: Gene symbol, extracted from the read id
    :param seq_line: Total protein primary sequence, extracted from input FASTA/generated by in silico splicing
    :return: An output-compatible FASTA entry ready for writing to file
    """
    return ">" + gene + "\n" + textwrap.fill(seq_line, 44) + "\n"

def translate(seq):
        table = {
            'ata':'I', 'atc':'I', 'att':'I', 'atg':'M',
            'aca':'T', 'acc':'T', 'acg':'T', 'act':'T',
            'aac':'N', 'aat':'N', 'aaa':'K', 'aag':'K',
            'agc':'S', 'agt':'S', 'aga':'R', 'agg':'R',                
            'cta':'L', 'ctc':'L', 'ctg':'L', 'ctt':'L',
            'cca':'P', 'ccc':'P', 'ccg':'P', 'cct':'P',
            'cac':'H', 'cat':'H', 'caa':'Q', 'cag':'Q',
            'cga':'R', 'cgc':'R', 'cgg':'R', 'cgt':'R',
            'gta':'V', 'gtc':'V', 'gtg':'V', 'gtt':'V',
            'gca':'A', 'gcc':'A', 'gcg':'A', 'gct':'A',
            'gac':'D', 'gat':'D', 'gaa':'E', 'gag':'E',
            'gga':'G', 'ggc':'G', 'ggg':'G', 'ggt':'G',
            'tca':'S', 'tcc':'S', 'tcg':'S', 'tct':'S',
            'ttc':'F', 'ttt':'F', 'tta':'L', 'ttg':'L',
            'tac':'Y', 'tat':'Y', 'taa':'_', 'tag':'_',
            'tgc':'C', 'tgt':'C', 'tga':'_', 'tgg':'W',
        }
        protein = ''
        #if len(seq)%3 == 0:
        for i in range(0, len(seq) - len(seq)%3, 3):
            codon = seq[i:(i + 3)]
            if table[codon] != '_':
                protein += table[codon]
            else: 
                break
        return protein

def build_dict(fa):
    #build a dictionary of nested empty dictionaries from fasta file, 'fa', where each item in the dict is a gene, 
    #and each gene has 4 nested dicts: 'genename', 'allele', 'dnaseq', and 'aaseq'. 
    dict = {}
    list1 = fa.split('>')
    for i in list1:
        #create a list of genes
        gene = ''
        if i != '':
            beg_gene = i.find('|')
            end_gene = i.find('*')
            gene = i[beg_gene + 1:end_gene]
        else:
            continue

        val = -1
        for j in range(0, 13):                #filtering out partial sequences
            val = i.find('|', val+1)
        if i[val + 1] != ' ':
            continue

        if gene not in dict:                  #append nested dictionary to dict
            dict.update({gene:{'genename':[], 'allele':[], 'dnaseq':[], 'aaseq':[]}})
        
        if i != '':
            #append gene names
            beg_name = i.find('>')
            end_name = i.find('|')
            name = i[beg_name + 1:end_name]
            dict[gene]['genename'] += [name]

            #append alleles
            beg_al = i.find('*')
            end_al = i.find('|', beg_al)
            allele = i[beg_al + 1:end_al]
            dict[gene]['allele'] += [allele]

            #append dna sequences
            beg_dna = i.find('\n')
            dna_seq = ''
            for j in range(beg_dna + 1, len(i)):
                if j != '\n':
                    dna_seq += i[j]
            dict[gene]['dnaseq'] += [dna_seq]

            #append amino acid sequences
            dna_seq2 = dna_seq.replace('\n', '')
            aa_seq = translate(dna_seq2)
            dict[gene]['aaseq'] += [aa_seq]

    return dict

def compare_prt(dict):
    for i in dict:
        for j in range(len(dict[i]['aaseq']) - 1):
            for k in range(j+1, len(dict[i]['aaseq'])):
                if dict[i]['aaseq'][j] != dict[i]['aaseq'][k]:
                    print('residue change between', i, '*', dict[i]['allele'][j], 'and', i, '*', dict[i]['allele'][k])
                            #':', dict[i]['aaseq'][j][k], k + 1, dict[i]['aaseq'][j+1][k])

#inputfile = "/Users/anh7/Documents/Scripts/test.rtf"

f = open(r"C:\\Users\\ddcol\\OneDrive\\Documents\\Scripts\\translation\\TRAV_complete.txt")
TRAV = f.read() 
f.close()
TRAV_dict = build_dict(TRAV)

compare_prt(TRAV_dict)

f = open(r"C:\\Users\\ddcol\\OneDrive\\Documents\\Scripts\\translation\\TRBV_complete.txt")
TRBV = f.read() 
f.close()
TRBV_dict = build_dict(TRBV)

compare_prt(TRBV_dict)