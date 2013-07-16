#!/usr/bin/python
# -*- coding: utf-8 -*-

##
#
#
# @author Yuan Jin
# @contact jinyuan@baidu.com
# @created Sept. 24, 2012
# @updated Sept. 25, 2012
#

import sys
reload(sys)
sys.setdefaultencoding('UTF-8')

from AlchemyApiCat import AlchemyApiCategory
from FreebaseAPI import FreebaseAPI
from srquery import Query
from srontoapi import SearchetOntology
import srontoapi
import srentity
import threading


class TagAlchemyAPI(threading.Thread):
    def __init__(self, keyword=None):
        threading.Thread.__init__(self)
        self.alchemy_api = AlchemyApiCategory(keyword)
        self.result = [] # highly possibly several of them

    def run(self):
        self.result = self.alchemy_api.get_types()

class TagBaidu(threading.Thread):
    pass

class TagFreebase(threading.Thread):
    def __init__(self, keyword=None):
        threading.Thread.__init__(self)
        self.freebase_api = FreebaseAPI(keyword)
        self.result = []

    def run(self):
        self.result = self.freebase_api.get_types()

class QueryTagger:
    ''' docs '''
    # TODO
    # 1. download freebase
    # 2. segment query
    # 3. find multiple entities from local freebase

    def __init__(self, query=None):
        self.query = Query(query)

        # instance of searchet-ontology-api
        self.searchet_ontology = SearchetOntology(source='searchet_v2.n3', format='n3')

    def get_types(self):
        '''docs'''
        ta = TagAlchemyAPI(self.query.query)
        # baidu ner should be trusted as the major source
        #tb = TagBaidu(self.query)

        # definitely problems arises if querying freebase this way
        # 
        tf = TagFreebase(self.query.query)

        ta.start()
        #tb.start()
        tf.start()

        # wait until all three finish, or two seconds
        ta.join(2*1000)
        #tb.join(2*2000)
        tf.join(2*2000)

        return ta.result, tf.result
        #return ta.result, tb.result, tf.result

    def pattern_generator(self, query):
        '''simple strategy, subject to further changes'''
        pass

    def analyze_alchemyapi(self, entities):
        '''find out 1.the ancestor 2.the corresponding text 3.update query'''
        # the alchemyapi Query instance
        query = Query(self.query.query)
        
        query.feature_words = query.query
        query.pattern = query.query

        for e in entities:
            ancestor = self.searchet_ontology.get_pedigree('http://www.alchemyapi.com/api/entity/types.html#', e.entity_type)
            text = e.entity_text
            query.token_entities[text] = ancestor
            query.entity_tokens[ancestor] = text
            
            query.pattern = query.pattern.replace(text, str(ancestor))
            query.feature_words = query.feature_words.replace(text, "")
        
        # feature words
        query.feature_words = [t.strip().lower().capitalize() for t in query.feature_words.split() if t]
        query.pattern = [p.strip() for p in query.pattern.split() if p]

        return query

    def analyze_baidu(self):
        '''docs'''
        pass

    def analyze_freebase(self, entity):
        '''docs'''
        # the freebase Query instance
        query = Query(self.query.query)

        query.feature_words = query.query
        query.pattern = query.query

        ancestors = []
        for t in entity.entity_type:
            ancestor = self.searchet_ontology.get_pedigree('http://schemas.freebaseapps.com/type?id=', t)
            ancestors.append(ancestor)
        # dedup
        ancestors = list(set(ancestors))

        #special treatment for entity text
        text = ''
        for t in entity.entity_text:
            if t in query.query.lower():
                low = query.query.lower().find(t)
                high = len(t) + 1
                text = query.query[low:high]
                break
        if text:
            query.token_entities[text] = ancestors

            for ancestor in ancestors:
                query.entity_tokens[ancestor] = text

            query.feature_words = query.feature_words.replace(text, "")

        query.feature_words = [t.lower().strip().capitalize() for t in query.feature_words.split() if t]

        if any(ancestors):
            query.pattern = query.pattern.replace(text, '|'.join(ancestors))
            query.pattern = [p.strip() for p in query.pattern if p]

        return query

    #def analyze(alchemyapi_entities, baidu_entities, freebase_entity):
    def analyze(self, alchemyapi_entities, freebase_entity):
        '''each service tags by itself'''
        alchemyapi_tagged_query = self.analyze_alchemyapi(alchemyapi_entities)
        #baidu_tagged_query = analyze_baidu(baidu_entities)
        freebase_tagged_query = self.analyze_freebase(freebase_entity)

        # currently simple stratege:
        # if different, baidu > alchemyapi > freebase
        if alchemyapi_tagged_query.pattern != freebase_tagged_query.pattern:
            return alchemyapi_tagged_query
        else:
            return freebase_tagged_query

    def tag(self):
        ''' docs '''
        alchemyapi_entities, freebase_entity = self.get_types()
        #alchemyapi_entities, baidu_entities, freebase_entity = self.get_types()
        
        return self.analyze(alchemyapi_entities, freebase_entity)
        #return analyze(alchemyapi_entities, baidu_entities, freebase_entity)

if __name__=='__main__':
    client = QueryTagger('flight beijing boston')
    print client.tag()