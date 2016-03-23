-- ALTER TABLE insitu ADD COLUMN geog geography(Point,4326);
-- UPDATE insitu SET geog = ST_MakePoint(lon, lat);

-- ALTER TABLE cne ADD COLUMN geog geography(Point,4326);
-- UPDATE cne SET geog = ST_MakePoint(lon, lat);

-- ALTER TABLE cne_no_overlap ADD COLUMN geog geography(Point,4326);
-- UPDATE cne_no_overlap SET geog = ST_MakePoint(lon, lat);
-- CREATE INDEX cne_no_overlap_index ON cne_no_overlap USING GIST ( geog );

-- ALTER TABLE narwidth ADD COLUMN geog geography(Point,4326);
-- UPDATE narwidth SET geog = ST_MakePoint(lon, lat);

-- 
-- SELECT C.lat, C.lon, C.gt_width, C.landsat_width as narwidth_width, AVG(C.cne_width) as cne_width FROM
-- (
-- 	SELECT insitu.lat, insitu.lon, insitu.landsat_width,
-- 		insitu.insituwidth as gt_width, cne.width as cne_width, 
-- 		ST_Distance(insitu.geog, cne.geog) as cne_dist,
-- 		--MIN(ST_Distance(insitu.geog, cne.geog)) OVER (PARTITION BY insitu.lat, insitu.lon) as min_cne_dist
-- 		ABS(cne.width - insitu.insituwidth) as absdiff,
-- 		MIN(ABS(cne.width - insitu.insituwidth)) OVER (PARTITION BY insitu.lat, insitu.lon) as minabsdiff
-- 	FROM insitu INNER JOIN cne
-- 	ON ST_DWithin(insitu.geog, cne.geog, 1000)
-- ) as C
-- --WHERE cne_dist = min_cne_dist
-- WHERE absdiff < minabsdiff*3
-- GROUP BY C.lat, C.lon, C.gt_width, C.landsat_width;

-- -- -- ---
-- -- -- SELECT insitu.lat, insitu.lon, insitu.landsat_width as narwidth_width,
-- -- -- 	insitu.insituwidth as gt_width, avg(cne.width) * 48 as cne_width
-- -- -- FROM insitu INNER JOIN cne
-- -- -- ON ST_DWithin(insitu.geog, cne.geog, 1.5*insitu.insituwidth)
-- -- -- GROUP BY insitu.lat, insitu.lon, insitu.landsat_width, insitu.insituwidth;
-- -- -- ---

-- -- -- drop table if exists overlapping_results;
-- -- -- create table overlapping_results as
-- -- -- SELECT C.lat, C.lon, C.gt_width, AVG(C.cne_width) as cne_width FROM
-- -- -- (
-- -- -- 	SELECT narwidth.lat, narwidth.lon, narwidth.width as gt_width, cne.width as cne_width, 
-- -- -- 		ST_Distance(narwidth.geog, cne.geog) as cne_dist,
-- -- -- 		--MIN(ST_Distance(narwidth.geog, cne.geog)) OVER (PARTITION BY narwidth.lat, narwidth.lon) as min_cne_dist
-- -- -- 		ABS(cne.width * 48 - narwidth.width) as absdiff,
-- -- -- 		MIN(ABS(cne.width * 48 - narwidth.width)) OVER (PARTITION BY narwidth.lat, narwidth.lon) as minabsdiff
-- -- -- 	FROM narwidth INNER JOIN cne
-- -- -- 	ON ST_DWithin(narwidth.geog, cne.geog, cne.width * 48 + narwidth.width)
-- -- -- 	WHERE narwidth.width < 2000
-- -- -- ) as C
-- -- -- --WHERE cne_dist = min_cne_dist
-- -- -- WHERE absdiff < minabsdiff*3
-- -- -- GROUP BY C.lat, C.lon, C.gt_width;


drop table if exists overlapping_results;
create table overlapping_results as
SELECT C.lat, C.lon, C.gt_width, AVG(C.cne_width) as cne_width FROM
(
    SELECT narwidth.lat, narwidth.lon, narwidth.width as gt_width, cne.width as cne_width, 
        ST_Distance(narwidth.geog, cne.geog) as cne_dist,
        ABS(cne.width - narwidth.width) as absdiff,
        MIN(ABS(cne.width - narwidth.width)) OVER (PARTITION BY narwidth.lat, narwidth.lon) as minabsdiff
    FROM narwidth INNER JOIN cne
    ON ST_DWithin(narwidth.geog, cne.geog, narwidth.width)
    WHERE narwidth.width < 2000
) as C
WHERE absdiff < minabsdiff*2
GROUP BY C.lat, C.lon, C.gt_width;