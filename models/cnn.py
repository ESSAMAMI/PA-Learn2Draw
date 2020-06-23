# MANDATORY IMPORTS
import tensorflow as tf
from tensorflow.keras.models import load_model
import keras
import numpy as np
from sklearn.model_selection import train_test_split
from os import walk
import os
import h5py
from PIL import Image
import cv2

def get_predict_sample_cnn_baseball_broom_dolphin(image_name: str, category: str) -> str:
	# fix manually labels for the begining, need to provide that info depending on the model
	print("image_name = ", image_name)
	labels = ["baseball", "broom", "dolphin"]
	# load model for new use
	model = load_model('./models/QDrawModel_baseball_broom_dolphin.h5')
	print("load model ok")

	# load image and handle transparency with cv2
	image = cv2.imread(image_name, cv2.IMREAD_UNCHANGED)  
	#make mask of where the transparent bits are
	trans_mask = image[:,:,3] == 0

	#replace areas of transparency with white and not transparent
	image[trans_mask] = [255, 255, 255, 255]

	#new image without alpha channel...
	new_img = cv2.cvtColor(image, cv2.COLOR_BGRA2BGR)

	cv2.imwrite(image_name, new_img)

	img = Image.open(image_name).convert('L')
	im = np.array(img)
	#im = np.array(Image.open(image_name).convert('P'))
	# print(type(im))
	# print("shape : ", im.shape)

	# #Image.fromarray(im).save('gr_dolphin.png')

	# now that we have good dimensions (2D), reshape to have the good format
	new_width  = 28
	new_height = 28
	im = np.array(img.resize((new_width, new_height), Image.ANTIALIAS))
	# #Image.fromarray(im).save('gr_custom.png')
	#print("im shape 2 = ", im.shape)
	im = im.reshape(1,im.shape[0],im.shape[1],1)
	print("new shape for predict : ", im.shape)
	im = im.astype('float32') ##normalize image
	im /= 255
	print("im : \n", im)
	im = np.where(im==1, 0, im)

	print("switched : \n", im)
	predict_final = model.predict(im)
	print("prediction finale = ", labels[np.argmax(predict_final)]," => ", predict_final[0][np.argmax(predict_final)])
	print("toutes les predict : ", predict_final)
	return str(labels[np.argmax(predict_final)]) + ";" + str(predict_final[0][np.argmax(predict_final)])
