/* Ver los registros que se incorporan entre los pasos 1 y 2
   es decir, en la funcion "S02_add_CIC_data" */

SELECT load2.*
FROM load2
    LEFT JOIN load1 ON (load1.apellido == load2.apellido)
	AND (load1.nombre == load2.nombre)
WHERE load1.nombre IS NULL

/* Devuelve la lista de todos los miembros de conicet que no estaban
   la tabla original. */