# -*- coding: UTF-8 -*-
from itertools import izip
import codecs
import math
import sys
import os
import io
from collections import defaultdict

class BLUE(object):

    def __init__(self):
        return

    def get_ngram_words(self,file_data,i,n):
        end=i+n
        space=' '
        word = space.join(file_data[i:end])
        word = word.lower()
        return word





    def ngrams(self,input_data, n):
        file_data = input_data.split()
      #print "Imside ngram  data",data
        ngram_dict = {}

        ## Handling unigram
        if n==1:
            data_length=len(file_data)
        else: ## Handling multigram
            data_length=len(file_data)-n+1

        for i in range(data_length):
            word=self.get_ngram_words(file_data,i,n)
            if word not in ngram_dict:
                ngram_dict[word]=1
            else:
                count=ngram_dict.get(word)
                count+=1
                ngram_dict[word]=count
        return ngram_dict


    def read_input(self,s):
        file_paths=[]
        file_paths.append(s[1])
        ref=s[2]
        if os.path.isdir(ref):
        # Walk the tree.
            for root, directories, files in os.walk(ref):
                for filename in files:
                # Join the two strings in order to form the full filepath.
                    filepath = os.path.join(root, filename)
                    file_paths.append(filepath)
        else:
            file_paths.append(ref)

        return file_paths


    def calculate_c_r(self,c,r,cand_ref_files):
        reference_files=defaultdict(lambda:{})
        lines_list=[]
        for lines in izip(*cand_ref_files):
            lines_list.append(lines)
            candidate_file_ngram=self.ngrams(lines[0],1)
            for file_count in range(1,len(cand_ref_files)):
                reference_files[file_count]=self.ngrams(lines[file_count],1)
            c_latest=sum(candidate_file_ngram.values())
            c = c+c_latest
            #ref = sum(reference_files[1].values())
            #ref_update=100000000000
            ref_update=float("inf")
            for key in reference_files:
                reference_file_ngram=reference_files.get(key)
                ref_latest=sum(reference_file_ngram.values())
                if abs(c_latest-ref_latest) < abs(c_latest-ref_update):
                    ref_update=ref_latest
            r = r+ref_update
        return c,r,lines_list


    def find_clipped_total(self,clipped_val,total_val,candidate_file_ngram,reference_files):
        #num=0
        #deno=0
        for candidate_word in candidate_file_ngram:
            value = 0
            for reference_file_count in reference_files:
                #print candidate_word,reference_files,reference_file_ngram
                reference_file_ngram=reference_files.get(reference_file_count)
                if candidate_word in reference_file_ngram:
                    value = max(value,reference_file_ngram.get(candidate_word))
            clipped_val = clipped_val + min(value, candidate_file_ngram.get(candidate_word))
        total_val = total_val + sum(candidate_file_ngram.values())
        return clipped_val,total_val



    def calculate_pN(self,lines_list,files):
        p_N=0
        for i in range(1, 5):
            clipped_val,total_val = 0,0
            reference_files = {}
            #print "Inisde",lines_list
            for lines in lines_list:

                ## Calculating n gram for candidate file
                candidate_file_ngram = self.ngrams(lines[0], i)

                ## Calculating n gram for refernce file or files
                ## If just one refernce file
                if len(files) == 2:
                    reference_files[1]=self.ngrams(lines[1], i)
                else: ## if multiple refernece files
                    for file_count in range(1, len(files)):
                        reference_files[file_count] = self.ngrams(lines[file_count], i)
                clipped_val,total_val=self.find_clipped_total(clipped_val,total_val,candidate_file_ngram,reference_files)

            p_N = p_N+ math.log(float(clipped_val)/total_val) * 0.25

        
        return p_N



    def find_c_r_pN(self,files):
        c,r=0,0
        c,r,lines_list=self.calculate_c_r(c,r,files)
        #print "c is ",c,"r is ",r
        p_N=self.calculate_pN(lines_list,files)
        return c,r,p_N




if __name__ == "__main__":

    s=sys.argv
    out_file=open('bleu_out.txt', 'w')


    blue_obj=BLUE()

    ## Reading input file names ###
    cand_ref_files=blue_obj.read_input(s)

    ## Reading data from files ###
    files=[]
    for file in cand_ref_files:
        files.append(codecs.open(file,'r', encoding='utf-8'))

    ## Finding c, r, pN ###
    c,r,p_N=blue_obj.find_c_r_pN(files)

    ## Setting BP value
    BP = 1 if c > r else math.exp(1 - float(r)/c)

    ## Calculating BLUE score
    BLEU_score = BP * math.exp(p_N)

    ## Writing in output file
    out_file.write(str(BLEU_score))
