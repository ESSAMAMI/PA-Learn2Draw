# MANDATORY IMPORTS
import tensorflow as tf
import matplotlib
matplotlib.use('Agg')
from matplotlib import pyplot
from tensorflow.keras.models import load_model
from tensorflow.keras.utils import *
import numpy as np
from sklearn.model_selection import train_test_split
from os import walk, listdir
import os
import shutil
from PIL import Image
import cv2
from datetime import datetime
from utils import request_bdd

# CNN part
def create_and_train_cnn_model(new_inputName, new_inputEpochs, new_inputBatchSize, new_optimizer, new_learning_rate, is_update, delete_catego_or_not) -> str:

	try:
		print("\nCREATING CNN\n")
		# kill whitespace
		#new_inputName = new_inputName.replace(" ", "")

		# NP LOAD TRICK TO DEBUG ERROR CANNOT LOAD PICKLE DATA
		# save np.load
		np_load_old = np.load

		# modify the default parameters of np.load
		np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)

		# CONSTANTS
		batch_size = new_inputBatchSize
		epochs= new_inputEpochs
		img_rows, img_cols = 28, 28 # image dimensions

		# collect filenames
		print("cwd = ", os.getcwd())
		data_path = "models/dataset_quickdraw/"
		for (dirpath, dirnames, filenames) in walk(data_path):
		     pass # filenames accumulate in list 'filenames'
		print(filenames)

		# get catego from bdd ==> possible improvment, take only if dataset_available == 1
		categories_infos = request_bdd.learn2draw_list_all_categories()
		bdd_categories = []
		for elt in categories_infos:
			elt = elt.split(";")
			bdd_categories.append(elt[0]+".npy")

		print("current bdd cateogries handled = ", bdd_categories)

		#print("categories_infos : ",categories_infos)
		#print("bdd catego : ", bdd_categories)

		# only keep categories that are in the database + have an npy file associated
		shared_categories_filenames = list(set(filenames).intersection(bdd_categories))

		# if delete category triggered, need to remove the selected category 
		if delete_catego_or_not != "no":
			print("delete catego triggered, specific model created")
			shared_categories_filenames.remove(delete_catego_or_not+".npy")

		print("shared_categories_filenames :",shared_categories_filenames)
		# usefull variables for models
		#num_images = 400
		num_images = 10000#0 ### was 100000, reduce this number if memory issues.
		num_files = len(shared_categories_filenames) # *** we have x files ***
		images_per_category = num_images//num_files
		seed = np.random.randint(1, 10e7) #maybe delete seed later ?
		i=0
		print(images_per_category, " image per category (if possible)")


		# preprocess and load the data
		i=0
		for file in shared_categories_filenames:
		    print("i = ",i)
		    file_path = data_path + file
		    print("file path : ", file_path)
		    x = np.load(file_path)
		    print("x shape = ", x.shape)
		    print("x 0 shape = ", x[42].shape)
		    x = x.astype('float32') ##normalize images
		    x /= 255.0
		    y = [i] * len(x) # create numeric label for this image
		    
		    x = x[:images_per_category] # get the sample of images 
		    print("x final for ", file_path, " = ", x.shape)
		    y = y[:images_per_category] # get the sample of labels 
		    
		    if i == 0:
		        x_all = x
		        y_all = y
		    else:
		        x_all = np.concatenate((x,x_all), axis=0)
		        y_all = np.concatenate((y,y_all), axis=0)
		    i += 1

		# restore np.load for future normal usage, end of pickle bug
		np.load = np_load_old

		# split data arrays into train and test segments, delete random state soon ?
		x_train, x_test, y_train, y_test = train_test_split(x_all, y_all, test_size=0.2, random_state=42)

		# reshape and init input shape
		x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1) 
		x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1) 
		input_shape = (img_rows, img_cols, 1)
		print("input_shape : ", x_train.shape, "and ", x_test.shape)

		# one hot encode for convnet
		y_train = tf.keras.utils.to_categorical(y_train, num_files) 
		y_test = tf.keras.utils.to_categorical(y_test, num_files)

		# split again in smaller test sets == check if usefull later, delete random state soon ?
		x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.1, random_state=42)

		# basic conv model
		model = tf.keras.Sequential()

		model.add(tf.keras.layers.Conv2D(32, kernel_size=(3, 3), activation='relu', input_shape=input_shape)) 
		model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2))) 
		model.add(tf.keras.layers.Dropout(0.25))

		model.add(tf.keras.layers.Conv2D(64, (3, 3), activation='relu')) 
		model.add(tf.keras.layers.MaxPooling2D(pool_size=(2, 2))) 
		model.add(tf.keras.layers.Dropout(0.25))

		model.add(tf.keras.layers.Flatten())
		model.add(tf.keras.layers.Dense(128, activation='relu')) 
		model.add(tf.keras.layers.Dropout(0.5))
		model.add(tf.keras.layers.Dense(num_files, activation='softmax')) 

		print("Compiling...........")
		print("Define optimizer")
		if new_optimizer == "adam" :
			print("opti = adam")
			final_optimizer = tf.keras.optimizers.Adam(learning_rate=new_learning_rate)
		elif new_optimizer == "sgd" :
			print("opti = sgd")
			final_optimizer = tf.keras.optimizers.SGD(learning_rate=new_learning_rate)
		else:
			print("opti = adadelta")
			final_optimizer = tf.keras.optimizers.Adam(learning_rate=new_learning_rate)

		model.compile(loss=tf.keras.losses.categorical_crossentropy,
		 optimizer=final_optimizer,
		 metrics=['accuracy'])

		# train the model using new train and validation datasets over here, could also use test
		#callbacks=[tf.keras.callbacks.TensorBoard(log_dir="static/models/tb_log_dir", histogram_freq=1, profile_batch = 100000000)]
		history = model.fit( x_train, y_train,
		 batch_size=batch_size,
		 epochs=epochs,
		 #callbacks=callbacks,
		 verbose=1,
		 validation_data=(x_valid, y_valid)
		)

		# # predict using the test dataset
		# score = model.evaluate(x_test, y_test, verbose=1)
		# print('Test loss:', score[0])
		# print('Test accuracy:', score[1])

		# get the last prediction (loss + accuracy + val_loss + val_accuracy)
		predicts = []
		predicts.append(str(round(history.history['loss'][epochs-1].item(), 3)))
		predicts.append(str(round(history.history['accuracy'][epochs-1].item(), 3)))
		predicts.append(str(round(history.history['val_loss'][epochs-1].item(), 3)))
		predicts.append(str(round(history.history['val_accuracy'][epochs-1].item(), 3)))

		print("predicts [loss, accu, val_loss, val_accu] = ", predicts)

		# if is_update, delete the old folder to replace everything
		if "is_update" in is_update :
			print("\nupdate\n")
			shutil.rmtree("static/models/"+new_inputName)
			os.mkdir("static/models/"+new_inputName)

		# create folder for the model
		if not os.path.exists("static/models/"+new_inputName):
			print(" create ")
			os.mkdir("static/models/"+new_inputName)

		# forced to use timestamp in image name in Flask, mandatory for refresh when updating model
		time = int(datetime.now().strftime("%Y%m%d%H%M%S"))
		
		# save charts and model architecture
		plot_model(model, "static/models/"+new_inputName+"/model_"+str(time)+".png")

		pyplot.gcf().subplots_adjust(hspace = 0.5)
		# Afficher la loss
		pyplot.subplot(211)
		pyplot.title('Cross Entropy Loss')
		pyplot.plot(history.history['loss'], color='blue', label='train')
		pyplot.plot(history.history['val_loss'], color='orange', label='test')

		# Afficher l'accuracy
		pyplot.subplot(212)
		pyplot.title('Classification Accuracy')
		pyplot.plot(history.history['accuracy'], color='blue', label='train')
		pyplot.plot(history.history['val_accuracy'], color='orange', label='test')

		# Sauvegarde
		pyplot.savefig("static/models/"+new_inputName+"/plot_"+str(time)+".png")
		pyplot.close()
		# save model
		model.save("./static/models/"+new_inputName+"/"+new_inputName+".h5")

		# append time to returned list to find images
		predicts.append(str(time))

		# append all categories used for this model
		shared_catego_string = ','.join(str(e) for e in shared_categories_filenames).replace(".npy", "")
		predicts.append(shared_catego_string)

		return "True;" + predicts[1] + ";" + predicts[0] + ";" + predicts[3] + ";" + predicts[2] + ";" + predicts[4] + ";" + predicts[5]

	except Exception as e:
		print("on a récup l'exception ;) \n, type e = ", type(e))
		print("try str ==> ", str(e))

		return str(e)

