# import package ...
import copy
import csv
import math
import os.path
import sys
import gzip
import json
import numpy as np

collection_size = 1185999
avdl = 1215.16291
N = 976

class Posting:
    def __init__(self, query_name, query_terms, num_words, query_find):
        self.query_name = query_name
        self.query_terms = []
        for i in query_terms:
            self.query_terms.append(i)
        self.num_words = num_words
        self.query_find = query_find


def mysplit(s):
    head = s.rstrip('0123456789')
    tail = s[len(head):]
    return head, tail


def buildIndex(inputFile, queries):
    global collection_size
    inverted_list = []
    easy_outcome = []
    occurence_of_terms = []
    ql_result = []
    term_docs = []
    with gzip.open(inputFile, "rt", encoding="utf-8") as f:
        data = json.load(f)
    for i in queries:
        inverted_list.append(i)
        inverted_list.append([])
        easy_outcome.append(i)
        easy_outcome.append([])
        occurence_of_terms.append(i)
        occurence_of_terms.append(0)
        term_docs.append(i)
        term_docs.append(0)
    for items in data['corpus']:
        iden = items['storyID']
        text = np.array(items['text'].split())
        for i in range(0, len(inverted_list), 2):
            if isinstance(inverted_list[i], list):
                inorder = []
                for j in inverted_list[i]:
                    cur_indexes = np.where(text == j)[0]
                    if len(cur_indexes) == 0:
                        inorder = []
                        break
                    elif len(inorder) == 0:
                        inorder = cur_indexes
                    else:
                        temp = []
                        for h in range(len(inorder)):
                            if inorder[h] + 1 in cur_indexes:
                                temp.append(inorder[h] + 1)
                        inorder = temp
                        if len(inorder) == 0:
                            break
                if len(inorder) != 0:
                    term_docs[i+1] += 1
                    inverted_list[i+1].append(Posting(iden, inorder, len(text), inverted_list[i]))
                    if iden not in ql_result:
                        ql_result.append(iden)
                        ql_result.append([Posting(iden, inorder, len(text), inverted_list[i])])
                    else:
                        ql_result[ql_result.index(iden) + 1].append(Posting(iden, inorder, len(text), inverted_list[i]))
                    easy_outcome[i+1].append(iden)
                    occurence_of_terms[i+1] += len(inorder)
            elif inverted_list[i] in text:
                term_docs[i+1] += 1
                inverted_list[i+1].append(Posting(iden, np.where(text == inverted_list[i])[0], len(text), inverted_list[i]))
                if iden not in ql_result:
                    ql_result.append(iden)
                    ql_result.append([Posting(iden, np.where(text == inverted_list[i])[0], len(text), inverted_list[i])])
                else:
                    ql_result[ql_result.index(iden) + 1].append(Posting(iden, np.where(text == inverted_list[i])[0], len(text), inverted_list[i]))
                easy_outcome[i+1].append(iden)
                occurence_of_terms[i+1] += len(np.where(text == inverted_list[i])[0])
    return inverted_list, easy_outcome, occurence_of_terms, ql_result, term_docs


def print_res(result, info, outputFile, mode):
    with open(outputFile, mode) as f:
        if info[0] in ['or', 'and']:
            for i in range(len(result)):
                id_skip = ''
                name_skip = ''
                if len(info[1]) >= 11:
                    id_skip = ' '
                else:
                    for j in range(len(info[1]), 11):
                        id_skip += ' '
                for j in range(len(result[i]), 24 - len(str(i + 1))):
                    name_skip += ' '
                f.write(info[1] + id_skip + 'skip ' + result[i] + name_skip + str(i + 1) + ' 1.0000 skinreich\n')
            f.close()
        else:
            for i in range(len(result)):
                id_skip = ''
                name_skip = ''
                if len(info[1]) >= 11:
                    id_skip = ' '
                else:
                    for j in range(len(info[1]), 11):
                        id_skip += ' '
                for j in range(len(result[i][0].query_name), 24 - len(str(i + 1))):
                    name_skip += ' '
                f.write(info[1] + id_skip + 'skip ' + result[i][0].query_name + name_skip + str(i + 1) + ' {:.4f} skinreich\n'.format(result[i][1]))
            f.close()


