SELECT * FROM astronomers
WHERE cic IS NOT Null
AND cic IS NOT ''
ORDER BY cic;