# import package ...
import math
import sys
qrels = []
query_rel = []


def handle_qrels(f):
    for line in f:
        cur_arr = line.strip().split()
        if cur_arr[0] in qrels:
            for i in range(len(qrels[qrels.index(cur_arr[0]) + 2])):
                if int(cur_arr[3]) == qrels[qrels.index(cur_arr[0]) + 2][i] or int(cur_arr[3]) > \
                        qrels[qrels.index(cur_arr[0]) + 2][i]:
                    qrels[qrels.index(cur_arr[0]) + 2].insert(i, int(cur_arr[3]))
                    qrels[qrels.index(cur_arr[0]) + 1].insert(i, cur_arr[2])
                    break
                elif i == len(qrels[qrels.index(cur_arr[0]) + 2]) - 1:
                    qrels[qrels.index(cur_arr[0]) + 2].insert(i + 1, int(cur_arr[3]))
                    qrels[qrels.index(cur_arr[0]) + 1].insert(i + 1, cur_arr[2])
                    break
            if int(cur_arr[3]) > 0:
                query_rel[query_rel.index(cur_arr[0]) + 1] += 1
        else:
            qrels.append(cur_arr[0])
            qrels.append([cur_arr[2]])
            qrels.append([int(cur_arr[3])])
            query_rel.append(cur_arr[0])
            if int(cur_arr[3]) > 0:
                query_rel.append(1)
            else:
                query_rel.append(0)
    return


def write_to_output(query, NDCG, rel_found, reciprocal_rank, recall, precision, prec_at_20, ap, output):
    with open(output, 'a') as f:
        IDCG = 0
        for i in range(20):
            if i == 0:
                IDCG += qrels[qrels.index(query) + 2][i]
            else:
                IDCG += qrels[qrels.index(query) + 2][i] / math.log(i + 1, 2)
        space = ''
        for i in range(len(query), 9):
            space += " "
        if query_rel[query_rel.index(query) + 1] == 0:
            f.write("NDCG@20  " + query + space + '0.0000' + '\n')
        else:
            f.write("NDCG@20  " + query + space + "{:.4f}".format(NDCG[19] / IDCG, 4) + '\n')
        f.write("numRel   " + query + space + str(query_rel[query_rel.index(query) + 1]) + '\n')
        f.write("relFound " + query + space + str(rel_found) + '\n')
        f.write("RR       " + query + space + "{:.4f}".format(reciprocal_rank) + '\n')
        f.write("P@10     " + query + space + "{:.4f}".format(precision[9]) + '\n')
        f.write("R@10     " + query + space + "{:.4f}".format(recall[9]) + '\n')
        if recall[9] ==0 or precision[9] == 0:
            f.write("F1@10    " + query + space + "0.0000" + '\n')
        else:
            f.write("F1@10    " + query + space +
                    "{:.4f}".format((2 * recall[9] * precision[9]) / (recall[9] + precision[9])) + '\n')
        f.write("P@20%    " + query + space + "{:.4f}".format(prec_at_20) + '\n')
        aps = 0
        for i in ap:
            aps += i
        if query_rel[query_rel.index(query) + 1] == 0:
            f.write("AP       " + query + space + '0.0000' + '\n')
        else:
            f.write("AP       " + query + space + "{:.4f}".format(aps / query_rel[query_rel.index(query) + 1]) + '\n')
    return


def write_all(output):
    queries = 0
    all_NDCG = 0
    all_num_rel = 0
    all_rel_found = 0
    all_MRR = 0
    all_P = 0
    all_R = 0
    all_F1 = 0
    all_P20 = 0
    all_MAP = 0
    with open(output, 'r') as f:
        for line in f:
            cur_arr = line.strip().split()
            if cur_arr[0] == "NDCG@20":
                queries += 1
                all_NDCG += float(cur_arr[2])
            elif cur_arr[0] == "numRel":
                all_num_rel += int(cur_arr[2])
            elif cur_arr[0] == "relFound":
                all_rel_found += int(cur_arr[2])
            elif cur_arr[0] == "RR":
                all_MRR += float(cur_arr[2])
            elif cur_arr[0] == "P@10":
                all_P += float(cur_arr[2])
            elif cur_arr[0] == "R@10":
                all_R += float(cur_arr[2])
            elif cur_arr[0] == "F1@10":
                all_F1 += float(cur_arr[2])
            elif cur_arr[0] == "P@20%":
                all_P20 += float(cur_arr[2])
            elif cur_arr[0] == "AP":
                all_MAP += float(cur_arr[2])
    with open(output, 'a') as f1:
        f1.write("NDCG@20  " + "all      " + "{:.4f}".format(all_NDCG / queries) + '\n')
        f1.write("numRel   " + "all      " + str(all_num_rel) + '\n')
        f1.write("relFound " + "all      " + str(all_rel_found) + '\n')
        f1.write("MRR      " + "all      " + "{:.4f}".format(all_MRR / queries) + '\n')
        f1.write("P@10     " + "all      " + "{:.4f}".format(all_P / queries) + '\n')
        f1.write("R@10     " + "all      " + "{:.4f}".format(all_R / queries) + '\n')
        f1.write("F1@10    " + "all      " + "{:.4f}".format(all_F1 / queries) + '\n')
        f1.write("P@20%    " + "all      " + "{:.4f}".format(all_P20 / queries) + '\n')
        f1.write("MAP      " + "all      " + "{:.4f}".format(all_MAP / queries) + '\n')
    return


