COPY
(SELECT   legs.from_stop_id, 
         legs.to_stop_id, 
         Count(*)                                                                                  AS count,
         Count(*) / (extract('epoch' FROM '2016-03-01'::timestamp - '2016-03-03'::timestamp)/3600) AS per_hour, 
         avg(arrival - departure)                                                                  AS avg_time,
         max(arrival - departure)                                                                  AS max_time,
         min(arrival - departure)                                                                  AS min_time,
         array_agg(DISTINCT(line))                                                                 AS lines
FROM     legs 
JOIN 
         ( SELECT   subleg.from_stop_id, 
                           subleg.to_stop_id, 
                           avg(subleg.arrival - subleg.departure)                              AS avgdev, 
                           stddev_pop(extract('epoch' FROM subleg.arrival - subleg.departure)) AS sdev 
                  FROM     legs AS subleg
                  GROUP BY subleg.from_stop_id, 
                           subleg.to_stop_id ) AS var 
ON       legs.from_stop_id = var.from_stop_id 
AND      legs.to_stop_id = var.to_stop_id 
WHERE    extract('epoch' FROM legs.arrival - legs.departure) > extract('epoch' FROM avgdev) - sdev
AND      extract('epoch' FROM legs.arrival - legs.departure) < extract('epoch' FROM avgdev) + sdev
GROUP BY legs.from_stop_id, 
         legs.to_stop_id
         ) TO stdout WITH csv header; 