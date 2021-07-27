# Monkeys

insert into monkeys (name, monkeyId) values('Rwanda',1512436);
insert into monkeys (name, monkeyId) values('Kenya',1512692);
insert into monkeys (name, monkeyId) values('Bresil',1511184);
insert into monkeys (name, monkeyId) values('Somalie',1508202);

delete from spectralfiles where path not like '%.csv%';

# Add date 
update spectralfiles set date= substr(path, instr(path, '/2021')+1,4+1) || '-' || substr(path, instr(path, '/2021')+4+1,2) || '-' || substr(path, instr(path, '/2021')+6+1,2) || " " || substr(path, instr(path, '/2021')+9+1,2) || ":" || substr(path, instr(path, '/2021')+11+1,2) || ":" || substr(path, instr(path, '/2021')+13+1,2) where path like '%/2021____-______-%';

# Add monkeyId
update spectralfiles set monkeyId='1511184' where path like '%bresil%';
update spectralfiles set monkeyId='1512692' where path like '%kenya%';
update spectralfiles set monkeyId='1512436' where path like '%rwanda%';
update spectralfiles set monkeyId='1508202' where path like '%somalie%';

update spectralfiles set timeline='baseline' where path like '%baseline%';
update spectralfiles set timeline='background' where path like '%background%';

# Add region
update spectralfiles set region='onh' where path like '%onh%';
update spectralfiles set region='mac' where path like '%mac%';

# Add eye
update spectralfiles set eye='os' where path like '%-os-%';
update spectralfiles set eye='od' where path like '%-od-%';


# CLeanup import
delete from imagefiles where path not like '%.jpg%';

# Add date 
update imagefiles set date= substr(path, instr(path, '/2021')+1,4+1) || '-' || substr(path, instr(path, '/2021')+4+1,2) || '-' || substr(path, instr(path, '/2021')+6+1,2) || " " || substr(path, instr(path, '/2021')+9+1,2) || ":" || substr(path, instr(path, '/2021')+11+1,2) || ":" || substr(path, instr(path, '/2021')+13+1,2) where path like '%/2021____-______-%';

# Add monkeyId
update imagefiles set monkeyId='1511184' where path like '%bresil%';
update imagefiles set monkeyId='1512692' where path like '%kenya%';
update imagefiles set monkeyId='1512436' where path like '%rwanda%';
update imagefiles set monkeyId='1508202' where path like '%somalie%';

update imagefiles set timeline='baseline' where path like '%baseline%';
update imagefiles set timeline='background' where path like '%background%';

# Add region
update imagefiles set region='onh' where path like '%onh%';
update imagefiles set region='mac' where path like '%mac%';

# Add eye
update imagefiles set eye='os' where path like '%-os-%';
update imagefiles set eye='od' where path like '%-od-%';



# CLeanup import
delete  from bloodfiles where path not like "%Blood%";

# Saturation extracted with:
update bloodfiles set saturation=substr(path, instr(path, 'so')+2,2) where path like '%so%';
update bloodfiles set intensity=substr(path, instr(path, 'int')+3,2) where path like '%int%';
update bloodfiles set intensity = 75 where path like "%int___L%";
update bloodfiles set intensity=substr(path, instr(path, 'int')+3,3) where path like "%int%" and path not like '%int75%';

update bloodfiles set comment='sample' where path like '%sample%';
update bloodfiles set comment='calibration' where path not like '%sample%';