def eval(trecrunFile, qrelsFile, outputFile):
    with open(qrelsFile, 'r') as f:
        handle_qrels(f)
    query_eval = None
    query_NDCG = []
    precision_at_20 = 0
    query_rel_found = 0
    query_reciprocal_rank = 0
    query_recall = []
    query_precision = []
    AP = []
    with open(trecrunFile, 'r') as f:
        for line in f:
            cur_arr = line.strip().split()
            if query_eval is None or query_eval == cur_arr[0]:
                query_eval = cur_arr[0]
                if cur_arr[0] in qrels and cur_arr[2] in qrels[qrels.index(cur_arr[0]) + 1]:
                    rank = qrels[qrels.index(cur_arr[0]) + 2][qrels[qrels.index(cur_arr[0]) + 1].index(cur_arr[2])]
                else:
                    rank = 0
                if rank != 0:
                    query_rel_found += 1
                    if query_reciprocal_rank == 0:
                        query_reciprocal_rank = round(1 / int(cur_arr[3]), 4)
                if not query_NDCG:
                    query_NDCG.append(rank)
                else:
                    query_NDCG.append(rank / math.log(int(cur_arr[3]), 2) + query_NDCG[-1])
                if query_rel[query_rel.index(cur_arr[0]) + 1] == 0:
                    query_recall.append(0.0000)
                    query_precision.append(0.0000)
                else:
                    query_recall.append(round(query_rel_found / query_rel[query_rel.index(cur_arr[0]) + 1], 4))
                    query_precision.append(round(query_rel_found / int(cur_arr[3]), 4))
                if query_rel[query_rel.index(cur_arr[0]) + 1] != 0 and math.floor((query_rel_found / query_rel[query_rel.index(cur_arr[0]) + 1]) * 10) / 10 >= 0.2:
                    if query_precision[-1] > precision_at_20:
                        precision_at_20 = query_precision[-1]
                if (len(query_recall) == 1 and query_recall[0] > 0) or \
                        (len(query_recall) > 1 and query_recall[-1] > query_recall[-2]):
                    AP.append(round(query_precision[-1], 4))
            else:
                if query_eval == '330975':
                    print(query_recall)
                    print(query_precision)
                write_to_output(query_eval, query_NDCG, query_rel_found, query_reciprocal_rank, query_recall,
                                query_precision, precision_at_20, AP, outputFile)
                query_eval = cur_arr[0]
                query_NDCG = []
                query_rel_found = 0
                query_reciprocal_rank = 0
                query_recall = []
                query_precision = []
                precision_at_20 = 0
                AP =[]
                if cur_arr[0] in qrels and cur_arr[2] in qrels[qrels.index(cur_arr[0]) + 1]:
                    rank = qrels[qrels.index(cur_arr[0]) + 2][qrels[qrels.index(cur_arr[0]) + 1].index(cur_arr[2])]
                else:
                    rank = 0
                if rank != 0:
                    query_rel_found += 1
                    if query_reciprocal_rank == 0:
                        query_reciprocal_rank = round(1 / int(cur_arr[3]), 4)
                if not query_NDCG:
                    query_NDCG.append(rank)
                else:
                    query_NDCG.append(rank / math.log(int(cur_arr[3]), 2) + query_NDCG[-1])
                if query_rel[query_rel.index(cur_arr[0]) + 1] == 0:
                    query_recall.append(0.0000)
                    query_precision.append(0.0000)
                else:
                    query_recall.append(round(query_rel_found / query_rel[query_rel.index(cur_arr[0]) + 1], 4))
                    query_precision.append(round(query_rel_found / int(cur_arr[3]), 4))
                if query_rel[query_rel.index(cur_arr[0]) + 1] != 0 and math.floor((query_rel_found / query_rel[query_rel.index(cur_arr[0]) + 1]) * 10) / 10 >= 0.2:
                    if query_precision[-1] > precision_at_20:
                        precision_at_20 = query_precision[-1]
                if (len(query_recall) == 1 and query_recall[0] > 0) or \
                        (len(query_recall) > 1 and query_recall[-1] > query_recall[-2]):
                    AP.append(round(query_precision[-1], 4))
    write_to_output(query_eval, query_NDCG, query_rel_found, query_reciprocal_rank, query_recall,
                    query_precision, precision_at_20, AP, outputFile)
    write_all(outputFile)
    return


if __name__ == '__main__':
    argv_len = len(sys.argv)
    runFile = sys.argv[1] if argv_len >= 2 else "msmarcosmall-bm25.trecrun"
    qrelsFile = sys.argv[2] if argv_len >= 3 else "msmarco.qrels"
    outputFile = sys.argv[3] if argv_len >= 4 else "my-msmarcosmall-bm25.eval"

    eval(runFile, qrelsFile, outputFile)
    # Feel free to change anything here ...