# MLP part
def create_and_train_mlp_model(new_inputName, new_inputEpochs, new_inputBatchSize, new_optimizer, new_learning_rate, is_update, delete_catego_or_not) -> str:

	try:
		print("\nCREATING MLP\n")
		# kill whitespace
		#new_inputName = new_inputName.replace(" ", "")

		# NP LOAD TRICK TO DEBUG ERROR CANNOT LOAD PICKLE DATA
		# save np.load
		np_load_old = np.load

		# modify the default parameters of np.load
		np.load = lambda *a,**k: np_load_old(*a, allow_pickle=True, **k)

		# CONSTANTS
		batch_size = new_inputBatchSize
		epochs= new_inputEpochs
		img_rows, img_cols = 28, 28 # image dimensions

		# collect filenames
		print("cwd = ", os.getcwd())
		data_path = "models/dataset_quickdraw/" 
		for (dirpath, dirnames, filenames) in walk(data_path):
		     pass # filenames accumulate in list 'filenames'
		print(filenames)

		# get catego from bdd ==> maybe not usefull
		categories_infos = request_bdd.learn2draw_list_all_categories()
		bdd_categories = []
		for elt in categories_infos:
			elt = elt.split(";")
			bdd_categories.append(elt[0]+".npy")

		#print("categories_infos : ",categories_infos)
		#print("bdd catego : ", bdd_categories)

		# only keep categories that are in the database + have an npy file associated
		shared_categories_filenames = list(set(filenames).intersection(bdd_categories))
		print("shared_categories_filenames :",shared_categories_filenames)

		# usefull variables for models
		num_images = 10000#0 ### was 100000, reduce this number if memory issues.
		num_files = len(shared_categories_filenames) # *** we have x files ***
		images_per_category = num_images//num_files
		seed = np.random.randint(1, 10e7) #maybe delete seed later ?
		i=0
		print(images_per_category, " image per category (if possible)")


		# preprocess and load the data
		i=0
		for file in shared_categories_filenames:
		    print("i = ",i)
		    file_path = data_path + file
		    print("file path : ", file_path)
		    x = np.load(file_path)
		    print("x shape = ", x.shape)
		    print("x 0 shape = ", x[42].shape)
		    x = x.astype('float32') ##normalize images
		    x /= 255.0
		    y = [i] * len(x) # create numeric label for this image
		    
		    x = x[:images_per_category] # get the sample of images 
		    y = y[:images_per_category] # get the sample of labels 
		    
		    if i == 0:
		        x_all = x
		        y_all = y
		    else:
		        x_all = np.concatenate((x,x_all), axis=0)
		        y_all = np.concatenate((y,y_all), axis=0)
		    i += 1

		# restore np.load for future normal usage, end of pickle bug
		np.load = np_load_old

		# split data arrays into train and test segments, delete random state soon ?
		x_train, x_test, y_train, y_test = train_test_split(x_all, y_all, test_size=0.2, random_state=42)

		# reshape and init input shape
		x_train = x_train.reshape(x_train.shape[0], img_rows, img_cols, 1) 
		x_test = x_test.reshape(x_test.shape[0], img_rows, img_cols, 1) 
		print("mlp method")
		input_shape = (img_rows, img_cols, 1)
		print("input_shape : ", x_train.shape)

		# one hot encode for convnet
		y_train = tf.keras.utils.to_categorical(y_train, num_files) 
		y_test = tf.keras.utils.to_categorical(y_test, num_files)

		# split again in smaller test sets == check if usefull later, delete random state soon ?
		x_train, x_valid, y_train, y_valid = train_test_split(x_train, y_train, test_size=0.1, random_state=42)

		# basic conv model
		model = tf.keras.Sequential()

		model.add(tf.keras.layers.Flatten(input_shape=input_shape))
		model.add(tf.keras.layers.Dense(2048, activation='relu')) 
		model.add(tf.keras.layers.Dropout(0.4))
		model.add(tf.keras.layers.Dense(1024, activation='relu')) 
		model.add(tf.keras.layers.Dropout(0.4))
		model.add(tf.keras.layers.Dense(512, activation='relu')) 
		model.add(tf.keras.layers.Dropout(0.4))
		model.add(tf.keras.layers.Dense(256, activation='relu')) 
		model.add(tf.keras.layers.Dense(num_files, activation='softmax')) 

		print("Compiling...........")
		print("Define optimizer")
		if new_optimizer == "adam" :
			print("opti = adam")
			final_optimizer = tf.keras.optimizers.Adam(learning_rate=new_learning_rate)
		elif new_optimizer == "sgd" :
			print("opti = sgd")
			final_optimizer = tf.keras.optimizers.SGD(learning_rate=new_learning_rate)
		else:
			print("opti = adadelta")
			final_optimizer = tf.keras.optimizers.Adam(learning_rate=new_learning_rate)

		model.compile(loss=tf.keras.losses.categorical_crossentropy,
		 optimizer=final_optimizer,
		 metrics=['accuracy'])

		# train the model using new train and validation datasets over here, could also use test
		#callbacks=[tf.keras.callbacks.TensorBoard(log_dir="static/models/tensorboard_log_dir", histogram_freq=1, profile_batch = 100000000)]
		history = model.fit( x_train, y_train,
		 batch_size=batch_size,
		 epochs=epochs,
		 #callbacks=callbacks,
		 verbose=1,
		 validation_data=(x_valid, y_valid)
		)

		# # predict using the test dataset
		# score = model.evaluate(x_test, y_test, verbose=1)
		# print('Test loss:', score[0])
		# print('Test accuracy:', score[1])

		# get the last prediction (loss + accuracy + val_loss + val_accuracy)
		predicts = []
		predicts.append(str(round(history.history['loss'][epochs-1].item(), 3)))
		predicts.append(str(round(history.history['accuracy'][epochs-1].item(), 3)))
		predicts.append(str(round(history.history['val_loss'][epochs-1].item(), 3)))
		predicts.append(str(round(history.history['val_accuracy'][epochs-1].item(), 3)))

		print("predicts [loss, accu, val_loss, val_accu] = ", predicts)

		# if is_update, delete the old folder to replace everything
		if "is_update" in is_update :
			print("\nupdate\n")
			shutil.rmtree("static/models/"+new_inputName)
			os.mkdir("static/models/"+new_inputName)


		# create folder for the model
		if not os.path.exists("static/models/"+new_inputName):
			os.mkdir("static/models/"+new_inputName)

		# forced to use timestamp in image name in Flask, mandatory for refresh when updating model
		time = int(datetime.now().strftime("%Y%m%d%H%M%S"))
		
		# save charts and model architecture
		plot_model(model, "static/models/"+new_inputName+"/model_"+str(time)+".png")

		pyplot.gcf().subplots_adjust(hspace = 0.5)
		# Afficher la loss
		pyplot.subplot(211)
		pyplot.title('Cross Entropy Loss')
		pyplot.plot(history.history['loss'], color='blue', label='train')
		pyplot.plot(history.history['val_loss'], color='orange', label='test')

		# Afficher l'accuracy
		pyplot.subplot(212)
		pyplot.title('Classification Accuracy')
		pyplot.plot(history.history['accuracy'], color='blue', label='train')
		pyplot.plot(history.history['val_accuracy'], color='orange', label='test')

		# Sauvegarde
		pyplot.savefig("static/models/"+new_inputName+"/plot_"+str(time)+".png")
		pyplot.close()
		# save model
		model.save("./static/models/"+new_inputName+"/"+new_inputName+".h5")

		# append time to returned list to find images 
		predicts.append(str(time))

		# append all categories used for this model
		shared_catego_string = ','.join(str(e) for e in shared_categories_filenames).replace(".npy", "")
		predicts.append(shared_catego_string)

		return "True;" + predicts[1] + ";" + predicts[0] + ";" + predicts[3] + ";" + predicts[2] + ";" + predicts[4] + ";" + predicts[5]

	except Exception as e:
		print("on a récup l'exception ;) \n, type e = ", type(e))
		print("try str ==> ", str(e))

		return str(e)


