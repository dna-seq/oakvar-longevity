--- UPDATES UNCONVENTIONAL --
UPDATE variant SET identifier='rs1800796' WHERE (identifier='Rs1800796' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='IL6')); -- unconventional RS (uppercase)
UPDATE variant SET identifier='rs1799889' WHERE (identifier='1-bp guanine deletion/insertion (4G/5G)' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='SERPINE1')); -- https://www.snpedia.com/index.php/Rs1799889
UPDATE variant SET identifier='rs1800795' WHERE (identifier='-174C/G' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='IL6')); -- https://www.snpedia.com/index.php/Rs1800795 
UPDATE variant SET identifier='rs61733139' WHERE (identifier='Q95H' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='MTTP')); -- https://www.aginginterventionfoundation.org/GenomicsNotes.htm
UPDATE variant SET identifier='rs1800629' WHERE (identifier='-308G/A' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='TNF'));  -- https://www.dovepress.com/effect-of-tnf-alpha-minus308ga-rs1800629-promoter-polymorphism-on-the--peer-reviewed-fulltext-article-CCID https://www.snpedia.com/index.php/Rs1800629
UPDATE variant SET identifier='rs1799752' WHERE (identifier='I/D' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='ACE')); -- https://pubmed.ncbi.nlm.nih.gov/11091119/ https://www.snpedia.com/index.php/Rs1799752 https://pubmed.ncbi.nlm.nih.gov/21330423/
UPDATE variant SET identifier='rs1801133' WHERE ((identifier='C677T' OR identifier='677C/T') AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='MTHFR'));  -- rs1801133, https://www.snpedia.com/index.php/MTHFR rs1801133, also known as C677T or A222V
UPDATE variant SET identifier='rs7412' WHERE (identifier='E2/E3/E4' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='APOE'));  -- rs7412,rs429358 https://www.snpedia.com/index.php/APOE  There are three relatively common allelic variants of ApoE, as defined by two SNPs, rs429358 and rs7412 known as ApoE-ε2, ApoE-ε3, and ApoE-ε4
UPDATE variant SET identifier='rs1800790' WHERE (identifier='-455G/A' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='FGB')); -- https://www.snpedia.com/index.php/Rs1800790 Also known as 455G/A beta Fibrinogen polymorphism. A is the risk allele according to the following paper: 
UPDATE variant SET identifier='rs2430561' WHERE (identifier='874T/A' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='IFNG')); -- 874T/A -> rs2430561 https://www.archivesofmedicalscience.com/IFN-874-A-T-rs2430561-gene-polymorphism-and-risk-of-pulmonary-tuberculosis-a-meta,78642,0,2.html https://www.snpedia.com/index.php/Rs2430561
UPDATE variant SET identifier='rs662' WHERE (identifier='Q192R' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='PON1')); -- Q192R -> Rs662, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC6074118/ A single nucleotide polymorphism (SNP) in the PON1 gene, Q192R (rs662) https://www.snpedia.com/index.php/Rs662
UPDATE variant SET identifier='rs1800896' WHERE (identifier='-1082G/A' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='IL10')); -- -1082G/A -> rs1800896, https://www.ncbi.nlm.nih.gov/pmc/articles/PMC5658633/ https://www.snpedia.com/index.php/Rs1800896 This SNP is upstream of the IL10 gene, and is also known as the -1082G>A IL10 SNP
UPDATE variant SET identifier='rs1008438' WHERE (identifier='-110A/C' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='HSPA1A')); -- ## -110A/C -> rs1008438, https://pubmed.ncbi.nlm.nih.gov/22328194/  https://www.snpedia.com/index.php/Rs1008438
UPDATE variant SET identifier='rs1799963' WHERE (identifier='20210G/A' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='F2')); -- ## 20210G/A -> Rs1799963 https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4465517/ https://www.snpedia.com/index.php/Rs1799963 rs1799963 is a SNP far more commonly known as the G20210A mutation of the prothrombin F2 gene. 23andMe's i3002432 is another name for rs1799963. 
UPDATE variant SET identifier='rs2069762' WHERE (identifier='-330T/G' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='IL2')); -- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC4514317/

--- UPDATES TYPOS IN DB --
-- MTHFR A/V114 -> ??????? https://pubmed.ncbi.nlm.nih.gov/11602206/ https://pubmed.ncbi.nlm.nih.gov/10494771/ 
-- DOI: 10.1055/s-0037-1614336 unavailable, http://www.ensembl.org/Homo_sapiens/Gene/Variation_Gene/Table?db=core;g=ENSG00000177000;r=1:11785723-11806455
-- havent heard of such, no more mentions elsewhere
--SERPINA1 TYPO in DB, correct in article https://pubmed.ncbi.nlm.nih.gov/17048073/

INSERT INTO gene(entrez_id,name,symbol,alias,description,omim,ensembl,uniprot,unigene,in_genage,cytogenetic_location)
	VALUES (5265,'serpin family A member 1','SERPINA1','PI A1A AAT PI1 A1AT nNIF PRO2275 alpha1AT', 
			'The protein encoded by this gene is a serine protease inhibitor belonging to the serpin superfamily whose targets include elastase, plasmin, thrombin, trypsin, chymotrypsin, and plasminogen activator. This protein is produced in the liver, the bone marrow, by lymphocytic and monocytic cells in lymphoid tissue, and by the Paneth cells of the gut. Defects in this gene are associated with chronic obstructive pulmonary disease, emphysema, and chronic liver disease. Several transcript variants encoding the same protein have been found for this gene. [provided by RefSeq, Aug 2020].', 
			107400, 'ENSG00000197249', 'A1AT_HUMAN', 525557, 0, '14q32.13');		-- serpina1 gene info
