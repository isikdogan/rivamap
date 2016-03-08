create table cne_rounded as
select round( CAST("lat" as numeric), 3) as latr, round( CAST("lon" as numeric), 3) as lonr, avg(width) as width  --, avg(psi) as psi
from cne
group by latr, lonr