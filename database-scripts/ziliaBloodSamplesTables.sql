create table IF NOT EXISTS bloodfiles (path text, md5 text);

# Extract metadata from path
.mode csv
.import "/tmp/bloodfiles.txt"

alter table bloodfiles add column saturation real;
alter table bloodfiles add column intensity int;
alter table bloodfiles add column led text;
alter table bloodfiles add column comment text;


# Saturation extracted with:
# select substr(path, instr(path, 'so')+2,2),path from bloodfiles where path like '%so%';
update bloodfiles set saturation=substr(path, instr(path, 'so')+2,2) where path like '%so%';
update bloodfiles set intensity=substr(path, instr(path, 'int')+3,2) where path like '%int%';
update bloodfiles set intensity = 75 where path like "%int___L%";
update bloodfiles set intensity=substr(path, instr(path, 'int')+3,3) where path like "%int%" and path not like '%int75%';

update bloodfiles set comment='sample' where path like '%sample%';
update bloodfiles set comment='calibration' where path not like '%sample%';

CREATE TABLE bloodspectra (wavelength real, intensity real, column text, md5 text);
create index md5Idx3 on bloodspectra (md5);
create index wavelengthIdx2 on bloodspectra (wavelength);


