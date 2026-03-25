-- DDL for Materialized View (or Table if complex functions are used)
-- Create a gold table for analytical querying
-- Pre-calculates frequencies and assigns a score 1-5

CREATE OR REPLACE TABLE `joi-jinko.gold.skills_scoring`
PARTITION BY DATE(processed_timestamp)
CLUSTER BY seniority_level, skill_name
AS
WITH skill_counts AS (
    SELECT 
        skill_name,
        seniority_level,
        COUNT(*) as frequency,
        MAX(processed_timestamp) as processed_timestamp
    FROM `joi-jinko.silver.normalized_skills`
    GROUP BY skill_name, seniority_level
),
max_freq AS (
    SELECT 
        seniority_level, 
        MAX(frequency) as max_f
    FROM skill_counts
    GROUP BY seniority_level
)
SELECT 
    s.skill_name,
    s.seniority_level,
    s.frequency,
    -- Scale 1 to 5 based on max frequency in that seniority
    CAST(ROUND((s.frequency / m.max_f) * 4) + 1 AS INT64) as demand_score_1_to_5,
    CONCAT('https://www.google.com/search?q=curriculum+course+java+', REPLACE(s.skill_name, ' ', '+')) as learning_url,
    s.processed_timestamp
FROM skill_counts s
JOIN max_freq m ON s.seniority_level = m.seniority_level;
