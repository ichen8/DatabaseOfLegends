create database lol;

create table lol.player(
	playerID bigint not null,
	summonerID bigint,
	summonerName varchar(20),
	primary key (playerID)
);

create table lol.game(
	gameID bigint not null,

	gameDuration int,
	queueID int,
	seasonID int,

	winTeam int,

	team1Kills int,
	team1Deaths int,
	team1Assists int,
	team1TowerKills int,
	team1InhibKills int,
	team1BaronKills int,
	team1DragonKills int,
	team1Gold int,

	team2Kills int,
	team2Deaths int,
	team2Assists int,
	team2TowerKills int,
	team2InhibKills int,
	team2BaronKills int,
	team2DragonKills int,
	team2Gold int,

	team1Player1ID bigint,
	team1Player2ID bigint,
	team1Player3ID bigint,
	team1Player4ID bigint,
	team1Player5ID bigint,
	team2Player1ID bigint,
	team2Player2ID bigint,
	team2Player3ID bigint,
	team2Player4ID bigint,
	team2Player5ID bigint,

	primary key (gameID)
);


create table lol.playergame(
	playerID bigint not null,
	gameID bigint not null,
	timestamp varchar(20) not null,

	championID int not null,
	championString varchar(20),
	lane varchar(20),

	kills int,
	deaths int,
	assists int,
	
	primary key (playerID, gameID),
	foreign key (playerID) references player(playerID) on delete cascade,
	foreign key (gameID) references game(gameID) on delete cascade
);

create table lol.champPool(
	summonerID bigint not null,
	championID int not null,
	championString varchar(20),
	championLevel int,
	championPoints bigint,
	
	primary key (summonerID, championID)
);