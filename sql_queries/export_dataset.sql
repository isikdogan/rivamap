SELECT lat, lon, 
	round( CAST((2/(1+exp(-8*psi))-1) * width + 25 as numeric), 1) as width, 
	round( CAST("psi" as numeric), 3) as psi, 
	round( CAST("channel_orientation" as numeric), 2) channel_orientation
FROM public.cne;

