# **PA - Project : Learn2draw** :art:

The aim of this project is to identify the objects created in drawings, specially doodles, 
but also to help people who have difficulties to improve their level of
drawing.  

### **Members** :construction_worker:
- NEZONDET-RENAUD Nathanael
- SIMON Arnaud
- ESSAMAMI Hamza

### **Requirements** :rotating_light:

Please run this command line in your shell to install all of 
requirements dependencies:
- Flask
- pandas
- pymysql
- (...)

```md
pip install -r requirements.txt
```

### **How to use** :bulb:

First, open the project with an IDE (PyCharm for example). 
Secondly, be sure that your PC have a dynamic IP address,

Then create a database using our script "learn2draw_db.sql"
in the bdd folder.

Change the config file after you are done (folder utils\config.ini).

Download the baseball, broom and dolphin dataset here (https://console.cloud.google.com/storage/browser/quickdraw_dataset/full/numpy_bitmap?pli=1)

Copy them to the models/dataset_quickdraw folder and rename them (fully_bitmap ... TO broom.npy)

Finally you have to run the following command on a shell :
**python app.py --reload**

This command will start a server on which you can view the application

On your browser type your ip address:5000
- ex : 192.168.10.120:5000

If you want to access to the backoffice, just login as admin - admin

### **Contributing** :lock:
Pull requests are welcome. For major changes, please open an issue first 
to discuss what you would like to change.

Please make sure to update tests as appropriate.