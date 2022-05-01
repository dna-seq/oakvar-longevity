--- INPUT COUNTS ---
SELECT * FROM variant WHERE ( substr(identifier,1,2) <> 'rs' ); -- 452 on input
SELECT * FROM variant WHERE ( substr(identifier,1,2) <> 'rs' AND identifier LIKE 'rs%' ); -- 1

--- VALIDITY CHECKS ---
SELECT * FROM variant WHERE (identifier='1-bp guanine deletion/insertion (4G/5G)' AND gene_id=(SELECT id FROM gene WHERE symbol='SERPINE1')); -- 6
SELECT * FROM variant WHERE (identifier='-174C/G' AND gene_id=(SELECT id FROM gene WHERE symbol='IL6'));  -- 9 
SELECT * FROM variant WHERE (identifier='-174C/G' AND gene_id=(SELECT id FROM gene WHERE symbol='IL6'));  -- 2
SELECT * FROM variant WHERE (identifier='-308G/A' AND gene_id=(SELECT id FROM gene WHERE symbol='TNF'));  --8
SELECT * FROM variant WHERE (identifier='I/D' AND gene_id=(SELECT id FROM gene WHERE symbol='ACE'));  --21
SELECT * FROM variant WHERE ((identifier='C677T' OR identifier='677C/T') AND gene_id=(SELECT id FROM gene WHERE symbol='MTHFR'));  --5
SELECT * FROM variant WHERE (identifier='E2/E3/E4' AND gene_id=(SELECT id FROM gene WHERE symbol='APOE'));  --18
SELECT * FROM variant WHERE (identifier='-455G/A' AND gene_id=(SELECT id FROM gene WHERE symbol='FGB'));  --4
SELECT * FROM variant WHERE (identifier='874T/A' AND gene_id=(SELECT id FROM gene WHERE symbol='IFNG'));  --4
SELECT * FROM variant WHERE (identifier='Q192R' AND gene_id=(SELECT id FROM gene WHERE symbol='PON1'));  --4
SELECT * FROM variant WHERE (identifier='-1082G/A' AND gene_id=(SELECT id FROM gene WHERE symbol='IL10'));  --6
SELECT * FROM variant WHERE (identifier='-110A/C' AND gene_id=(SELECT id FROM gene WHERE symbol='HSPA1A'));  --3
SELECT * FROM variant WHERE (identifier='20210G/A' AND gene_id=(SELECT id FROM gene WHERE symbol='F2'));  --3
SELECT * FROM variant WHERE (identifier='-330T/G' AND gene_id=(SELECT id FROM gene WHERE symbol='IL2'));  --2

--- OUTPUT COUNTS AFTER REMOVAL ---
SELECT * FROM variant WHERE ( substr(identifier,1,2) <> 'rs' AND identifier LIKE 'rs%' ); -- 0 on output
SELECT * FROM variant WHERE ( substr(identifier,1,2) <> 'rs' ); -- 355 on output