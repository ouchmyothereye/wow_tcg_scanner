select * from card_versions 
where set_id = 46 and variant_id = 5
and card_id not in (select card_id from collection_inventory where variant_id = 5 and ignore = 0)
order by card_number
