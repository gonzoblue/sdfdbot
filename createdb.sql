create database sdfd;
use sdfd;
create table calls (id INT NOT NULL PRIMARY KEY AUTO_INCREMENT, date CHAR(25), calltype VARCHAR(50), street VARCHAR(50), crossstreet VARCHAR(100), unitids VARCHAR(500), numunits INT(3));
insert into calls (id, date, calltype, street, crossstreet, unitids, numunits) values (NULL, '11/11/2001 11:11:11 PM', 'Medical', 'TEST ST', 'CROSS DR', 'E00, M00', '2');
exit;
