__author__ = 'kentan'


import os
import math
import re
from simple_term_document_matrix import SimpleTermDocumentMatrix

spam_data_dir_path = "./ML_for_Hackers-master 2/03-Classification/data/spam/"
ham_data_dir_path = "./ML_for_Hackers-master 2/03-Classification/data/easy_ham/"
target_data_dir_path = "./ML_for_Hackers-master 2/03-Classification/data/hard_ham/"


def get_body(email_path):
    lines = [line.strip() for line in open(email_path)]

    body = ""
    only_newline_found = False

    for l in lines:
        if only_newline_found:
            body = body + " " + l
        elif l == "":
            only_newline_found = True

    return body


def get_tdm(email_path) :

    if os.path.isdir(email_path):
        files = [ email_path + "/" + f for f in os.listdir(email_path) if os.path.isfile(os.path.join(email_path,f))]
    else:
        files = [email_path]
    tdm = SimpleTermDocumentMatrix()

    for f in files:
        body = get_body(f)
        tdm.add_doc(body)

    return tdm

def get_intersect(target1,target2):
    return list(set(target1) & set(target2))


def get_doc_prob(prob,target_term,common_term):
    prior = 0.5
    c = 0.000001
    if len(common_term) == 0:
        return math.log10(prior) + len(target_term) * math.log10(c)

    else:
        p = sum([math.log10(prob[t]) for t in common_term])
        return math.log10(prior) + p + (len(target_term) - len(common_term)) * math.log10(c)


def email_classify():
    spam_tdm = get_tdm(spam_data_dir_path)
    ham_tdm = get_tdm(ham_data_dir_path)

    spam_occurrence =  spam_tdm.get_term_prob()
    ham_occurrence =  ham_tdm.get_term_prob()


    target_files = [ target_data_dir_path + "/" + f for f in os.listdir(target_data_dir_path) if os.path.isfile(os.path.join(target_data_dir_path,f))]

    result = []

    for target_file in target_files:

        target_tdm = get_tdm(target_file)
        spam_and_target_common_term = get_intersect(spam_tdm.get_terms(),target_tdm.get_terms(1))

        ham_and_target_common_term = get_intersect(ham_tdm.get_terms(),target_tdm.get_terms(1))

        spam_expectation =  get_doc_prob(spam_occurrence,target_tdm.get_terms(),spam_and_target_common_term)
        ham_expectation =  get_doc_prob(ham_occurrence,target_tdm.get_terms(),ham_and_target_common_term)


        result.append(spam_expectation > ham_expectation)

    spam = 0
    ham = 0
    for t in result:
        if t:
            spam += 1
        else:
            ham += 1

    print spam,ham

email_classify()

