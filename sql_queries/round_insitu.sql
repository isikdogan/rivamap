create table insitu_rounded as
select round( CAST("lat" as numeric), 3) as latr, round( CAST("lon" as numeric), 3) as lonr, avg(insituwidth) as width
from insitu
group by latr, lonr