def get_predict_sample_cnn_baseball_broom_dolphin(image_name: str, category: str, model_name: str) -> str:
	# fix manually labels for the begining, need to provide that info depending on the model
	print("\n\nPREDICTION TIME\n\n")
	print("image_name = ", image_name)
	print("model name = ", model_name)

	# get catego handled by the current model
	# get all predictable categories, first get current model name, then categories
	print("get all handled categories for current model")
	categories = request_bdd.learn2draw_get_categories_handled_for_one_model(model_name)
	print("categories handled : ", categories)
	# predict using catego handled by the model !
	
	# take list of "invalid" indexes (0 correspond), cases will be delated in last predict

	# dynamics labels to predict !
	# print("cat info ", categories_infos)
	# labels = categories_infos

	labels = list(categories.split(",")) #["baseball", "broom", "dolphin"]
	print("labels handeled", labels)

	index_cat = labels.index("chat")

	# OLD LOAD METHOD
	# model = load_model('./models/QDrawModel_baseball_broom_dolphin.h5')
	# print("load model ok")

	# load the "current" model, if doesn't existe use the default one
	current_model = [f for f in listdir("models/") if f.endswith('.h5') and "current" in f and "default" not in f]
	print("current_model = ", current_model)
	if current_model == []:
		current_model = "default.h5"
	else:
		current_model = str(current_model).strip("['']")
	print("current_model = ", current_model)

	model = load_model("./models/"+current_model)
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
	print("new formatted image = ", image_name)

	img = Image.open(image_name).convert('L')
	im = np.array(img)
	print("size of formatted image numpy = ", im.shape)
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
	#print("im : \n", im)
	im = np.where(im==1, 0, im)

	#print("switched : \n", im)
	predict_final = model.predict(im)
	print("np argmax == ", np.argmax(predict_final))
	print("prediction finale = ", labels[np.argmax(predict_final)])
	print(" => ", predict_final[0][np.argmax(predict_final)])
	# change predict final, kill cases with "invalid" indexes

	# change values to be sure that the sum of everything = 1 (percentage)
	print("cat percent : ", float(str(predict_final[0][index_cat]).replace(',', '.')))

	print("\ntoutes les predict : ", predict_final)
	print(str(labels[np.argmax(predict_final)]) + ";" + str(predict_final[0][np.argmax(predict_final)]))
	return str(labels[np.argmax(predict_final)]) + ";" + str(predict_final[0][np.argmax(predict_final)])
