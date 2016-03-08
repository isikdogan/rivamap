create table narwidth_rounded as
select round( CAST("lat" as numeric), 3) as latr, round( CAST("lon" as numeric), 3) as lonr, avg(width) as width
from narwidth where reservoir < 1
group by latr, lonr