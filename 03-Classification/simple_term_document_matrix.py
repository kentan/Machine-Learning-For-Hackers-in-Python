import re

class SimpleTermDocumentMatrix:
    punctuations1 = [".","?","!",":",";","-","/","'","\"","[","]","(",")","<",">","=","%","*","+","\\"]
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

    def get_term_freq(self):
        freq = {}
        for term in self.term_doc_matrix.keys():
            freq[term] = len(self.term_doc_matrix[term])

        return freq

    def get_matrix(self):
        return self.term_doc_matrix
