--CREATE table subset1
--AS
select *,
       COUNT(*) as cc,
	   MAX(p.year) as ymx,
	   SUM(CASE WHEN p.inar=1 then 1 else 0 END) as N_inar,
	   SUM(CASE WHEN p.inar=1 then 1 else 0 END) / (1.*COUNT(*)) as q
    FROM papers as p
	INNER JOIN people as g
    WHERE 
	    p.ID==g.ID
		AND
		g.edad BETWEEN 40 AND 85
		AND
		p.journal_Q==1
		AND
		p.author_count<51
	GROUP BY p.ID 
	HAVING 
	   ymx>2016
	   AND
	   q>0.85