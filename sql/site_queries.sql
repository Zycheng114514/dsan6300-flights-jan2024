-- Extra queries behind the website's charts (not part of the graded answers).
-- Each block starts with "-- @name <file>" and is exported to website/data/<file>.csv
-- by scripts/build_site_data.py. Same delay rule as the homework: departure-delay stats
-- use only flights with a recorded departure time (DepTime <> ''), early = 0 minutes.

-- @name daily
-- One row per day: volume, cancellations by reason, delay level.
SELECT p.FlightDate AS flight_date,
       w.Day AS day_of_week,
       COUNT(*) AS flights,
       SUM(p.Cancelled = 1) AS cancelled,
       SUM(p.Cancelled = 1 AND p.CancellationCode = 'A') AS cancel_carrier,
       SUM(p.Cancelled = 1 AND p.CancellationCode = 'B') AS cancel_weather,
       SUM(p.Cancelled = 1 AND p.CancellationCode = 'C') AS cancel_nas,
       SUM(p.Cancelled = 1 AND p.CancellationCode = 'D') AS cancel_security,
       ROUND(AVG(CASE WHEN p.DepTime <> '' THEN GREATEST(p.DepDelay, 0) END), 2) AS avg_dep_delay,
       ROUND(100 * AVG(CASE WHEN p.DepTime <> '' THEN p.DepDel15 END), 2) AS pct_dep_delayed_15
FROM al_perf p
JOIN L_WEEKDAYS w ON w.Code = p.DayOfWeek
GROUP BY p.FlightDate, w.Day
ORDER BY p.FlightDate;

-- @name daily_carrier_cancel
-- Carrier-caused cancellations per day: Alaska, United, everyone else.
SELECT FlightDate AS flight_date,
       SUM(Reporting_Airline = 'AS') AS alaska,
       SUM(Reporting_Airline = 'UA') AS united,
       SUM(Reporting_Airline NOT IN ('AS', 'UA')) AS all_other_airlines
FROM al_perf
WHERE Cancelled = 1 AND CancellationCode = 'A'
GROUP BY FlightDate
ORDER BY FlightDate;

-- @name airline_scorecard
SELECT p.Reporting_Airline AS code,
       a.Name AS airline_name,
       COUNT(*) AS flights,
       SUM(p.Cancelled = 1) AS cancelled,
       ROUND(100 * AVG(p.Cancelled = 1), 2) AS pct_cancelled,
       SUM(p.Cancelled = 1 AND p.CancellationCode = 'A') AS cancel_carrier,
       SUM(p.Cancelled = 1 AND p.CancellationCode = 'B') AS cancel_weather,
       SUM(p.Cancelled = 1 AND p.CancellationCode = 'C') AS cancel_nas,
       ROUND(AVG(CASE WHEN p.DepTime <> '' THEN GREATEST(p.DepDelay, 0) END), 2) AS avg_dep_delay,
       ROUND(100 * AVG(CASE WHEN p.DepTime <> '' THEN p.DepDel15 END), 2) AS pct_dep_delayed_15,
       ROUND(100 * AVG(CASE WHEN p.DepTime <> '' THEN p.DepDelay < 0 END), 2) AS pct_departed_early,
       MAX(CASE WHEN p.DepTime <> '' THEN p.DepDelay END) AS max_dep_delay,
       -MIN(CASE WHEN p.DepTime <> '' THEN p.DepDelay END) AS max_early_departure,
       SUM(p.DepTime <> '' AND p.DepDelay >= 180) AS delays_3h_plus
FROM al_perf p
JOIN L_AIRLINE_ID a ON a.ID = p.DOT_ID_Reporting_Airline
GROUP BY p.Reporting_Airline, a.Name
ORDER BY flights DESC;

-- @name airports
SELECT p.Origin AS code,
       ap.Name AS airport_name,
       COUNT(*) AS flights,
       SUM(p.DepTime <> '') AS departed,
       SUM(p.Cancelled = 1) AS cancelled,
       ROUND(100 * AVG(p.Cancelled = 1), 2) AS pct_cancelled,
       ROUND(AVG(CASE WHEN p.DepTime <> '' THEN GREATEST(p.DepDelay, 0) END), 2) AS avg_dep_delay,
       ROUND(100 * AVG(CASE WHEN p.DepTime <> '' THEN p.DepDel15 END), 2) AS pct_dep_delayed_15
FROM al_perf p
JOIN L_AIRPORT ap ON ap.Code = p.Origin
GROUP BY p.Origin, ap.Name
ORDER BY flights DESC;

-- @name airline_airport_worst
-- Problem 5 again, with the number of departures behind each average.
WITH airline_airport AS (
    SELECT p.DOT_ID_Reporting_Airline AS airline_id, p.Reporting_Airline AS airline_code,
           p.Origin AS airport_code,
           COUNT(*) AS departures,
           AVG(GREATEST(p.DepDelay, 0)) AS avg_delay
    FROM al_perf p
    WHERE p.DepTime <> ''
    GROUP BY p.DOT_ID_Reporting_Airline, p.Reporting_Airline, p.Origin
),
ranked AS (
    SELECT *, RANK() OVER (PARTITION BY airline_id ORDER BY avg_delay DESC) AS rnk
    FROM airline_airport
)
SELECT r.airline_code, a.Name AS airline_name, r.airport_code, ap.Name AS airport_name,
       r.departures, ROUND(r.avg_delay, 2) AS avg_dep_delay
FROM ranked r
JOIN L_AIRLINE_ID a ON a.ID = r.airline_id
JOIN L_AIRPORT ap ON ap.Code = r.airport_code
WHERE r.rnk = 1
ORDER BY r.avg_delay DESC;

-- @name weekday
SELECT w.Code AS day_code,
       w.Day AS day_of_week,
       COUNT(DISTINCT p.FlightDate) AS days_in_month,
       COUNT(*) AS flights,
       ROUND(COUNT(*) / COUNT(DISTINCT p.FlightDate), 0) AS flights_per_day,
       SUM(p.Cancelled = 1) AS cancelled
FROM al_perf p
JOIN L_WEEKDAYS w ON w.Code = p.DayOfWeek
GROUP BY w.Code, w.Day
ORDER BY w.Code;

-- @name time_of_day
-- Delays build up over the day (scheduled departure hour block).
SELECT DepTimeBlk AS dep_time_block,
       COUNT(*) AS flights,
       ROUND(AVG(CASE WHEN DepTime <> '' THEN GREATEST(DepDelay, 0) END), 2) AS avg_dep_delay,
       ROUND(100 * AVG(CASE WHEN DepTime <> '' THEN DepDel15 END), 2) AS pct_dep_delayed_15
FROM al_perf
GROUP BY DepTimeBlk
ORDER BY DepTimeBlk;

-- @name cancel_reason_airports
-- Cancellations by reason at the 15 airports with the most cancellations.
WITH top_airports AS (
    SELECT Origin, COUNT(*) AS total
    FROM al_perf
    WHERE Cancelled = 1
    GROUP BY Origin
    ORDER BY total DESC
    LIMIT 15
)
SELECT t.Origin AS code, ap.Name AS airport_name, t.total,
       SUM(p.CancellationCode = 'A') AS carrier,
       SUM(p.CancellationCode = 'B') AS weather,
       SUM(p.CancellationCode = 'C') AS nas
FROM top_airports t
JOIN al_perf p ON p.Origin = t.Origin AND p.Cancelled = 1
JOIN L_AIRPORT ap ON ap.Code = t.Origin
GROUP BY t.Origin, ap.Name, t.total
ORDER BY t.total DESC;
