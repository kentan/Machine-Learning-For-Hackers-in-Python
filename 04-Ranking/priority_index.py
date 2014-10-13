
import os
import math
import re
import datetime
from simple_term_document_matrix import SimpleTermDocumentMatrix
import dateutil.tz
import dateutil.parser



ham_data_dir_path = "./ML_for_Hackers-master/03-Classification/data/easy_ham/"

DEFAULT = datetime.datetime(2000, 1, 1, 1, 1, 1,tzinfo=dateutil.tz.tzoffset('UTC', -0))

class Thread:
    def __init__(self):
        self.subject = ""
        self.oldest = datetime.datetime.today().replace(year=1969)
        self.newest = datetime.datetime.today()
        self.sender_freq = {}
        self.thread_freq = 0

    def set_oldest(self,oldest):
        self.oldest = oldest

    def set_newest(self,newest):
        self.newest = newest

    def increment_freq(self,sender):
        self.thread_freq += 1
        self.sender_freq[sender] = self.sender_freq[sender] + 1 if self.sender_freq.has_key(sender) else 1

    def update_date(self,date_):

        if date_ > self.newest:
            self.newest = date_
        if date_ < self.oldest:
            self.oldest = date_


    def set_subject(self,subject):
        self.set_subject = subject

    def get_weight(self):
        span = (self.newest - self.oldest).total_seconds()
        if span == 0:
            return 1
        else:

            weight = math.log10(self.thread_freq/span ) + 10
            return weight

    def get_sender_weight(self,sender):
        if self.sender_freq.has_key(sender):
            return math.log10(self.sender_freq[sender] + 1)
        else:
            return 1

class PriorityTrainer:
    def calc_weight_on_thread(self,subject,sender,date_,threads):
        subject_lower = subject.lower()
        s = subject_lower.split("re:")
        if len(s) >= 2:
            if threads.has_key(subject_lower):
                t = threads[subject_lower]
                t.increment_freq(sender)
                t.update_date(date_)
            else:
                t = Thread()
                t.set_subject(subject_lower)
                t.set_newest(date_)
                t.set_oldest(date_)

                threads[subject_lower] = t


    def calc_sender_freq(self,sender,senders_map):
        senders_map[sender] = senders_map[sender] + 1 if senders_map.has_key(sender) else 1


    def train(self,files):


        senders_map = {}
        threads = {}
        tdm = SimpleTermDocumentMatrix()

        for f in files:

            l = parse_email(f)
            sender = l[0]
            subject = l[1]
            date_ = l[2]
            body = l[3]

            tdm.add_doc(body)
            self.calc_sender_freq(sender,senders_map)
            self.calc_weight_on_thread(subject,sender,date_,threads)

        self.senders_freq = senders_map
        self.threads_weight = threads
        self.tdm = tdm

    def get_sender_rank(self,sender):
        if self.senders_freq.has_key(sender):
            return math.log10(1 + self.senders_freq[sender])
        else:
            return 1

    def get_thread_sender_rank(self,sender,subject):
        if self.threads_weight.has_key(subject):
            return self.threads_weight[subject].get_sender_weight(sender)
        else:
            return 1

    def get_thread_activity(self,subject):
        if self.threads_weight.has_key(subject):
            return self.threads_weight[subject].get_weight()
        else:
            return 1

    def get_thread_term_weight(self,subject):
        for punctuation in SimpleTermDocumentMatrix.punctuations1:
            subject = subject.replace(punctuation," ")

        terms = subject.split(" ")
        terms = [v.lower() for v in terms if v != ""]
        s = 0
        count = 0
        for subject_in_thread in self.threads_weight:
            for term in terms:
                if re.search(term,subject_in_thread):
                    s += self.threads_weight[subject_in_thread].get_weight()
                    count += 1

        mean = s/count if count > 0 else 1
        return mean

    def get_message_weight(self,body):
        body_tdm = SimpleTermDocumentMatrix()
        body_tdm.add_doc(body)
        body_terms = body_tdm.get_terms(min_doc_freq=1)

        tm = self.tdm.get_term_freq()

        for body_term in body_terms:
            tm_log10 = [math.log10(tm[k]) for k in tm if body_term == k]

        mean =  sum(tm_log10)/len(tm_log10) if len(tm_log10) > 0 else 1
        return mean


def parse_email(email_path):
    lines = [line.strip() for line in open(email_path)]

    body = ""
    sender = ""
    only_newline_found = False
    subject = ""
    date_ = ""
    for l in lines:
        if only_newline_found:
            body = body + " " + l
        elif l == "":
            only_newline_found = True
        elif "From: " in l:
            try:
                sender = re.split(r"[ :<>()]",l)
                sender = [v for v in sender if "@" in v]
                sender = sender[0]
            except IndexError:
                sender = ""
        elif "Subject: " in l:
            subject = l
        elif "Date: " in l:

            date_ = l.split("Date: ")[1]
            date_ = dateutil.parser.parse(date_,default=DEFAULT)

    if sender == "":
        return None
    else:
        return (sender,subject,date_,body)


def get_ranking(email_path,trainer):

    email = parse_email(email_path)

    if email == None:
        return None

    sender = email[0]
    subject = email[1].lower()
    received_date = email[2]
    body = email[3]


    sender_rank = trainer.get_sender_rank(sender)
    thread_sender_rank = trainer.get_thread_sender_rank(sender,subject)
    activity = trainer.get_thread_activity(subject)
    thread_weight = trainer.get_thread_term_weight(subject)
    term_weight = trainer.get_message_weight(body)
    rank_data = [sender_rank,thread_sender_rank,activity,thread_weight,term_weight]
    rank = reduce(lambda x,y: x*y,rank_data)
    return [received_date.ctime(),sender,subject,rank]

def run():
    train_data = []
    test_data = []

    if os.path.isdir(ham_data_dir_path):
        count = 1250
        for f in os.listdir(ham_data_dir_path):
            count -= 1
            if count >= 0:
                train_data.append(ham_data_dir_path + "/" + f)
            else:
                test_data.append(ham_data_dir_path + "/" + f)


    trainer = PriorityTrainer()
    trainer.train(train_data)

    count = 0
    for test_datum in test_data:
        rank = get_ranking(test_datum,trainer)
        if not rank == None :print rank

run()
