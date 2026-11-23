# DSAN 6300 - Homework 4 (Mini-Project)
# Zhiyang Cheng (zc385)
# Data: BTS Reporting Carrier On-Time Performance, January 2024 (547,271 flights)
# Schema: FAA   Fact table: al_perf   Dimension tables: L_AIRLINE_ID, L_AIRPORT, L_AIRPORT_ID,
#         L_CANCELATION, L_DISTANCE_GROUP_250, L_WEEKDAYS
#
# Data note used in several answers:
# mysqlimport loads blank numeric fields as 0, not NULL. Cancelled flights that never left
# the gate have a blank departure time and a blank delay, so after loading their DepDelay is 0.
# For departure-delay questions (1, 2, 4, 5) I keep only flights with a recorded departure
# time (DepTime <> ''), so those fake zeros do not pull the averages down.

USE FAA;


# Problem 1
# Find maximal departure delay in minutes for each airline. Sort results from smallest to
# largest maximum delay. Output airline names and values of the delay.
SELECT a.Name AS airline_name,
       MAX(p.DepDelay) AS max_departure_delay_minutes
FROM al_perf p
JOIN L_AIRLINE_ID a ON a.ID = p.DOT_ID_Reporting_Airline
WHERE p.DepTime <> ''
GROUP BY a.ID, a.Name
ORDER BY max_departure_delay_minutes ASC;

# rows returned: __Q1__


# Problem 2
# Find maximal early departures in minutes for each airline. Sort results from largest to
# smallest. Output airline names.
# (An early departure has a negative DepDelay; minutes early = -DepDelay.)
SELECT a.Name AS airline_name,
       -MIN(p.DepDelay) AS max_early_departure_minutes
FROM al_perf p
JOIN L_AIRLINE_ID a ON a.ID = p.DOT_ID_Reporting_Airline
WHERE p.DepTime <> ''
  AND p.DepDelay < 0
GROUP BY a.ID, a.Name
ORDER BY max_early_departure_minutes DESC;

# rows returned: __Q2__


# Problem 3
# Rank days of the week by the number of flights performed by all airlines on that day
# (1 is the busiest). Output the day of the week names, number of flights and ranks in the
# rank increasing order.
# (Every row in al_perf is one flight; BTS sets Flights = 1 for every row, cancelled ones included.)
SELECT w.Day AS day_of_week,
       COUNT(*) AS num_flights,
       RANK() OVER (ORDER BY COUNT(*) DESC) AS day_rank
FROM al_perf p
JOIN L_WEEKDAYS w ON w.Code = p.DayOfWeek
GROUP BY w.Code, w.Day
ORDER BY day_rank;

# rows returned: __Q3__


# Problem 4
# Find the airport that has the highest average departure delay among all airports.
# Consider 0 minutes delay for flights that departed early. Output one line of results:
# the airport name, code, and average delay.
SELECT ap.Name AS airport_name,
       p.Origin AS airport_code,
       ROUND(AVG(GREATEST(p.DepDelay, 0)), 2) AS avg_departure_delay_minutes
FROM al_perf p
JOIN L_AIRPORT ap ON ap.Code = p.Origin
WHERE p.DepTime <> ''
GROUP BY p.Origin, ap.Name
ORDER BY AVG(GREATEST(p.DepDelay, 0)) DESC
LIMIT 1;

# rows returned: __Q4__


# Problem 5
# For each airline find an airport where it has the highest average departure delay.
# Output an airline name, a name of the airport that has the highest average delay, and the
# value of that average delay.
# (Same delay rule as Problem 4: early departures count as 0 minutes.
#  RANK() keeps ties, so an airline would appear twice only if two airports tie exactly.)
WITH airline_airport AS (
    SELECT p.DOT_ID_Reporting_Airline AS airline_id,
           p.Origin AS airport_code,
           AVG(GREATEST(p.DepDelay, 0)) AS avg_delay
    FROM al_perf p
    WHERE p.DepTime <> ''
    GROUP BY p.DOT_ID_Reporting_Airline, p.Origin
),
ranked AS (
    SELECT airline_id, airport_code, avg_delay,
           RANK() OVER (PARTITION BY airline_id ORDER BY avg_delay DESC) AS rnk
    FROM airline_airport
)
SELECT a.Name AS airline_name,
       ap.Name AS airport_name,
       ROUND(r.avg_delay, 2) AS avg_departure_delay_minutes
FROM ranked r
JOIN L_AIRLINE_ID a ON a.ID = r.airline_id
JOIN L_AIRPORT ap ON ap.Code = r.airport_code
WHERE r.rnk = 1
ORDER BY r.avg_delay DESC;

# rows returned: __Q5__


# Problem 6a
# Check if your dataset has any canceled flights.
SELECT COUNT(*) AS total_flights,
       SUM(Cancelled = 1) AS cancelled_flights,
       ROUND(100 * SUM(Cancelled = 1) / COUNT(*), 2) AS pct_cancelled
FROM al_perf;

# rows returned: __Q6A__


# Problem 6b
# If it does, what was the most frequent reason for each departure airport? Output airport
# name, the most frequent reason, and the number of cancelations for that reason.
# (If two reasons tie for first place at an airport, both are listed.)
WITH airport_reason AS (
    SELECT p.Origin AS airport_code,
           p.CancellationCode,
           COUNT(*) AS num_cancellations
    FROM al_perf p
    WHERE p.Cancelled = 1
    GROUP BY p.Origin, p.CancellationCode
),
ranked AS (
    SELECT airport_code, CancellationCode, num_cancellations,
           RANK() OVER (PARTITION BY airport_code ORDER BY num_cancellations DESC) AS rnk
    FROM airport_reason
)
SELECT ap.Name AS airport_name,
       c.Reason AS most_frequent_reason,
       r.num_cancellations
FROM ranked r
JOIN L_AIRPORT ap ON ap.Code = r.airport_code
JOIN L_CANCELATION c ON c.Code = r.CancellationCode
WHERE r.rnk = 1
ORDER BY r.num_cancellations DESC, airport_name, most_frequent_reason;

# rows returned: __Q6B__


# Problem 7
# Build a report that for each day output average number of flights considering the current
# and the previous two days.
# (3-day moving average. Jan 1 and Jan 2 have no earlier days in this dataset, so their
#  averages use the 1 or 2 days that exist.)
WITH daily AS (
    SELECT FlightDate, COUNT(*) AS num_flights
    FROM al_perf
    GROUP BY FlightDate
)
SELECT FlightDate AS flight_date,
       num_flights,
       ROUND(AVG(num_flights) OVER (ORDER BY FlightDate
                                    ROWS BETWEEN 2 PRECEDING AND CURRENT ROW), 2) AS avg_flights_3day
FROM daily
ORDER BY FlightDate;

# rows returned: __Q7__
