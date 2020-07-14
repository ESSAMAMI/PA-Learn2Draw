# create 99 insert notation from id=51 (for drawing 1050)
i = 1
data = ["INSERT INTO `notations` (`id`, `score`, `USERS_id`, `DRAWINGS_id`, `DRAWINGS_USERS_id`, `DRAWINGS_CATEGORIES_id`) VALUES"]
while i <= 99 :
	if i >= 1 and i <= 5: 
		line = "(" + str(1099 + i) + ", 'no', "+str(9+i)+", 2099, 2, 5),"
	else:
		line = "(" + str(1099 + i) + ", 'yes', "+str(9+i)+", 2099, 2, 5),"
	data.append(line)
	#(1, 'no', 3, 21, 2, 2),
	i += 1

with open("my_notations_insert_lines.sql", "w") as fobj:
    for x in data:
        fobj.write(x + "\n")
