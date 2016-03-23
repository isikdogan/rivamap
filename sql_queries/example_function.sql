CREATE OR REPLACE FUNCTION somefuncname() RETURNS int LANGUAGE plpgsql AS $$
DECLARE
  counter int;
  ground_truth CURSOR FOR SELECT * FROM insitu;
BEGIN
counter := 0;

    FOR cur_row IN ground_truth LOOP
	

	SELECT cne.*
	FROM cne
	WHERE ST_DWithin(geog, cur_row.geog, 2*cur_row.insituwidth)
	ORDER BY ST_Distance(geog, cur_row.geog)
	LIMIT 1;

	counter := counter + 1;
	
	RAISE NOTICE 'counter %', counter;
	EXIT;
    END LOOP;

  RETURN counter;
END
$$;
SELECT somefuncname();

