#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Feb 16 20:31:44 2018

@author: josharnold
"""

from keras.models import Model
from keras.layers import Input, LSTM, Dense, Concatenate
from keras.callbacks import History, ReduceLROnPlateau
from keras.optimizers import Adam
import numpy as np
from model.data import preprocessing
from matplotlib import pyplot as plt
import os, pickle

from rdkit import Chem
from chem import molecule

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
            target = preprocessing.process_smiles(target)            
            for i in range(0, len(target)):
                self.X_test[i] = target[i]
                        
        x_latent = self.smiles_to_latent_model.predict(self.X_test)
            
        molecules = []
        smiles_arr = []
        
        for i in range(0, len(target)-1):  
            latent1 = x_latent[i:i+1] 
            latent0 = x_latent[i+2:i+3]        
            for r in ratios:
                rlatent = (1.0-r)*latent0 + r*latent1            
                smiles  = self.latent_to_smiles(rlatent)
                mol = Chem.MolFromSmiles(smiles)
                if mol and ((smiles in smiles_arr) == False):
                    print(smiles)
                    molecules.append(molecule(smiles))  
                    smiles_arr.append(smiles)       
                                          
        return molecules    
    
    def save(self, force_overwrite=False):        
        if force_overwrite == False:
            if os.path.exists("weights.h5"):
                print("Uh oh. Path to model weights already exists :(")
                return
            
        self.model.save_weights("weights.h5")
        
        with open('char_to_int.pkl', 'wb') as path:
            pickle.dump(preprocessing.char_to_int, path)
            
        with open('int_to_char.pkl', 'wb') as path:
            pickle.dump(preprocessing.int_to_char, path)
        
        print("Saved model to file.")
        return
    
    def predict(self, num=10):
        for i in range(num):
            v = self.model.predict([self.X_test[i:i+1], self.X_test[i:i+1]]) #Can't be done as output not necessarely 1
            idxs = np.argmax(v, axis=2)
            pred=  "".join([preprocessing.int_to_char[h] for h in idxs[0]])[:-1]
            idxs2 = np.argmax(self.X_test[i:i+1], axis=2)
            true =  "".join([preprocessing.int_to_char[k] for k in idxs2[0]])[1:]
            print(true, pred)
        return
    
    def train(self, show_loss=True):
        h = History()
        rlr = ReduceLROnPlateau(monitor='val_loss', factor=0.5,patience=10, min_lr=0.000001, verbose=1, epsilon=1e-5)
        
        opt=Adam(lr=0.005) 
        
        self.model.compile(optimizer=opt, loss='categorical_crossentropy')
        self.model.fit([self.X_train, self.X_train], self.y_train,
                  epochs=self.num_epochs, batch_size=self.batch_size,
                  shuffle=True, callbacks=[h, rlr],
                  validation_data=[[self.X_test, self.X_test], self.y_test])     
        
        if (show_loss == True):
            # Show graph
            plt.plot(h.history["loss"], label="Loss")
            plt.plot(h.history["val_loss"], label="Val_Loss")
            plt.yscale("log")
            plt.legend()
            plt.show()        
        return 
