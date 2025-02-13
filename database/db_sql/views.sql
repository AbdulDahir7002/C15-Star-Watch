CREATE VIEW meteor_data 
AS 
SELECT m.*, c.city_name
FROM meteor_shower AS m
JOIN meteor_shower_assignment AS msa
ON msa.meteor_shower_id = m.meteor_shower_id
JOIN stargazing_status AS ss
ON ss.stargazing_status_id = msa.stargazing_status_id
JOIN city AS c
ON c.city_id = ss.city_id;

CREATE VIEW aurora_data
AS 
SELECT a.*, c.city_id
FROM aurora_status AS a
JOIN country AS co
ON co.country_id = a.country_id
JOIN city AS c
ON c.country_id = co.country_id;
