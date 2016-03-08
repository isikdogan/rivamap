-- ALTER TABLE insitu ADD COLUMN geog geography(Point,4326);
-- UPDATE insitu SET geog = ST_MakePoint(lon, lat);

-- ALTER TABLE cne ADD COLUMN geog geography(Point,4326);
-- UPDATE cne SET geog = ST_MakePoint(lon, lat);

-- ALTER TABLE narwidth ADD COLUMN geog geography(Point,4326);
-- UPDATE narwidth SET geog = ST_MakePoint(lon, lat);

SELECT DISTINCT C.* FROM
(
	SELECT insitu.lat, insitu.lon, insitu.insituwidth, insitu.landsat_width, cne.width as cne_width,
		ABS(cne.width - insitu.insituwidth) as absdiff,
		MIN(ABS(cne.width - insitu.insituwidth)) OVER (PARTITION BY insitu.lat, insitu.lon) as minabsdiff
	FROM insitu INNER JOIN cne
	ON ST_DWithin(insitu.geog, cne.geog, insitu.insituwidth)
) as C
WHERE absdiff = minabsdiff;