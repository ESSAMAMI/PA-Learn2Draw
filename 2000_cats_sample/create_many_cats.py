import os
import shutil

print("hello")
directory = os.getcwd()
print(directory)

current_cats = [f for f in os.listdir(directory+"/") if f.endswith('.jpg')]

for f in os.listdir(directory+"/"):
	print(f)

print("current_cats ", current_cats)

objectif = 1000
current = 20

while current < objectif:
	print("current = ", current)
	for elt in current_cats:
		#copy each element and change id
		#filename = elt
		splited = elt.split("_")
		splited[1] = splited[1].replace(".jpg", "")
		print("before : ", splited[1])
		splited[1] = str(int(splited[1]) + current) + ".jpg"
		print("after ", " chat_", splited[1])
		
		shutil.copy2(directory+"/"+elt, directory+"/chat_"+splited[1])

	current += 20