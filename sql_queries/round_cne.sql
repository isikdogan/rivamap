create table cne_rounded as
select round( CAST("lat" as numeric), 2) as latr, round( CAST("lon" as numeric), 2) as lonr, avg(width) as width, avg(psi) as psi
from cne
group by latr, lonr