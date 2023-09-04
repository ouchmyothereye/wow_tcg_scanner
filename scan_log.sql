WITH RankedEntries AS (
    SELECT
        wc.card_name,
        s.set_name,
		scan_date,
        ROW_NUMBER() OVER (PARTITION BY ci.card_id ORDER BY ci.scan_date) - 1 AS number_of_entries
    FROM wow_cards wc
    JOIN collection_inventory ci ON wc.card_id = ci.card_id
    JOIN sets s ON wc.set_id = s.set_id
)
SELECT card_name, set_name, scan_date, number_of_entries
FROM RankedEntries
ORDER BY scan_date desc;
