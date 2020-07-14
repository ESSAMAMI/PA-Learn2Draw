# create 1000 inserts from id=51
i = 1
data = ["INSERT INTO `drawings` (`id`, `USERS_id`, `CATEGORIES_id`, `CATEGORIES_PREDICTED_id`, `location`, `status`, `score`, `score_by_votes`, `time`) VALUES"]
while i < 1000 :
	line = "(" + str(50 + i) + ", 2, 2, 1,'\\\\static\\\\doodle\\\\baseball\\\\baseball_"+str(i)+".jpg', '3', 40, 92, 20),"
	data.append(line)
	#(1, 2, 5, 1, '\\static\\assets\\images\\test\\draw.jpg', '0', 50, 0, 10)
	i += 1

#last will have status == 1 for vote
i = 1000
line = "(" + str(50 + i) + ", 2, 2, 1,'\\\\static\\\\doodle\\\\baseball\\\\baseball_"+str(i)+".jpg', '1', 40, 0, 20),"
data.append(line)

with open("my_drawing_insert_lines.sql", "w") as fobj:
    for x in data:
        fobj.write(x + "\n")
