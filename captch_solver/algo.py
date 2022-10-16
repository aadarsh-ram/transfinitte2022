import time
import pickle
from unicodedata import name


class ALGO:

    def __init__(self, file, epic):
    
        self.deets = pickle.load(open(file, "rb"))


        self.initial_id= epic
        self.initial_dict = self.deets[self.initial_id]

        self.deets_new = {}

        for i in self.deets:
            if(self.deets[i]['house_no']==self.initial_dict['house_no']):
                self.deets_new[i]=self.deets[i]

        self.deets = self.deets_new.copy()

        self.created={}

    def create_node(self,di):
        new_dict={}
        new_dict['info'] = di.copy()
        new_dict['children'] = []
        new_dict['spouse']=""
        new_dict['parents']=[]
        new_dict['same']=[]
        self.created[di['uniqueid']] = new_dict.copy()

    def cons_same(self,node):
        gender=(self.created[node]['info']['gender'])
        if(gender=='M' or (self.created[node]['info']['uniqueid']==self.initial_dict['uniqueid'] and self.created[node]['info']['father/husband']=='F')):
            for i in self.deets:
                if(self.deets[i]['father/husband'][0]==self.deets[node]['father/husband'][0] and i!=node and i not in self.created[node]['same']):
                    self.created[node]['same'].append(i)

    def find_spouse(self, node):
        gender=(self.created[node]['info']['gender'])
        if(gender=='F' and self.deets[node]['father/husband'][1]=='H'):
            for i in self.deets:
                if(self.deets[node]['father/husband'][0]==self.deets[i]['name']):
                    self.created[node]['spouse']=i
        else:
            for i in self.deets:
                if(self.deets[i]['father/husband'][0]==self.deets[node]['name'] and self.deets[i]['father/husband'][1]=='H'):
                    self.created[node]['spouse']=i

    def get_children(self,node):
        gender=(self.created[node]['info']['gender'])
        if(gender=='M'):
            for i in self.deets:
                if(self.deets[i]['father/husband'][1]=='F' and self.deets[i]['father/husband'][0]==self.deets[node]['name'] and i not in created[node]['children']):
                    self.created[node]['children'].append(i)

    def get_parents(self, node):
        if(self.deets[node]['father/husband'][1]=='F'):
            for i in self.deets:
                if(self.deets[i]['name']==self.deets[node]['father/husband'][0] and i not in self.created[node]['parents']):
                    self.created[node]['parents'].append(i)


    def caller(self,last_created):
        for i in self.created[last_created]['children']:
            if(self.created.get(i,0)==0):
                self.create_node(self.deets[i])
                self.cons_same(i)
                self.find_spouse(i)
                self.get_children(i)
                self.get_parents(i)
                self.caller(i)
        for i in self.created[last_created]['parents']:
            if(self.created.get(i,0)==0):
                self.create_node(self.deets[i])
                self.cons_same(i)
                self.find_spouse(i)
                self.get_children(i)
                self.get_parents(i)
                self.caller(i)

        for i in self.created[last_created]['same']:
            if(self.created.get(i,0)==0):
                self.create_node(self.deets[i])
                self.cons_same(i)
                self.find_spouse(i)
                self.get_children(i)
                self.get_parents(i)
                self.caller(i)

        if(self.created[last_created]['spouse']!="" and self.created.get(self.created[last_created]['spouse'],0)==0):
            self.create_node(self.deets[self.created[last_created]['spouse']])
            self.cons_same(self.created[last_created]['spouse'])
            self.find_spouse(self.created[last_created]['spouse'])
            self.get_children(self.created[last_created]['spouse'])
            self.get_parents(self.created[last_created]['spouse'])
            self.caller(self.created[last_created]['spouse'])



    def genTree(self):
        self.create_node(self.initial_dict)
        self.cons_same(self.initial_id)
        self.find_spouse(self.initial_id)
        self.get_children(self.initial_id)
        self.get_parents(self.initial_id)
        self.caller(self.initial_id)
        for i in self.created:
            if(self.created[i]['info']['gender']=='F' and self.created[i]['spouse']!=""):
                self.created[i]['children'] = self.created[self.created[i]['spouse']]['children']