# -*- coding: utf-8 -*-
"""TFG - Orlando - CMAPSS.ipynb

authors: Orlando J. S. Béco and Carlos H. V. Moraes

Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1fDCI2zk4mOHVu01MFwWZHTh53vlkz-oI

# TFG Completo
"""

# LIBERAR DOWNLOAD NO CHROME
import time
from google.colab import files
files.download('/content/sample_data/README.md')
files.download('/content/sample_data/anscombe.json')

"""## Baixando Base"""

import gdown
#https://drive.google.com/file/d/1M5Bo2sdK99OqI3Z7BhSVS_gB3auMF1X6/view?usp=sharing
url = 'https://drive.google.com/uc?id=1M5Bo2sdK99OqI3Z7BhSVS_gB3auMF1X6'
output = 'N-CMAPSS_DS02-006.h5'
gdown.download(url, output, quiet=False)
filename = 'N-CMAPSS_DS02-006.h5'

"""## Leitura do Dataset"""

import h5py
import numpy as np
import pandas as pd

# Load data
with h5py.File(filename, 'r') as hdf:
  W = np.concatenate((
      np.array(hdf.get('W_dev')), 
      np.array(hdf.get('W_test')),
      ), axis=0)
  
  X_s = np.concatenate((
      np.array(hdf.get('X_s_dev')), 
      np.array(hdf.get('X_s_test')),
      ), axis=0)
  
  X_v = np.concatenate((
      np.array(hdf.get('X_v_dev')), 
      np.array(hdf.get('X_v_test')),
      ), axis=0)
  
  Y = np.concatenate((
      np.array(hdf.get('Y_dev')), 
      np.array(hdf.get('Y_test')),
      ), axis=0)

  #Nome das colunas
  W_var = np.array(hdf.get('W_var'))
  X_s_var = np.array(hdf.get('X_s_var'))  
  X_v_var = np.array(hdf.get('X_v_var')) 
  #corrigindo nomes
  W_var = list(np.array(W_var, dtype='U20'))
  X_s_var = list(np.array(X_s_var, dtype='U20'))  
  X_v_var = list(np.array(X_v_var, dtype='U20'))

#agrupando dados
data = np.concatenate((W, X_s, X_v, Y), axis=1)
columns = np.concatenate((W_var, X_s_var, X_v_var, ['RUL']), axis=0)

#eliminando da memória vetores não mais usados
del W, X_s, X_v, Y

#criando dataset final
ds = pd.DataFrame(data=data, columns=columns)

#eliminando da memória copia
del data, columns

#formato do dataset
ds.shape

ds.head()

## Treinamento

## Metodologias de Aprendizado Regressivo

regressores=[]
reg_nomes =[]

"""### Lineares"""

from sklearn import linear_model

regressores.append(linear_model.LinearRegression())
reg_nomes.append('LinearRegression')

regressores.append(linear_model.Ridge(alpha=1.0))
reg_nomes.append('Ridge')

regressores.append(linear_model.Lasso(alpha=0.1))
reg_nomes.append('Lasso')

regressores.append(linear_model.ElasticNet(random_state=42))
reg_nomes.append('ElasticNet')

#regressores.append(linear_model.LogisticRegression(random_state=42))
#reg_nomes.append('LogisticRegression')

"""### Não Lineares"""

from sklearn.kernel_ridge import KernelRidge
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.neural_network import MLPRegressor

#regressores.append(KernelRidge(alpha=1.0,kernel='rbf'))
#reg_nomes.append('KernelRidge')

#regressores.append(SVR(kernel='rbf'))
#reg_nomes.append('SVM-R')

#regressores.append(DecisionTreeRegressor(random_state=42,max_depth=10))
#reg_nomes.append('DecisionTreeRegressor')

regressores.append(MLPRegressor(
    random_state=42,
    hidden_layer_sizes=(100,),
    activation='relu',
    solver='adam',
    ))
reg_nomes.append('MLPRegressor')

"""## Métrica"""

from sklearn.metrics import max_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

"""## Pipeline"""

### Completa

X = ds[ds.columns[:-1]].values
y = ds[ds.columns[-1]].values
print(X.shape,y.shape)

### Base reduzida para Debug

#X = ds[ds.columns[:-1]].sample(n=1000000,random_state=42).values
#y = ds[ds.columns[-1]].sample(n=1000000,random_state=42).values
#print(X.shape,y.shape)

#X = ds[ds.columns[:-1]].sample(n=700000,random_state=42).values
#y = ds[ds.columns[-1]].sample(n=700000,random_state=42).values
#print(X.shape,y.shape)



"""### Treinamento"""

del ds

import time
from sklearn.model_selection import KFold

#https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html
num_partes = 5
kf = KFold(n_splits=num_partes, random_state=42, shuffle=True) # 10-Fold

