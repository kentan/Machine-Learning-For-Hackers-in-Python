__author__ = 'kentan'


import os
import math
import re

spam_data_dir_path = "./ML_for_Hackers-master 2/03-Classification/data/spam/"
ham_data_dir_path = "./ML_for_Hackers-master 2/03-Classification/data/easy_ham/"
target_data_dir_path = "./ML_for_Hackers-master 2/03-Classification/data/hard_ham/"


class SimpleTermDocumentMatrix:
    punctuations1 = [".","?","!",":",";","-","/","'","\"","[","]","(",")","<",">","=","%"]
    punctuations2 = [r'\[.*?\]',r'\(.*?\)',r'\<.*?\>']
    stopwords =["i","me","my","myself","we","our","ours","ourselves","you","your",
                "yours","yourself","yourselves","he","him","his","himself","she","her","hers",
                "herself","it","its","itself","they","them","their","theirs","themselves","what",
                "which","who","whom","this","that","these","those","am","is","are",
                "was","were","be","been","being","have","has","had","having","do",
                "does","did","doing","would","should","could","ought","i'm","you're","he's",
                "she's","it's","we're","they're","i've","you've","we've","they've","i'd","you'd",
                "he'd","she'd","we'd","they'd","i'll","you'll","he'll","she'll","we'll","they'll",
                "isn't","aren't","wasn't","weren't","hasn't","haven't","hadn't","doesn't","don't","didn't",
                "won't","wouldn't","shan't","shouldn't","can't","cannot","couldn't","mustn't","let's","that's",
                "who's","what's","here's","there's","when's","where's","why's","how's","a","an",
                "the","and","but","if","or","because","as","until","while","of",
                "at","by","for","with","about","against","between","into","through","during",
                "before","after","above","below","to","from","up","down","in","out",
                "on","off","over","under","again","further","then","once","here","there",
                "when","where","why","how","all","any","both","each","few","more",
                "most","other","some","such","no","nor","not","only","own","same",
                "so","than","too","very"]


    def __init__(self):
        self.doc_count = 0
        self.term_doc_matrix= {}

    def remove_punctuations(self,doc):
        for p in self.punctuations1:
            doc = doc.replace(p," ")

        return doc

    def remove_stopwords(self,terms):
        terms2 = terms
        for s in self.stopwords:
            terms2 = [t for t in terms2 if t.lower() != s]

        return terms2

    def remove_numbers(self,terms):
        return [t for t in terms if re.match(r"^\d+",t) == None]

    def add_doc(self,doc):
        doc = self.remove_punctuations(doc)

        terms = re.split(r"\s+",doc)
        terms = self.remove_stopwords(terms)
        terms = self.remove_numbers(terms)

        for term in terms:
            term = term.lower()
            v = {}
            try:
                v = self.term_doc_matrix[term]
            except KeyError:
                t = {}
                t[self.doc_count] = 1
                self.term_doc_matrix[term] = t
            try:
                v[self.doc_count] = v[self.doc_count] + 1
            except KeyError:
                v[self.doc_count] = 0

        self.doc_count += 1



    def get_terms(self,min_doc_freq=2):
        if min_doc_freq == 0:
            return self.term_doc_matrix.keys()
        else:
            return {k for k in self.term_doc_matrix if len(self.term_doc_matrix[k]) >= min_doc_freq}

    def get_term_count(self):
        return len(self.term_doc_matrix)

    def get_term_prob(self):
        prob = {}
        for term in self.term_doc_matrix.keys():
            prob[term] = float(len(self.term_doc_matrix[term]))/float(self.doc_count)

        return prob

    def get_matrix(self):
        return self.term_doc_matrix

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

