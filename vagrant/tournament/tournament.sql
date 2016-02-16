-- Table definitions for the tournament project.
--
-- Put your SQL 'create table' statements in this file; also 'create view'
-- statements if you choose to use it.
--
-- You can write comments in this file by starting them with two dashes, like
-- these lines here.

-- CREATE tournament database
DROP DATABASE IF EXISTS tournament;
CREATE database tournament;

-- Connect to new DB
\c tournament

-- ***** Table definitions *****
-- ID -- Player Mapping
DROP TABLE IF EXISTS Player CASCADE;
CREATE TABLE Player(
	id serial primary key,
	name text);

-- Record
DROP TABLE IF EXISTS Match CASCADE;
CREATE TABLE Match(
	player1 integer references Player(id),
	player2 integer references Player(id),
	result text
	);	

-- Views to assist with more complicated queries
-- Total win of each Player (id)
DROP VIEW IF EXISTS Win CASCADE;
CREATE VIEW Win as
SELECT Player.id, count(Match.result) as wins
FROM Player LEFT JOIN Match 
ON result = 'win' and Player.id = Match.player1
GROUP BY Player.id;

-- Total Matches played by each player (excluding byes)
DROP VIEW IF EXISTS Num_match;	
CREATE VIEW Num_match as
SELECT Player.id, count(Match.player2) as matches
FROM Player LEFT JOIN Match
ON Player.id = Match.player1 and Match.player1 != Match.player2
GROuP BY Player.id;

-- Total Matches played by each player (excluding byes)
DROP VIEW IF EXISTS Num_bye;	
CREATE VIEW Num_bye as
SELECT Player.id, count(Match.player2) as byes
FROM Player LEFT JOIN Match
ON Player.id = Match.player1 and Match.player1 = Match.player2
GROuP BY Player.id;

-- Opponents of each player -- groups unique player1,player2 in match
DROP VIEW IF EXISTS Opponent CASCADE;
CREATE VIEW Opponent as
SELECT player1, player2
FROM Match 
WHERE Match.player1 != Match.player2
GROUP BY player1,player2;

-- Total number of wins each opponent of a Player (id) has
DROP VIEW IF EXISTS Opponent_Win CASCADE;
CREATE VIEW Opponent_Win as
SELECT Player.id, sum(Win.wins) as opponent_wins
From Player
	LEFT JOIN Opponent
		ON Player.id = Opponent.player1
	LEFT JOIN Win
		ON Opponent.player2 = Win.id
GROUP BY Player.id;

-- Standings sort by wins and tiebreaked by opp. record
DROP VIEW IF EXISTS Standing CASCADE;
CREATE VIEW Standing as
SELECT Player.id, Player.name, Win.wins, Num_match.matches, Opponent_Win.opponent_wins
FROM Player 
	INNER JOIN Win
		ON Player.id = Win.id
	INNER JOIN Num_match
		ON Player.id = Num_match.id
	LEFT JOIN Opponent_Win
		ON Player.id = Opponent_Win.id
ORDER BY Win.wins DESC, Opponent_Win.opponent_wins DESC;

insert into Player (name) values ('Tina');
insert into Player (name) values ('Lujia');
insert into Player (name) values ('Mike');
insert into Player (name) values ('Anthony');
insert into Player (name) values ('Alyssa');

insert into Match values (1,2,'win');
insert into Match values (1,2,'win');
insert into Match values (2,1,'loss');
insert into Match values (2,1,'loss');
insert into Match values (1,1,'win');
insert into Match values (2,3,'draw');
insert into Match values (3,2,'draw');
insert into Match values (3,4,'win');
insert into Match values (3,5,'win');
insert into Match values (3,3,'win');
insert into Match values (4,3,'loss');
insert into Match values (5,3,'loss');
insert into Match values (4,5,'loss');
insert into Match values (5,4,'win');