UPDATE variant SET identifier='rs28940579',gene_id=(SELECT entrez_id FROM gene WHERE symbol='SERPINE1') WHERE (identifier='SERPINE1' AND gene_id=(SELECT entrez_id FROM gene WHERE symbol='SERPINE1')); -- https://www.snpedia.com/index.php/Rs28929474 

--- UPDATES TYPOS IN SOURCE --
UPDATE variant SET identifier='rs28940579' WHERE identifier='rs28940479'; -- rs28940479 does not exist! It is an error in article itself https://jlb.onlinelibrary.wiley.com/doi/full/10.1189/jlb.0705416 correct no is https://www.ncbi.nlm.nih.gov/snp/rs28940579 see https://www.ncbi.nlm.nih.gov/clinvar/variation/2540/
UPDATE variant SET identifier='rs3792683' WHERE identifier='rs37926683'; -- rs37926683 does not exist! It is an error in article itself https://academic.oup.com/biomedgerontology/article/62/2/202/574582 Typo, correct is https://www.ncbi.nlm.nih.gov/snp/rs3792683

--- UPDATES MERGES --
UPDATE variant SET identifier='rs2228570' WHERE identifier='rs10735810'; -- rs10735810 was merged into rs2228570 https://www.snpedia.com/index.php/Rs10735810 
UPDATE variant SET identifier='rs1126545' WHERE identifier='rs2281891'; -- rs2281891 was merged into rs1126545 on January 15, 2013 (Build 137) 
UPDATE variant SET identifier='rs1136201' WHERE identifier='rs1801200'; -- rs1801200 was merged into rs1136201 on May 25, 2008 (Build 130) https://www.ncbi.nlm.nih.gov/snp/rs1801200    
UPDATE variant SET identifier='rs1042028' WHERE identifier='rs4149396'; --  rs4149396 was merged into rs1042028 on January 27, 2015 (Build 131) https://www.ncbi.nlm.nih.gov/snp/rs4149396   
UPDATE variant SET identifier='rs2229738' WHERE identifier='rs17610395'; -- rs17610395 was merged into rs2229738 on May 24, 2008 (Build 130) https://www.ncbi.nlm.nih.gov/snp/rs17610395     
UPDATE variant SET identifier='rs3212227' WHERE identifier='rs17875322'; -- rs17875322 was merged into rs3212227 on March 11, 2006 (Build 126) https://www.ncbi.nlm.nih.gov/snp/rs17875322
UPDATE variant SET identifier='rs1800470' WHERE identifier='rs1982073'; -- rs1982073 was merged into rs1800470 on May 25, 2008 (Build 130) https://www.ncbi.nlm.nih.gov/snp/rs1982073
UPDATE variant SET identifier='rs1130409' WHERE identifier='rs3136820'; -- rs3136820 was merged into rs1130409 on March 10, 2006 (Build 126) https://www.ncbi.nlm.nih.gov/snp/rs3136820
UPDATE variant SET identifier='rs9344' WHERE identifier='rs603965'; -- rs603965 was merged into rs9344 on May 25, 2008 (Build 130) https://www.ncbi.nlm.nih.gov/snp/rs603965
UPDATE variant SET identifier='rs2228145' WHERE identifier='rs8192284'; -- rs8192284 was merged into rs2228145 on May 24, 2008 (Build 130) , https://www.ncbi.nlm.nih.gov/snp/rs8192284    
UPDATE variant SET identifier='rs1801318' WHERE identifier='rs4147719'; -- rs4147719 was merged into rs1801318 on May 25, 2008 (Build 130) , https://www.ncbi.nlm.nih.gov/snp/rs4147719
UPDATE variant SET identifier='rs1135640' WHERE identifier='rs1137582'; -- rs1137582 was merged into rs1135640 on May 25, 2008 (Build 130) , https://www.ncbi.nlm.nih.gov/snp/rs1137582     

--- REMOVALS UNSUPPORTED ---
UPDATE variant SET identifier=NULL WHERE (identifier='rs10498263'); -- Unsupported. This RefSNP no longer has any supporting observations. 
UPDATE variant SET identifier=NULL WHERE (identifier='rs3087784'); -- Unsupported. This RefSNP no longer has any supporting observations. https://www.ncbi.nlm.nih.gov/snp/rs3087784 

--- REMOVALS WITHDRAWN for PMID 22459618 (article "All 38 of the previously reported coding SNPs in FOXO3 are either invalid") --
SELECT * FROM variant WHERE (quickpubmed='22459618');
UPDATE variant SET identifier=NULL WHERE (identifier='rs138174682'); -- rs138174682 was withdrawn on September 3, 2011. 
UPDATE variant SET identifier=NULL WHERE (identifier='rs147010831'); -- rs147010831 was withdrawn on September 3, 2011. 
UPDATE variant SET identifier=NULL WHERE (identifier='rs148296241'); -- rs148296241 was withdrawn on September 3, 2011. 
UPDATE variant SET identifier=NULL WHERE (identifier='rs148405845'); -- rs148405845 was withdrawn on February 21, 2013. 
UPDATE variant SET identifier=NULL WHERE (identifier='rs149158541'); -- rs149158541 was withdrawn on September 3, 2011. 

--- SAINITY CHECKS ---
SELECT * FROM variant WHERE ( substr(identifier,1,2) <> 'rs' AND identifier LIKE 'rs%' ); -- 0 on output
SELECT * FROM variant WHERE ( substr(identifier,1,2) <> 'rs' ); -- 355 on output


