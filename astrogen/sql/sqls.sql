-- VER LAS DIFERENCIAS ENTRE DOS TABLAS --
-- ../sql/diferences.sq 

/* Ver los registros que se incorporan entre los pasos 1 y 2
   es decir, en la funcion "S02_add_CIC_data" */

SELECT load2.*
FROM load2
    LEFT JOIN load1 ON (load1.apellido == load2.apellido)
        AND (load1.nombre == load2.nombre)
WHERE load1.nombre IS NULL

/* Devuelve la lista de todos los miembros de conicet que no estaban
   la tabla original. */




-- VER LA LISTA DE PERSONAL DE CONICET --
-- ../sql/query_cic2.sql

SELECT * FROM astronomers
WHERE cic IS NOT Null
  AND cic IS NOT ''
ORDER BY cic;


-- CONTAR LA CANTIDAD DE PERSONAS EN CONICET --
-- ../sql/query_cic.sql

SELECT * FROM astronomers
WHERE cic !=""
ORDER BY cic
COUNT;


-- VER LA LISTA DE INVESTIGADORES ADJUNTOS --
-- ../sql/query_count.sql

SELECT COUNT(nombre)
FROM astronomers
WHERE cic="Adjunto";




SELECT * FROM people
WHERE 
    edad BETWEEN 25 AND 80
    AND
	filter_authors==1



   
select 
	bibcode,
	ID,
	COUNT(*) as cc
FROM papers
group by ID
HAVING cc>200




--create TABLE pp
--AS
select *,
       COUNT(*) as cc,
	   MAX(p.year) as ymx
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
		AND
		p.inar==1
	GROUP BY p.ID
