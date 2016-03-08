drop table if exists overlapping_results;
create table overlapping_results as
SELECT insitu_rounded.latr, insitu_rounded.lonr, insitu_rounded.width as width_ground_truth, cne_rounded.width as width_predicted
FROM insitu_rounded
INNER JOIN cne_rounded ON insitu_rounded.latr = cne_rounded.latr AND insitu_rounded.lonr = cne_rounded.lonr;
-- WHERE cne_rounded.psi > 0.1;

SELECT
(SELECT corr(width_ground_truth, width_predicted) from overlapping_results) as corr_coef,
((SELECT COUNT(*) FROM overlapping_results)::float / (SELECT COUNT(*) FROM cne_rounded)) as prec,
((SELECT COUNT(*) FROM overlapping_results)::float / (SELECT COUNT(*) FROM insitu_rounded)) as recal

