update imageFiles set date= substr(path, instr(path, '/2021')+1,4) || '-' || substr(path, instr(path, '/2021')+1+4,2) || '-' || substr(path, instr(path, '/2021')+1+6,2) || " " || substr(path, instr(path, '/2021')+1+9,2) || ":" || substr(path, instr(path, '/2021')+11+1,2) || ":" || substr(path, instr(path, '/2021')+13+1,2) where path like '%/2021____-______-%';


# Add monkeyId
update imageFiles set monkeyId='1511184' where path like '%bresil%';
update imageFiles set monkeyId='1512692' where path like '%kenya%';
update imageFiles set monkeyId='1512436' where path like '%rwanda%';
update imageFiles set monkeyId='1508202' where path like '%somalie%';

# Add target
update imageFiles set target='onh' where path like '%onh%';
update imageFiles set target='mac' where path like '%mac%';

# Add eye
update imageFiles set eye='os' where path like '%-os-%';
update imageFiles set eye='od' where path like '%-od-%';
