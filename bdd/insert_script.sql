INSERT INTO categories VALUES(1, "tortue");
INSERT INTO categories VALUES(2, "baseball");
INSERT INTO categories VALUES(3, "broom");
INSERT INTO categories VALUES(4, "dolphin");
INSERT INTO categories VALUES(5, "ant");
INSERT INTO categories VALUES(6, "boomerang");
INSERT INTO categories VALUES(7, "car");
INSERT INTO categories VALUES(8, "foot");
INSERT INTO categories VALUES(9, "golf_club");
INSERT INTO categories VALUES(10, "mushroom");
INSERT INTO categories VALUES(11, "pants");
INSERT INTO categories VALUES(12, "rain");

INSERT INTO users VALUES(1,"arnaudsimon091@gmail.comaa","arnaudsimon091@gmail.com","aqwzsx",0,0);
INSERT INTO users VALUES(2,"user1","user1@gmail.com","aqwzsx",0,0);
INSERT INTO users VALUES(3,"arnaud_lasticotier","arnaud_lasticot@gmail.com","aqwzsxedc",0,0);

INSERT INTO drawings VALUES(1,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,50,0,10);
INSERT INTO drawings VALUES(2,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,90,0,10);
INSERT INTO drawings VALUES(3,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,75,0,10);
INSERT INTO drawings VALUES(4,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,45,0,10);
INSERT INTO drawings VALUES(5,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,35,0,30);
INSERT INTO drawings VALUES(6,2,1,1,"\\static\\assets\\images\\test\\plot.png",0,90,0,30);
INSERT INTO drawings VALUES(7,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,70,0,30);
INSERT INTO drawings VALUES(8,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,60,0,30);
INSERT INTO drawings VALUES(9,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,22,0,30);
INSERT INTO drawings VALUES(10,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,50,0,30);
INSERT INTO drawings VALUES(11,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,60,0,30);
INSERT INTO drawings VALUES(12,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,60,0,30);
INSERT INTO drawings VALUES(13,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,60,0,30);
INSERT INTO drawings VALUES(14,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,60,0,30);
INSERT INTO drawings VALUES(15,2,1,1,"\\static\\assets\\images\\test\\draw.jpg",0,60,0,30);
INSERT INTO drawings VALUES(17,2,2,2,"\\static\\doodle\\baseball\\baseball_92.jpg",1,97,0,10);
INSERT INTO drawings VALUES(18,2,2,2,"\\static\\doodle\\baseball\\baseball_93.jpg",1,91,0,10);
INSERT INTO drawings VALUES(19,2,2,2,"\\static\\doodle\\broom\\broom_38.jpg",1,100,0,5);
INSERT INTO drawings VALUES(20,2,2,2,"\\static\\doodle\\baseball\\baseball_94.jpg",1,86,0,5);
INSERT INTO drawings VALUES(21,2,2,2,"\\static\\doodle\\baseball\\baseball_95.jpg",1,78,0,5);

INSERT INTO notations VALUES(1,"no",3,21,2,2);

INSERT INTO MODELS VALUES(1,"default", 40, 0.993, 0.018, 0.988, 0.034, "batch_size;1024;optimizer;adadelta;learning_rate;0.001", "20200628035258", "baseball,broom");