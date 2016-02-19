drop table if exists overlapping_results;
create table overlapping_results as
SELECT cne_rounded.latr, cne_rounded.lonr, cne_rounded.psi, narwidth_rounded.width as width_ground_truth, cne_rounded.width as width_predicted
FROM narwidth_rounded
RIGHT OUTER JOIN cne_rounded ON narwidth_rounded.latr = cne_rounded.latr AND narwidth_rounded.lonr = cne_rounded.lonr;


