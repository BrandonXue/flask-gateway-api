-- $ sqlite3 MBS.db < MBS.sql

PRAGMA foreign_keys=ON;
BEGIN TRANSACTION;
--TABLES-------------------------------------------------------------
DROP TABLE IF EXISTS users;
CREATE TABLE users (
	id 			INTEGER		PRIMARY KEY		AUTOINCREMENT	NOT NULL,
	username	TEXT		UNIQUE	NOT NULL,
	email		TEXT		UNIQUE	NOT NULL,
	pw_hash		TEXT		NOT NULL
);

DROP TABLE IF EXISTS follows;
CREATE TABLE follows (
	user_id			INTEGER	NOT NULL,
	following_id	INTEGER	NOT NULL,

	PRIMARY KEY(user_id, following_id),
	FOREIGN KEY(user_id) REFERENCES users(id)
		ON DELETE CASCADE,
	FOREIGN KEY(following_id) REFERENCES users(id)
		ON DELETE CASCADE
);

DROP TABLE IF EXISTS tweets;
CREATE TABLE tweets (
	id 				INTEGER  	NOT NULL,
	author_id		INTEGER		NOT NULL,
	timestamp		TEXT		NOT NULL,
	content_text	TEXT		NOT NULL,

	PRIMARY KEY(id, author_id),
	FOREIGN KEY(author_id) REFERENCES users(id)
		ON DELETE CASCADE ON UPDATE CASCADE
);
--TRIGGERS------------------------------------------------------------

--SAMPLE INPUTS-------------------------------------------------------
--USERS
INSERT INTO users(username, email, pw_hash) VALUES ("user1", "user1@email.com", "sha3_512$OSP9k1FypjhEJ9bUdONsdvGsh52OfNMZ7D5ILCyvuKKhKPPxzbGA6FU7vdrB74aT$12a4640ededb41963458f870a7ae7ec08c875298e573b5ed2ad6dbe985b4e4323d83b9862957b067be68e3f4e87c7c1ee6010043837be9c3f9c703456e7d6481");
INSERT INTO users(username, email, pw_hash) VALUES ("user2", "user2@email.com", "sha3_512$A1Y8krnxLBTYmjraRzNhrbAUnA5XJfFBUl2PLWOiG4vMFuisu5XU45aDewI9VddS$90419122b3d5ebf25dcef3ede3428a8c46f4374e5c14dcc78a1b3bdb7cbe7561d8a94ee93ca68f7409d5f8685e32a496cf0caf9418e05b4255522e6686141a90");
INSERT INTO users(username, email, pw_hash) VALUES ("user3", "user3@email.com", "sha3_512$urLWRtKk91lBjtEFAIhgsrYRRfYSEf8yyHFQSmoLO0mScb1HyPcwpwLiND1RwQgu$af73b7134429d3077c7059fc85c8049f01b081e9d3a071b1556ff96b0e481cadca6dbffe65065969374a4e8299a34eca851b841746167c4c086851e62eef441c");
INSERT INTO users(username, email, pw_hash) VALUES ("user4", "user4@email.com", "sha3_512$VbZM3K30NKlp2RJRVPzMUAWcR2EQmBvUIxeDv2FU94zG1B2Y43XZ6hRC9H5MWBaU$0eabf8264b43b6edca1739b180d4355841b1085b246e29ac476c6626da725171e723fe61f524fb69dafcb2cb972165c50d8c91cf909963579b49290fb36f7120");
INSERT INTO users(username, email, pw_hash) VALUES ("user5", "user5@email.com", "sha3_512$Mdo3QRIWNW18cwK37zxnhscfEyogNxT7dOpqFKhbPrdU4vVBY4x2RYHoDniIifI8$80af1010d4dc31100119923d0e818bc85294d26643f30eb2794a434610fe74ff37fa3b7f4279ce8c1de01c1bab9b7764209535a6bf64c679b3d0f6e4f0afc4f3");
INSERT INTO users(username, email, pw_hash) VALUES ("user6", "user6@email.com", "sha3_512$VgbAbvOsgnzh16J1GkgoxZ8dYiJ1Cpe0lxS0dbzjcvE2sR4VYUCSk1EGntkVB1CE$a892511ccf94ad1195db4b4c17230ef8df5657ed2e9b8ba72b290e1732dddad4a94ca6f54a2089cbe6850eea9bfcc423299347d773ea3127c9a11824ce568385");
INSERT INTO users(username, email, pw_hash) VALUES ("user7", "user7@email.com", "sha3_512$xAD5fZT5wVtKxo5ZnHqMJWGavKXWDGE2ApBJaVh8MqR4GnIyzS9YaGOBwoIgZKZN$18b133abb29848c09ace17b66df55bc65ac2b63fbcced31e69dbf870f346bc97b80f688e903aa21d1e22ceb1cfc34a050087c1cf0f44ab96737d5139dbf1570d");
--FOLLOWINGS
INSERT INTO follows(user_id, following_id) VALUES(1, 2);
INSERT INTO follows(user_id, following_id) VALUES(1, 3);
INSERT INTO follows(user_id, following_id) VALUES(2, 1);
INSERT INTO follows(user_id, following_id) VALUES(2, 3);
INSERT INTO follows(user_id, following_id) VALUES(3, 1);
--TWEETS
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 1)+1, 1, current_timestamp, "Hello world!");
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 1)+1, 1, current_timestamp, "Hello universe!");
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 1)+1, 1, current_timestamp, "Baked potato!");
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 2)+1, 2, current_timestamp, "Grilled onion!");
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 2)+1, 2, current_timestamp, "Steamed vegetable!");
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 2)+1, 2, current_timestamp, "Toasted bread!");
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 3)+1, 3, current_timestamp, "Seared steak!"); 
INSERT INTO tweets(id, author_id, timestamp, content_text) VALUES ((SELECT COALESCE(MAX(id), 0) FROM tweets WHERE author_id = 3)+1, 3, current_timestamp, "Fermented cucumber!");
COMMIT;
