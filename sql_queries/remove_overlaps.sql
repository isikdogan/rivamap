drop table if exists cne_no_overlap;
create table cne_no_overlap as
select round( CAST("lat" as numeric), 4) as latr, 
	round( CAST("lon" as numeric), 4) as lonr,
	avg(width) as width  --, avg(psi) as psi
from cne
group by latr, lonr

--create geog and index on it