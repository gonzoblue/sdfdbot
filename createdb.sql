create database sdfd;
use sdfd;
create table calls (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, calldate CHAR(25), calltype VARCHAR(50), street VARCHAR(50), crossstreet VARCHAR(100), unitids VARCHAR(500), numunits TINYINT(3), processtime TIMESTAMP, alertsent TINYINT(1);
insert into calls (id, calldate, calltype, street, crossstreet, unitids, numunits, processdate, alertsent) values (NULL, '11/11/2001 11:11:11 PM', 'Medical', 'TEST ST', 'CROSS DR', 'E00, M00', '2', '2001-11-11 01:01:01', '0');
exit;