resultados =[]
res_nomes = ['Técnica','Tempo(s)','ME','MAE','MSE','R2']

for nome, rgr in zip(reg_nomes, regressores):
  print('==',nome,'==')
  for train_index, test_index in kf.split(X):
    etapa = []
    etapa.append(nome)

    # dataset de treinamento(X_train,y_train)
    # dataset de testes(X_test,y_test)
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    #treinamento
    t = time.process_time()  
    rgr.fit(X_train,y_train)
    etapa.append(time.process_time()-t)
    
    #validacao
    y_prev = rgr.predict(X_test)

    #métricas
    etapa.append(max_error(y_test,y_prev))
    etapa.append(mean_absolute_error(y_test,y_prev))
    etapa.append(mean_squared_error(y_test,y_prev))
    etapa.append(r2_score(y_test,y_prev))

    print(etapa)

    resultados.append(etapa)
    #armazenando resultados
    res1 = pd.DataFrame(data = resultados, columns =res_nomes )
    # salva
    res1.to_excel('sem_pca.xlsx',index=True)

#armazenando resultados
res1 = pd.DataFrame(data = resultados, columns =res_nomes )
# salva
res1.to_excel('sem_pca.xlsx',index=True)

from google.colab import files
files.download('sem_pca.xlsx')

"""### Treinamento com pré-processamento"""

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

#limita escala dos atributos//colunas
scaler = StandardScaler()
X = scaler.fit_transform(X)

# decompoem informação de 33 atr. para 2 atr/col
pca = PCA(n_components=2)
X = pca.fit_transform(X)

import time
from sklearn.model_selection import KFold

#https://scikit-learn.org/stable/modules/generated/sklearn.model_selection.KFold.html
num_partes = 5
kf = KFold(n_splits=num_partes, random_state=42, shuffle=True) # 10-Fold

resultados =[]
res_nomes = ['Técnica','Tempo(s)','ME','MAE','MSE','R2']

for nome, rgr in zip(reg_nomes, regressores):
  print('==',nome,'==')
  for train_index, test_index in kf.split(X):
    etapa = []
    etapa.append(nome)

   # dataset de treinamento(X_train,y_train)
   # dataset de testes(X_test,y_test)
    X_train, X_test = X[train_index], X[test_index]
    y_train, y_test = y[train_index], y[test_index]

    #treinamento
    t = time.process_time()  
    rgr.fit(X_train,y_train)
    etapa.append(time.process_time()-t)
    
    #validacao
    y_prev = rgr.predict(X_test)

    #métricas
    etapa.append(max_error(y_test,y_prev))
    etapa.append(mean_absolute_error(y_test,y_prev))
    etapa.append(mean_squared_error(y_test,y_prev))
    etapa.append(r2_score(y_test,y_prev))

    print(etapa)

    resultados.append(etapa)

#armazenando resultados
res1 = pd.DataFrame(data = resultados, columns =res_nomes )
# salva
res1.to_excel('com_pca.xlsx',index=True)

from google.colab import files
files.download('com_pca.xlsx')

"""## Treinamento Incremental"""

##https://scikit-learn.org/0.15/modules/scaling_strategies.html


import time
from sklearn.model_selection import KFold
from sklearn.linear_model import SGDRegressor, PassiveAggressiveRegressor

from sklearn.metrics import max_error
from sklearn.metrics import mean_absolute_error
from sklearn.metrics import mean_squared_error
from sklearn.metrics import r2_score

resultados = []

incrementais = (SGDRegressor(), PassiveAggressiveRegressor())

X = ds[ds.columns[:-1]].values
y = ds[ds.columns[-1]].values

kf = KFold(n_splits=3, random_state=42, shuffle=True)

for inc in incrementais:
  print('==',inc.__class__,'==')
  for train_index, test_index in kf.split(X):
    etapa = []
    etapa.append(inc.__class__)

    train_size = len(train_index)
    train_step = int(train_size/100)
    
    t = time.process_time()

    for step in range(1, train_size, train_step):
      train_baund = train_index[step:step+train_step]
      X_train = X[train_baund]
      y_train = y[train_baund]

      inc.partial_fit(X_train,y_train)


    etapa.append(time.process_time()-t)
    
    X_test = X[test_index]
    y_test = y[test_index]

    #validacao
    y_prev = inc.predict(X_test)

    #métricas
    etapa.append(max_error(y_test,y_prev))
    etapa.append(mean_absolute_error(y_test,y_prev))
    etapa.append(mean_squared_error(y_test,y_prev))
    etapa.append(r2_score(y_test,y_prev))

    print(etapa)

    resultados.append(etapa)
    #armazenando resultados
    res1 = pd.DataFrame(data = resultados)
    # salva
    res1.to_excel('incremental.xlsx',index=True)

#armazenando resultados
res1 = pd.DataFrame(data = resultados )
