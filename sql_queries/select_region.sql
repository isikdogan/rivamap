SELECT cne.*
FROM cne,
  (select ST_MakePoint(-90.15,29.53)::geography as poi) as poi
WHERE ST_DWithin(geog, poi, 200000)
ORDER BY ST_Distance(geog, poi);