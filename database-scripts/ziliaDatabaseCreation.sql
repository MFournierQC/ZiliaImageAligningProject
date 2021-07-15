# Add date 
update spectralFiles set date= substr(path, instr(path, '2021'),4) || '-' || substr(path, instr(path, '2021')+4,2) || '-' || substr(path, instr(path, '2021')+6,2) || " " || substr(path, instr(path, '2021')+9,2) || ":" || substr(path, instr(path, '2021')+11,2) || ":" || substr(path, instr(path, '2021')+13,2) where path like '%/2021____-______-%';

# Add monkeyId
update spectralFiles set monkeyId='1511184' where path like '%bresil%';
update spectralFiles set monkeyId='1512692' where path like '%kenya%';
update spectralFiles set monkeyId='1508202' where path like '%1508202%';
update spectralFiles set monkeyId='1508202' where path like '%somalie%';

# Add target
update spectralFiles set target='onh' where path like '%onh%';
update spectralFiles set target='mac' where path like '%mac%';

# Add eye
update spectralFiles set eye='os' where path like '%-os-%';
update spectralFiles set eye='od' where path like '%-od-%';

