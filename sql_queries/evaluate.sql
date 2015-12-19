drop overlapping_results if exists;
create table overlapping_results as
SELECT narwidth_rounded.latr, narwidth_rounded.lonr, narwidth_rounded.width as width_ground_truth, cne_rounded.width as width_predicted
FROM narwidth_rounded
INNER JOIN cne_rounded ON narwidth_rounded.latr = cne_rounded.latr AND narwidth_rounded.lonr = cne_rounded.lonr
WHERE cne_rounded.psi > 0.01046635673;

SELECT
(SELECT corr(width_ground_truth, width_predicted) from overlapping_results) as corr_coef,
((SELECT COUNT(*) FROM overlapping_results)::float / (SELECT COUNT(*) FROM cne_rounded)) as prec,
((SELECT COUNT(*) FROM overlapping_results)::float / (SELECT COUNT(*) FROM narwidth_rounded)) as recal