def runQueries(inputFile, queriesFile, outputFile):
    with open(queriesFile, 'r') as f:
        tsv_file = csv.reader(f, delimiter='\t')
        for line in tsv_file:
            queries = []
            info = []
            occurence = []
            for i in range(len(line)):
                if i in [0, 1]:
                    info.append(line[i])
                else:
                    if " " in line[i]:
                        terms = line[i].split()
                        queries.append(terms)
                        if line[i] not in occurence:
                            occurence.append(terms)
                            occurence.append(1)
                        else:
                            occurence[occurence.index(line[i]) + 1] += 1
                    else:
                        queries.append(line[i])
                        if line[i] not in occurence:
                            occurence.append(line[i])
                            occurence.append(1)
                        else:
                            occurence[occurence.index(line[i]) + 1] += 1
            result = []
            index, easy_outcome, tf, ql_res, docs = buildIndex(inputFile, queries)
            if info[0] == 'or':
                for i in range(1, len(easy_outcome), 2):
                    for j in easy_outcome[i]:
                        if j not in result:
                            result.append(j)
                result.sort()
                if os.path.exists(outputFile):
                    print_res(result, info, outputFile, 'a')
                else:
                    print_res(result, info, outputFile, 'w+')
            if info[0] == 'and':
                for i in range(1, len(easy_outcome), 2):
                    for j in easy_outcome[i]:
                        if j not in result:
                            everywhere = True
                            for h in range(1, len(easy_outcome), 2):
                                if j not in easy_outcome[h]:
                                    everywhere = False
                                    break
                            if everywhere:
                                result.append(j)
                result.sort()
                if os.path.exists(outputFile):
                    print_res(result, info, outputFile, 'a')
                else:
                    print_res(result, info, outputFile, 'w+')
            if info[0] == 'bm25':
                b = 0.75
                k1 = 1.8
                k2 = 5
                for i in range(1, len(ql_res), 2):
                    result.append([ql_res[i][0], 0])
                    for j in range(len(ql_res[i])):
                        K = k1 * ((1-b) + b * (ql_res[i][j].num_words / avdl))
                        result[-1][1] += math.log(((N - docs[docs.index(ql_res[i][j].query_find) + 1] + 0.5) /
                                                  (docs[docs.index(ql_res[i][j].query_find) + 1] + 0.5))) * (((k1 + 1) *
                                                  len(ql_res[i][j].query_terms)) / (K + len(ql_res[i][j].query_terms))) \
                                                    * (((k2 + 1) * occurence[occurence.index(ql_res[i][j].query_find) + 1]) /
                                                     (k2 + occurence[occurence.index(ql_res[i][j].query_find) + 1]))
                result = sorted(result, key=lambda x: x[0].query_name)
                result = sorted(result, key=lambda x: x[1], reverse=True)
                for i in range(len(result)):
                    result[i][1] = round(result[i][1], 4)
                if os.path.exists(outputFile):
                    print_res(result, info, outputFile, 'a')
                else:
                    print_res(result, info, outputFile, 'w+')
            if info[0] == 'ql':
                for i in range(1, len(ql_res), 2):
                    result.append([ql_res[i][0], 0])
                    temp = copy.deepcopy(tf)
                    mew = 300
                    doc_words = ql_res[i][0].num_words
                    for j in range(len(ql_res[i])):
                        result[-1][1] += math.log((len(ql_res[i][j].query_terms) + mew *
                                (tf[tf.index(ql_res[i][j].query_find) + 1] / collection_size)) / (doc_words + mew))
                        if ql_res[i][j].query_find in temp:
                            ind = temp.index(ql_res[i][j].query_find) + 1
                            temp.pop(ind)
                            temp.remove(ql_res[i][j].query_find)
                    if len(temp) != 0:
                        for j in range(1, len(temp), 2):
                            result[-1][1] += math.log((0 + mew * (temp[j] / collection_size)) / (doc_words + mew))
                result = sorted(result, key=lambda x: x[0].query_name)
                result = sorted(result, key=lambda x: x[1], reverse=True)
                for i in range(len(result)):
                    result[i][1] = round(result[i][1], 4)
                if os.path.exists(outputFile):
                    print_res(result, info, outputFile, 'a')
                else:
                    print_res(result, info, outputFile, 'w+')
    return

#def check_res(outputFile):
#    data1 = []
#    data2 = []
#    with open("P3train1.trecrun", 'r') as f:
#        for line in f:
#            data1.append(line.split())
#    with open(outputFile, 'r') as f:
#        for line in f:
#            data2.append((line.split()))
#    for i in range(len(data1)):
#        for j in range(len(data1[i]) - 1):
#            if data1[i][j] != data2[i][j]:
#                print("True " + f"{data1[i]}")
#                print("False " + f"{data2[i]}")

if __name__ == '__main__':
    # Read arguments from command line, or use sane defaults for IDE.
    argv_len = len(sys.argv)
    inputFile = sys.argv[1] if argv_len >= 2 else "sciam.json.gz"
    queriesFile = sys.argv[2] if argv_len >= 3 else "P3train.tsv"
    outputFile = sys.argv[3] if argv_len >= 4 else "P3train.trecrun"
    if queriesFile == 'showIndex':
        a = 1
    elif queriesFile == 'showTerms':
        a = 1
    else:
        runQueries(inputFile, queriesFile, outputFile)
#        check_res(outputFile)
    # Feel free to change anything
