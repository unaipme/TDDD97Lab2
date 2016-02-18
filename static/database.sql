CREATE TABLE 'Genders' (
	GenderID integer not null,
	Name text not null,
	primary key (GenderID)
);

INSERT INTO 'Genders' (GenderID, Name)
VALUES 		(0, 'Unspecified');
INSERT INTO 'Genders' (GenderID, Name)
VALUES		(1, 'Male');
INSERT INTO 'Genders' (GenderID, Name)
VALUES		(2, 'Female');

CREATE TABLE 'Users' (
	UserID integer primary key,
	Username text not null unique, /* e-mail */
	Password text not null,
	FirstName text not null,
	FamilyName text not null,
	Gender integer not null,
	City text not null,
	Country text not null,
	foreign key (Gender) references Genders (GenderID)
);

CREATE TABLE 'Tokens' (
	Token text,
	UserID integer,
	ExpireDate text not null,
	primary key (Token, UserID),
	foreign key (UserID) references Users (UserID)
);

CREATE TABLE 'Messages' (
	MessageID integer,
	SenderID integer not null,
	ReceiverID integer not null,
	MsgText text not null,
	primary key (MessageID),
	foreign key (SenderID) references Users (UserID),
	foreign key (ReceiverID) references Users (UserID)
);