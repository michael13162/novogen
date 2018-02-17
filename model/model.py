#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:31:44 2018

@author: josharnold
"""

from keras.models import Model
from keras.layers import Input, LSTM, Dense, Concatenate
#from keras.callbacks import History, ReduceLROnPlateau
from keras.optimizers import Adam
import numpy as np
from model.data import preprocessing
#from matplotlib import pyplot as plt
#import os, pickle

from rdkit import Chem
from model.chem import molecule

class nn:
    def __init__(self, X_train, y_train, X_test, y_test):
        self.num_epochs = 200
        self.batch_size = 256
        self.X_train = X_train
        self.y_train = y_train
        self.X_test = X_test
        self.y_test = y_test
        
        #create model
        self.create_model()
        
        return
    
    def create_model(self):
        self.input_shape = self.X_train.shape[1:]
        self.output_dim = self.y_train.shape[-1]
        self.latent_dim = 64
        self.lstm_dim = 64        
        self.unroll = False
        
        self.encoder_inputs = Input(shape=self.input_shape)
        encoder = LSTM(self.lstm_dim, return_state=True, unroll=self.unroll)        
        encoder_outputs, state_h, state_c = encoder(self.encoder_inputs)
        
        states = Concatenate(axis=-1)([state_h, state_c])
        neck = Dense(self.latent_dim, activation="relu")
        self.neck_outputs = neck(states)

        self.decode_h = Dense(self.lstm_dim, activation="relu")
        self.decode_c = Dense(self.lstm_dim, activation="relu")
        state_h_decoded =  self.decode_h(self.neck_outputs)
        state_c_decoded =  self.decode_c(self.neck_outputs)
        encoder_states = [state_h_decoded, state_c_decoded]
        decoder_inputs = Input(shape=self.input_shape)
        decoder_lstm = LSTM(self.lstm_dim, return_sequences=True, unroll=self.unroll)

        decoder_outputs = decoder_lstm(decoder_inputs, initial_state=encoder_states)
        decoder_dense = Dense(self.output_dim, activation='softmax')
        decoder_outputs = decoder_dense(decoder_outputs)

        self.model = Model([self.encoder_inputs, decoder_inputs], decoder_outputs)
        return
    
    def create_encoder_and_decoder(self):     
        # Create encoder
        self.smiles_to_latent_model = Model(self.encoder_inputs, self.neck_outputs)
        
        # Create state model
        latent_input = Input(shape=(self.latent_dim,))
        state_h_decoded_2 =  self.decode_h(latent_input)
        state_c_decoded_2 =  self.decode_c(latent_input)
        self.latent_to_states_model = Model(latent_input, [state_h_decoded_2, state_c_decoded_2])
        
        # Create decoder
        inf_decoder_inputs = Input(batch_shape=(1, 1, self.input_shape[1]))
        inf_decoder_lstm = LSTM(self.lstm_dim, return_sequences=True, unroll=self.unroll, stateful=True)
        inf_decoder_outputs = inf_decoder_lstm(inf_decoder_inputs)
        inf_decoder_dense = Dense(self.output_dim, activation='softmax')
        inf_decoder_outputs = inf_decoder_dense(inf_decoder_outputs)
        self.decoder = Model(inf_decoder_inputs, inf_decoder_outputs)
        
        #Transfer Weights
        for i in range(1,3):
            self.decoder.layers[i].set_weights(self.model.layers[i+6].get_weights())
        return
    
    def load(self):             
        preprocessing.load_charset() # Reload charset just incase
        self.model.load_weights("weights.h5") # Load weights
        self.model.compile(optimizer=Adam(lr=0.005), loss='categorical_crossentropy') # Compile model   
        self.create_encoder_and_decoder() # Create encoder / decoder 
        print("Loaded model from file.")
        return
    
    def latent_to_smiles(self, latent):
        states = self.latent_to_states_model.predict(latent)
        self.decoder.layers[1].reset_states(states=[states[0],states[1]])

        startidx = preprocessing.char_to_int["!"]
        samplevec = np.zeros((1,1,22))
        samplevec[0,0,startidx] = 1
        smiles = ""
        for i in range(50):
            o = self.decoder.predict(samplevec)
            sampleidx = np.argmax(o)
            samplechar = preprocessing.int_to_char[sampleidx]
            if samplechar != "E":
                smiles = smiles + preprocessing.int_to_char[sampleidx]
                samplevec = np.zeros((1,1,22))
                samplevec[0,0,sampleidx] = 1
            else:
                break
        return smiles
    
    def generate(self, target=[], ratios=np.linspace(0,3,500)):
        if target != []:
            target = preprocessing.process_smiles(['NC=NC1CN1CO', 'CC1=CNCN2CC12'])            
            for i in range(0, len(target)):
                self.X_test[i] = target[i]
                        
        x_latent = self.smiles_to_latent_model.predict(self.X_test)
            
        # interpolate from first two
        latent1 = x_latent[0:1] 
        latent0 = x_latent[2:3]
        
        molecules = []
        smiles_arr = []
        
        # Ratio to determine randomness        
        for r in ratios:
            rlatent = (1.0-r)*latent0 + r*latent1            
            smiles  = self.latent_to_smiles(rlatent)
            mol = Chem.MolFromSmiles(smiles)
            if mol and ((smiles in smiles_arr) == False):
                print(smiles)
                molecules.append(molecule(smiles))  
                smiles_arr.append(smiles)       
                                          
        return molecules