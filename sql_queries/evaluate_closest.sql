-- ALTER TABLE insitu ADD COLUMN geog geography(Point,4326);
-- UPDATE insitu SET geog = ST_MakePoint(lon, lat);

-- ALTER TABLE cne ADD COLUMN geog geography(Point,4326);
-- UPDATE cne SET geog = ST_MakePoint(lon, lat);

-- ALTER TABLE cne_no_overlap ADD COLUMN geog geography(Point,4326);
-- UPDATE cne_no_overlap SET geog = ST_MakePoint(lon, lat);
-- CREATE INDEX cne_no_overlap_index ON cne_no_overlap USING GIST ( geog );

-- ALTER TABLE narwidth ADD COLUMN geog geography(Point,4326);
-- UPDATE narwidth SET geog = ST_MakePoint(lon, lat);

drop table if exists overlapping_results;
create table overlapping_results as
SELECT C.lat, C.lon, C.gt_width, AVG(C.cne_width) as cne_width, 
    AVG(C.psi) as psi, AVG(C.new_width) as new_width FROM
(
    SELECT narwidth.lat, narwidth.lon, narwidth.width as gt_width, cne.width as cne_width,
       cne.psi, (2/(1+exp(-8*cne.psi))-1)*cne.width*60+30 as new_width
    FROM narwidth INNER JOIN cne
    ON ST_DWithin(narwidth.geog, cne.geog, narwidth.width)
    WHERE narwidth.width < 2000
) as C
GROUP BY C.lat, C.lon, C.gt_width;