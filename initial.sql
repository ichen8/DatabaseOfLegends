CREATE TABLE IF NOT EXISTS game (
	GameID BIGINT NOT NULL,
    Score1 TINYINT,
    Score2 TINYINT,
    Winner TINYINT,
    CS1 INT,
    CS2 INT,
    Gold1 INT,
    Gold2 INT,
    Duration LONG,
    PRIMARY KEY (GameID)
);

CREATE TABLE IF NOT EXISTS item (
	ItemID INT NOT NULL,
    Stats VARCHAR(200),
    Actives VARCHAR(200),
    Passives VARCHAR(200),
    PRIMARY KEY (ItemID)
);

CREATE TABLE IF NOT EXISTS champion (
	ChampionID INT NOT NULL,
    ChampionName VARCHAR (200),
    WinRate DOUBLE,
    AverageKDA DOUBLE,
    BaseStats VARCHAR(200),
    PRIMARY KEY (ChampionID)
);

CREATE TABLE IF NOT EXISTS player (
	PlayerID BIGINT NOT NULL,
    SummonerName VARCHAR(20),
    Rank VARCHAR(100),
    KDA DOUBLE,
    ChampionID INT,
    GameID BIGINT,
    ItemID INT,
    PRIMARY KEY (PlayerID),
    FOREIGN KEY (ChampionID) REFERENCES champion(ChampionID) ON DELETE CASCADE,
    FOREIGN KEY (GameID) REFERENCES game(GameID) ON DELETE CASCADE,
    FOREIGN KEY (ItemID) REFERENCES item(ItemID) ON DELETE CASCADE
);