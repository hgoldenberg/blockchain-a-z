#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Oct 17 15:13:31 2021

@author: hernangoldenberg
"""
# Modulo 1 - Crear una blockchain
# Flask==0.12.2 : pip install Flask==0.12.2
# Cliente HTTP Postman: hhtps://www.getpostman.com/

# Importar las librerias

import datetime
import hashlib
import json
from flask import Flask, jsonify


# Parte 1 - Crear la Blockchain

class Blockchain:
    
    def __init__(self):
        
        self.chain = []
        self.create_block (proof = 1, previous_hash = '0')
        
    def create_block(self, proof, previous_hash):
        block = {'index': len(self.chain) + 1,
                 'timestamp': str(datetime.datetime.now()),
                 'proof': proof,
                 'previous_hash': previous_hash}
        self.chain.append(block)
        return block
        

# Parte 2 - Minado de un Blockchain