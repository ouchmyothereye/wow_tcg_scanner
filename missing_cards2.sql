with missing_cards as (select card_name, cast(card_number as INTEGER) as card_number, set_name, r.name from wow_cards wc
join sets c on c.set_id = wc.set_id
join rarities r on r.rarity_id = wc.rarity_id
where set_name like '%dark portal%'
and card_id not in (select card_id from collection_inventory where variant_id = 5 and ignore = 0)
order by card_number)
SELECT count(card_name) as 'no. missing', name
from missing_cards
group by name
